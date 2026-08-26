"""
evaluate.py
===========
BLEU and chrF evaluation for trained LoRA adaptors.

Loads the test split for a given pair, runs inference, and computes
sacrebleu metrics (BLEU, chrF, chrF++).

Results are saved to:  results/<pair_id>_<direction>_eval.json

Usage:
    python evaluate.py --pair ht
    python evaluate.py --pair eh --direction eng_hoc
    python evaluate.py --all              # evaluate all pairs, all directions
    python evaluate.py --pair ht --max_samples 100   # quick smoke test
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import sacrebleu

from config import PAIR_CONFIGS, RESULTS_DIR, LANG_NAMES
from dataset_utils import load_jsonl, build_samples, direction_to_lang_codes
from translate import Translator


# ---------------------------------------------------------------------------
# Evaluation core
# ---------------------------------------------------------------------------

def evaluate_direction(
    pair_id: str,
    direction: str,
    max_samples: Optional[int] = None,
    num_beams: int = 4,
    batch_size: int = 16,
    split: str = "test",
) -> Dict:
    """
    Evaluate one direction of one language pair.

    Returns a dict with BLEU, chrF, chrF++ scores and sample count.
    """
    cfg = PAIR_CONFIGS[pair_id]
    test_path = os.path.join(cfg["data_dir"], f"{split}.jsonl")

    if not os.path.exists(test_path):
        print(f"  [WARN] {test_path} not found, skipping.")
        return {}

    # Load test samples for this specific direction only
    rows = load_jsonl(test_path)
    samples = build_samples(
        rows,
        cfg["direction_a"],
        cfg["direction_b"],
        both_directions=False,
        direction_sample_prob=1.0 if direction == cfg["direction_a"] else 0.0,
    )

    # Filter to only the requested direction
    samples = [s for s in samples if s["direction"] == direction]

    if not samples:
        print(f"  [WARN] No samples found for direction '{direction}' in {test_path}")
        return {}

    if max_samples and len(samples) > max_samples:
        samples = samples[:max_samples]

    src_code, tgt_code = direction_to_lang_codes(direction)
    src_name = LANG_NAMES.get(src_code, src_code)
    tgt_name = LANG_NAMES.get(tgt_code, tgt_code)

    print(f"\n  Evaluating [{pair_id}] {src_name} -> {tgt_name}  ({len(samples)} samples)")

    # Extract sources and references
    # The "input" field contains the full prompt; we extract just the sentence
    sources    = [s["input"].split("\n")[1].strip() for s in samples]   # line 2 = the actual sentence
    references = [s["target"] for s in samples]

    # Run inference
    translator = Translator.get(pair_id)
    start = time.time()

    hypotheses = translator.translate(
        sources,
        direction,
        num_beams=num_beams,
        batch_size=batch_size,
    )

    elapsed = time.time() - start
    speed   = len(samples) / elapsed if elapsed > 0 else 0

    # Compute metrics
    bleu_score = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf_score = sacrebleu.corpus_chrf(hypotheses, [references])
    chrfpp     = sacrebleu.corpus_chrf(hypotheses, [references], word_order=2)

    result = {
        "pair":       pair_id,
        "direction":  direction,
        "src_lang":   src_name,
        "tgt_lang":   tgt_name,
        "split":      split,
        "num_samples": len(samples),
        "bleu":       round(bleu_score.score, 2),
        "chrf":       round(chrf_score.score, 2),
        "chrfpp":     round(chrfpp.score, 2),
        "bleu_details": {
            "bp":        round(bleu_score.bp, 4),
            "precisions": [round(p, 2) for p in bleu_score.precisions],
        },
        "speed_sentences_per_sec": round(speed, 1),
        "elapsed_sec": round(elapsed, 1),
    }

    # Print summary
    print(f"    BLEU  : {result['bleu']:.2f}")
    print(f"    chrF  : {result['chrf']:.2f}")
    print(f"    chrF++: {result['chrfpp']:.2f}")
    print(f"    Speed : {result['speed_sentences_per_sec']} sent/s")

    # Print a few examples
    print(f"\n    Examples (first 3):")
    for i in range(min(3, len(samples))):
        print(f"      Source : {sources[i][:80]}")
        print(f"      Ref    : {references[i][:80]}")
        print(f"      Hyp    : {hypotheses[i][:80]}")
        print()

    return result


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def save_result(result: Dict, pair_id: str, direction: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"{pair_id}_{direction}_eval.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"    Saved -> {os.path.relpath(out_path)}")


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(all_results: List[Dict]):
    print("\n" + "=" * 70)
    print(f"  {'Pair':<5} {'Direction':<12} {'Src':>10} {'Tgt':>10} {'BLEU':>6} {'chrF':>6} {'chrF++':>7}")
    print("-" * 70)
    for r in all_results:
        if not r:
            continue
        print(
            f"  {r['pair']:<5} {r['direction']:<12} "
            f"{r['src_lang']:>10} {r['tgt_lang']:>10} "
            f"{r['bleu']:>6.2f} {r['chrf']:>6.2f} {r['chrfpp']:>7.2f}"
        )
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate trained LoRA adaptors")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pair",  choices=list(PAIR_CONFIGS.keys()),
                       help="Evaluate a specific language pair")
    group.add_argument("--all",   action="store_true",
                       help="Evaluate all pairs and all directions")

    parser.add_argument("--direction", default=None,
                        help="Specific direction (e.g. hin_unr). Default: both directions")
    parser.add_argument("--split",      default="test",
                        choices=["train", "val", "test"],
                        help="Dataset split to evaluate on (default: test)")
    parser.add_argument("--max_samples", type=int, default=None,
                        help="Max samples per direction (for quick tests)")
    parser.add_argument("--num_beams",   type=int, default=4,
                        help="Beam search width")
    parser.add_argument("--batch_size",  type=int, default=16,
                        help="Inference batch size")
    parser.add_argument("--no_save",     action="store_true",
                        help="Don't save results to disk")
    return parser.parse_args()


def main():
    args = parse_args()

    pairs_to_eval: List[Tuple[str, str]] = []

    if args.all:
        for pair_id, cfg in PAIR_CONFIGS.items():
            pairs_to_eval.append((pair_id, cfg["direction_a"]))
            pairs_to_eval.append((pair_id, cfg["direction_b"]))
    else:
        pair_id = args.pair
        cfg     = PAIR_CONFIGS[pair_id]
        if args.direction:
            valid = {cfg["direction_a"], cfg["direction_b"]}
            if args.direction not in valid:
                print(f"ERROR: '{args.direction}' is not valid for pair '{pair_id}'")
                print(f"       Valid: {valid}")
                sys.exit(1)
            pairs_to_eval.append((pair_id, args.direction))
        else:
            pairs_to_eval.append((pair_id, cfg["direction_a"]))
            pairs_to_eval.append((pair_id, cfg["direction_b"]))

    print(f"\nEvaluating {len(pairs_to_eval)} direction(s)...")
    all_results = []

    for pair_id, direction in pairs_to_eval:
        result = evaluate_direction(
            pair_id=pair_id,
            direction=direction,
            max_samples=args.max_samples,
            num_beams=args.num_beams,
            batch_size=args.batch_size,
            split=args.split,
        )
        if result:
            all_results.append(result)
            if not args.no_save:
                save_result(result, pair_id, direction)

    print_summary(all_results)

    # Save combined results
    if all_results and not args.no_save:
        combined_path = os.path.join(RESULTS_DIR, "all_results.json")
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\nCombined results saved to: {os.path.relpath(combined_path)}")


if __name__ == "__main__":
    main()
