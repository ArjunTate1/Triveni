"""
translate.py
============
Single-pair inference using a trained LoRA adaptor.

Usage (CLI):
    python translate.py --pair ht --direction hin_unr --text "नमस्ते"
    python translate.py --pair he --direction hin_eng --text "आप कैसे हैं?"
    python translate.py --pair eh --direction eng_hoc --text "Where are you going?"

Python API (used by pipeline.py):
    from translate import Translator
    t = Translator("ht")
    print(t.translate("नमस्ते", "hin_unr"))
"""

import argparse
import os
import sys
from typing import List, Optional, Union

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from peft import PeftModel

from config import (
    BASE_MODEL,
    PAIR_CONFIGS,
    ADAPTORS_DIR,
    LANG_NAMES,
)
from dataset_utils import build_prompt, direction_to_lang_codes


# ---------------------------------------------------------------------------
# Translator class  (reusable across pipeline.py and evaluate.py)
# ---------------------------------------------------------------------------

class Translator:
    """
    Loads a base model + LoRA adaptor for one language pair and provides
    translation inference.

    Keeps the model in memory for repeated calls (lazy-loaded on first use).
    """

    _instances: dict = {}   # module-level cache: pair_id -> Translator

    def __init__(
        self,
        pair_id: str,
        base_model_name: Optional[str] = None,
        adaptor_dir: Optional[str] = None,
        device: Optional[str] = None,
    ):
        if pair_id not in PAIR_CONFIGS:
            raise ValueError(f"Unknown pair_id '{pair_id}'. Choose from: {list(PAIR_CONFIGS.keys())}")

        self.pair_id    = pair_id
        self.pair_cfg   = PAIR_CONFIGS[pair_id]
        self.base_model_name = base_model_name or BASE_MODEL
        self.adaptor_dir     = adaptor_dir     or self.pair_cfg["adaptor_dir"]
        self.device          = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self._model     = None
        self._tokenizer = None

    # ------------------------------------------------------------------
    # Lazy loading — model is loaded once on first translate() call
    # ------------------------------------------------------------------

    def _load(self):
        if self._model is not None:
            return   # already loaded

        adaptor_path = self.adaptor_dir
        has_adaptor  = os.path.isdir(adaptor_path) and os.path.exists(
            os.path.join(adaptor_path, "adapter_config.json")
        )

        print(f"  [Translator:{self.pair_id}] Loading tokenizer...", flush=True)
        # Prefer adaptor dir tokenizer (may have custom vocab), else use base
        tok_path = adaptor_path if has_adaptor else self.base_model_name
        self._tokenizer = AutoTokenizer.from_pretrained(tok_path)

        print(f"  [Translator:{self.pair_id}] Loading base model: {self.base_model_name}", flush=True)
        base = AutoModelForSeq2SeqLM.from_pretrained(self.base_model_name)

        if has_adaptor:
            print(f"  [Translator:{self.pair_id}] Loading LoRA adaptor: {adaptor_path}", flush=True)
            self._model = PeftModel.from_pretrained(base, adaptor_path)
            self._model = self._model.merge_and_unload()  # merge for faster inference
        else:
            print(
                f"  [Translator:{self.pair_id}] WARNING: No adaptor found at {adaptor_path}. "
                "Using base model only.",
                flush=True
            )
            self._model = base

        self._model = self._model.to(self.device)
        self._model.eval()

    # ------------------------------------------------------------------
    # Core translation
    # ------------------------------------------------------------------

    def translate(
        self,
        text: Union[str, List[str]],
        direction: str,
        num_beams: int = 4,
        max_length: int = 256,
        batch_size: int = 8,
    ) -> Union[str, List[str]]:
        """
        Translate a string (or list of strings) using the given direction key.

        Args:
            text:       Input sentence(s).
            direction:  e.g. "hin_unr" or "eng_hoc"
            num_beams:  Beam search width (4 is good; 1 = greedy)
            max_length: Max output tokens
            batch_size: Sentences per forward pass (for list input)

        Returns:
            Translated string, or list of strings if input was a list.
        """
        self._load()

        is_single = isinstance(text, str)
        texts = [text] if is_single else text

        src_code, tgt_code = direction_to_lang_codes(direction)
        prompts = [build_prompt(t, src_code, tgt_code) for t in texts]

        results = []
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i : i + batch_size]

            enc = self._tokenizer(
                batch_prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.pair_cfg.get("max_source_length", 128),
            ).to(self.device)

            with torch.no_grad():
                generated = self._model.generate(
                    **enc,
                    num_beams=num_beams,
                    max_length=max_length,
                    early_stopping=True,
                )

            decoded = self._tokenizer.batch_decode(generated, skip_special_tokens=True)
            results.extend(decoded)

        return results[0] if is_single else results

    # ------------------------------------------------------------------
    # Class-level cached factory  (used by pipeline.py for efficiency)
    # ------------------------------------------------------------------

    @classmethod
    def get(cls, pair_id: str, **kwargs) -> "Translator":
        """Return a cached Translator instance for the given pair."""
        if pair_id not in cls._instances:
            cls._instances[pair_id] = cls(pair_id, **kwargs)
        return cls._instances[pair_id]

    @classmethod
    def clear_cache(cls):
        """Unload all cached translators (free memory)."""
        cls._instances.clear()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Translate text using a trained LoRA adaptor")
    parser.add_argument("--pair",      required=True, choices=list(PAIR_CONFIGS.keys()),
                        help="Language pair: ht | eh | es | he")
    parser.add_argument("--direction", required=True,
                        help="Translation direction key, e.g. hin_unr")
    parser.add_argument("--text",      default=None,
                        help="Input text to translate (or use --file)")
    parser.add_argument("--file",      default=None,
                        help="Input file: one sentence per line")
    parser.add_argument("--output",    default=None,
                        help="Output file for translations (default: stdout)")
    parser.add_argument("--base_model",  default=None, help="Override base model")
    parser.add_argument("--adaptor_dir", default=None, help="Override adaptor directory")
    parser.add_argument("--num_beams", type=int, default=4,
                        help="Beam search width (default: 4)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate direction against pair config
    cfg = PAIR_CONFIGS[args.pair]
    valid_dirs = {cfg["direction_a"], cfg["direction_b"]}
    if args.direction not in valid_dirs:
        print(f"ERROR: direction '{args.direction}' is not valid for pair '{args.pair}'.")
        print(f"       Valid directions: {valid_dirs}")
        sys.exit(1)

    # Collect input texts
    if args.text:
        texts = [args.text]
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        print("ERROR: provide --text or --file")
        sys.exit(1)

    # Translate
    translator = Translator(
        args.pair,
        base_model_name=args.base_model,
        adaptor_dir=args.adaptor_dir,
    )

    src_code, tgt_code = direction_to_lang_codes(args.direction)
    src_name = LANG_NAMES.get(src_code, src_code)
    tgt_name = LANG_NAMES.get(tgt_code, tgt_code)
    print(f"\nTranslating {src_name} -> {tgt_name}  ({args.pair}/{args.direction})\n")

    translations = translator.translate(texts, args.direction, num_beams=args.num_beams)
    if isinstance(translations, str):
        translations = [translations]

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for t in translations:
                f.write(t + "\n")
        print(f"Saved {len(translations)} translation(s) to {args.output}")
    else:
        for src, tgt in zip(texts, translations):
            print(f"  IN : {src}")
            print(f"  OUT: {tgt}")
            print()


if __name__ == "__main__":
    main()
