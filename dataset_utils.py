"""
dataset_utils.py
================
JSONL dataset loader for the Triveni LoRA translation pipeline.

Each JSONL line has this schema:
    {
      "translation": {
        "<direction_a>": {"source": "...", "target": "..."},
        "<direction_b>": {"source": "...", "target": "..."}
      }
    }

The loader expands every line into TWO training samples (one per direction)
and wraps each in the prompt template defined in config.py.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple

from torch.utils.data import Dataset

from config import PAIR_CONFIGS, PROMPT_TEMPLATE, LANG_NAMES


# ---------------------------------------------------------------------------
# Low-level JSONL reader
# ---------------------------------------------------------------------------

def load_jsonl(path: str) -> List[dict]:
    """Read a .jsonl file and return a list of parsed dicts."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  [WARN] Skipping malformed line {lineno} in {path}: {e}")
    return rows


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(source: str, source_lang_code: str, target_lang_code: str) -> str:
    """
    Format a source sentence into the instruction prompt.

    Args:
        source:           The source sentence.
        source_lang_code: e.g. "hin", "eng"
        target_lang_code: e.g. "unr", "hoc"

    Returns:
        A ready-to-tokenise string ending with "Translation:"
    """
    src_name = LANG_NAMES.get(source_lang_code, source_lang_code)
    tgt_name = LANG_NAMES.get(target_lang_code, target_lang_code)
    return PROMPT_TEMPLATE.format(
        source_lang=src_name,
        target_lang=tgt_name,
        source=source,
    )


# ---------------------------------------------------------------------------
# Direction utilities
# ---------------------------------------------------------------------------

def direction_to_lang_codes(direction: str) -> Tuple[str, str]:
    """
    Parse a direction key (e.g. 'hin_unr') into (source_code, target_code).
    Handles 3-letter codes like 'hin', 'eng', 'hoc', 'sat', 'unr'.
    """
    parts = direction.split("_")
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(f"Cannot parse direction '{direction}'")


# ---------------------------------------------------------------------------
# Flat sample list builder
# ---------------------------------------------------------------------------

def build_samples(
    rows: List[dict],
    direction_a: str,
    direction_b: str,
    both_directions: bool = True,
    direction_sample_prob: float = 0.5,
) -> List[Dict[str, str]]:
    """
    Convert raw JSONL rows into a flat list of
    {"input": "<prompt>", "target": "<translation>"} dicts.

    Args:
        rows:                 Output of load_jsonl().
        direction_a:          e.g. "hin_unr"
        direction_b:          e.g. "unr_hin"
        both_directions:      If True, emit both directions per row.
                              If False, randomly sample one direction per row.
        direction_sample_prob: When both_directions=False, probability of
                              choosing direction_a (vs direction_b).
    """
    samples = []
    src_a, tgt_a = direction_to_lang_codes(direction_a)
    src_b, tgt_b = direction_to_lang_codes(direction_b)

    for row in rows:
        t = row.get("translation", {})
        pair_a = t.get(direction_a)
        pair_b = t.get(direction_b)

        if pair_a and pair_a.get("source") and pair_a.get("target"):
            if both_directions or random.random() < direction_sample_prob:
                samples.append({
                    "input":     build_prompt(pair_a["source"], src_a, tgt_a),
                    "target":    pair_a["target"],
                    "direction": direction_a,
                })

        if pair_b and pair_b.get("source") and pair_b.get("target"):
            if both_directions or random.random() >= direction_sample_prob:
                samples.append({
                    "input":     build_prompt(pair_b["source"], src_b, tgt_b),
                    "target":    pair_b["target"],
                    "direction": direction_b,
                })

    return samples


# ---------------------------------------------------------------------------
# HuggingFace-compatible Dataset
# ---------------------------------------------------------------------------

class TranslationDataset(Dataset):
    """
    PyTorch Dataset for seq2seq translation training.

    Returns tokenised (input_ids, attention_mask, labels) per item.
    """

    def __init__(
        self,
        samples: List[Dict[str, str]],
        tokenizer,
        max_source_length: int = 128,
        max_target_length: int = 128,
    ):
        self.samples           = samples
        self.tokenizer         = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict:
        sample = self.samples[idx]

        # Tokenise source (the instruction prompt)
        model_inputs = self.tokenizer(
            sample["input"],
            max_length=self.max_source_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Tokenise target
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(
                sample["target"],
                max_length=self.max_target_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )

        # Mask padding tokens in labels so they are ignored in loss
        label_ids = labels["input_ids"].squeeze()
        label_ids[label_ids == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids":      model_inputs["input_ids"].squeeze(),
            "attention_mask": model_inputs["attention_mask"].squeeze(),
            "labels":         label_ids,
        }


# ---------------------------------------------------------------------------
# Convenience loader used by train.py and evaluate.py
# ---------------------------------------------------------------------------

def load_pair_datasets(
    pair_id: str,
    tokenizer,
    splits: Optional[List[str]] = None,
    both_directions: bool = True,
) -> Dict[str, TranslationDataset]:
    """
    Load train / val / test splits for a given language pair.

    Args:
        pair_id:         One of "ht", "eh", "es", "he".
        tokenizer:       A HuggingFace tokeniser instance.
        splits:          Which splits to load. Default: ["train", "val", "test"]
        both_directions: Expand each row into both translation directions.

    Returns:
        Dict mapping split name -> TranslationDataset.
    """
    if splits is None:
        splits = ["train", "val", "test"]

    cfg = PAIR_CONFIGS[pair_id]
    datasets = {}

    for split in splits:
        path = os.path.join(cfg["data_dir"], f"{split}.jsonl")
        if not os.path.exists(path):
            print(f"  [WARN] {path} not found, skipping split '{split}'")
            continue

        rows = load_jsonl(path)
        samples = build_samples(
            rows,
            cfg["direction_a"],
            cfg["direction_b"],
            both_directions=both_directions,
        )
        print(f"  [{pair_id}] {split:5s}: {len(rows):>6,} rows -> {len(samples):>6,} samples")

        datasets[split] = TranslationDataset(
            samples,
            tokenizer,
            max_source_length=cfg["max_source_length"],
            max_target_length=cfg["max_target_length"],
        )

    return datasets


# ---------------------------------------------------------------------------
# Quick sanity check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    # Fix Windows console to handle Unicode (Devanagari, Ol Chiki, etc.)
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

    print("dataset_utils.py -- sanity check (no tokenizer needed)")

    for pair_id, cfg in PAIR_CONFIGS.items():
        train_path = os.path.join(cfg["data_dir"], "train.jsonl")
        if not os.path.exists(train_path):
            print(f"  [{pair_id}] train.jsonl not found, skipping")
            continue

        rows = load_jsonl(train_path)
        samples = build_samples(rows, cfg["direction_a"], cfg["direction_b"])
        print(f"\n[{pair_id}] {cfg['name']}")
        print(f"  Rows:    {len(rows):,}")
        print(f"  Samples: {len(samples):,}  (2x rows, both directions)")
        if samples:
            s = samples[0]
            # ascii-safe repr so Windows cp1252 console doesn't crash
            inp_safe = s['input'][:120].encode('ascii', 'replace').decode('ascii')
            tgt_safe = s['target'][:80].encode('ascii', 'replace').decode('ascii')
            print(f"  Example input  : {inp_safe!r}")
            print(f"  Example target : {tgt_safe!r}")
            print(f"  Direction      : {s['direction']}")
