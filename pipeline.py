"""
pipeline.py
===========
Full text-to-text translation pipeline for Triveni.

Supports all direct routes AND pivot routes:

  Direct:
    Hindi   <-> Mundari   (ht adaptor)
    English <-> Ho        (eh adaptor)
    English <-> Santali   (es adaptor)
    Hindi   <-> English   (he adaptor)

  Pivot (no direct data — chained through English):
    Hindi  -> Ho        :  Hindi -[he]-> English -[eh]-> Ho
    Ho     -> Hindi     :  Ho    -[eh]-> English -[he]-> Hindi
    Hindi  -> Santali   :  Hindi -[he]-> English -[es]-> Santali
    Santali -> Hindi    :  Santali -[es]-> English -[he]-> Hindi

Usage (CLI):
    python pipeline.py --src hin --tgt unr --text "नमस्ते"
    python pipeline.py --src hin --tgt hoc --text "आप कहाँ जा रहे हैं?"
    python pipeline.py --src hin --tgt sat --text "क्या आप ठीक हैं?"
    python pipeline.py --src hoc --tgt hin --text "Ape do okon renko?"
    python pipeline.py --src hin --tgt hoc --file input.txt --output output.txt

Python API:
    from pipeline import TranslationPipeline
    pipe = TranslationPipeline()
    result = pipe.translate("नमस्ते", "hin", "hoc")
    print(result)

    # Batch
    results = pipe.translate_batch(["नमस्ते", "आप कैसे हैं?"], "hin", "sat")
"""

import argparse
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Union

from config import PIVOT_ROUTES, LANG_NAMES, PAIR_CONFIGS
from translate import Translator


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------

class TranslationPipeline:
    """
    High-level translation interface.

    Accepts any supported (source_lang, target_lang) pair and resolves
    it via the PIVOT_ROUTES table — automatically chaining adaptors when
    a direct model doesn't exist.
    """

    def __init__(self, num_beams: int = 4, verbose: bool = True):
        self.num_beams = num_beams
        self.verbose   = verbose
        # Translators are loaded lazily inside Translator.get()
        # and cached for the lifetime of this pipeline instance.

    # ------------------------------------------------------------------
    # Route resolution
    # ------------------------------------------------------------------

    def _get_route(self, src: str, tgt: str) -> List[Tuple[str, str]]:
        """
        Return the list of (pair_id, direction) steps for this translation.
        Raises ValueError if the route is not registered.
        """
        route = PIVOT_ROUTES.get((src, tgt))
        if route is None:
            available = [
                f"{s} -> {t}" for s, t in PIVOT_ROUTES.keys()
            ]
            raise ValueError(
                f"No route found for '{src}' -> '{tgt}'.\n"
                f"Available routes:\n  " + "\n  ".join(available)
            )
        return route

    # ------------------------------------------------------------------
    # Single sentence translation
    # ------------------------------------------------------------------

    def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        return_intermediate: bool = False,
    ) -> Union[str, Dict]:
        """
        Translate a single sentence from src to tgt language.

        Args:
            text:                The source sentence.
            src:                 Source language code (e.g. "hin", "eng").
            tgt:                 Target language code (e.g. "unr", "hoc").
            return_intermediate: If True, return dict with all pivot steps.

        Returns:
            Translated string, or dict with {"steps": [...], "result": "..."}.
        """
        route = self._get_route(src, tgt)

        if self.verbose and len(route) > 1:
            step_str = " -> ".join(
                [LANG_NAMES.get(src, src)] +
                [LANG_NAMES.get(PAIR_CONFIGS[r[0]]["lang_b_code"] if r[1].endswith(PAIR_CONFIGS[r[0]]["lang_b_code"]) else PAIR_CONFIGS[r[0]]["lang_a_code"], "?") for r in route]
            )
            print(f"  [Pivot] {LANG_NAMES.get(src, src)} -> {LANG_NAMES.get(tgt, tgt)}", flush=True)

        steps = []
        current_text = text

        for pair_id, direction in route:
            translator = Translator.get(pair_id)
            if self.verbose:
                src_c, tgt_c = direction.split("_")
                print(f"    [{pair_id}] {LANG_NAMES.get(src_c, src_c)} -> {LANG_NAMES.get(tgt_c, tgt_c)}: {current_text[:60]!r}", flush=True)

            result = translator.translate(current_text, direction, num_beams=self.num_beams)

            steps.append({
                "pair":      pair_id,
                "direction": direction,
                "input":     current_text,
                "output":    result,
            })
            current_text = result

        if return_intermediate:
            return {"steps": steps, "result": current_text}
        return current_text

    # ------------------------------------------------------------------
    # Batch translation
    # ------------------------------------------------------------------

    def translate_batch(
        self,
        texts: List[str],
        src: str,
        tgt: str,
    ) -> List[str]:
        """
        Translate a list of sentences from src to tgt.
        For pivot routes, the full list passes through each hop in sequence.
        """
        route = self._get_route(src, tgt)

        current_texts = texts
        for pair_id, direction in route:
            translator = Translator.get(pair_id)
            if self.verbose:
                src_c, tgt_c = direction.split("_")
                print(
                    f"  [{pair_id}] {LANG_NAMES.get(src_c, src_c)} -> "
                    f"{LANG_NAMES.get(tgt_c, tgt_c)}  ({len(current_texts)} sentences)",
                    flush=True
                )
            current_texts = translator.translate(
                current_texts, direction, num_beams=self.num_beams
            )

        return current_texts

    # ------------------------------------------------------------------
    # Convenience: describe a route
    # ------------------------------------------------------------------

    def describe_route(self, src: str, tgt: str) -> str:
        """Return a human-readable description of the translation route."""
        route = self._get_route(src, tgt)
        src_name = LANG_NAMES.get(src, src)
        tgt_name = LANG_NAMES.get(tgt, tgt)
        if len(route) == 1:
            pair_id, direction = route[0]
            return f"{src_name} -> {tgt_name}  [direct, adaptor: {pair_id}]"
        else:
            steps = []
            for pair_id, direction in route:
                s, t = direction.split("_")
                steps.append(f"{LANG_NAMES.get(s, s)} -[{pair_id}]-> {LANG_NAMES.get(t, t)}")
            return f"{src_name} -> {tgt_name}  [pivot: {' -> '.join(steps)}]"

    # ------------------------------------------------------------------
    # List all supported routes
    # ------------------------------------------------------------------

    def list_routes(self) -> List[str]:
        """Return all available translation routes as human-readable strings."""
        return [self.describe_route(s, t) for s, t in PIVOT_ROUTES.keys()]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Triveni text-to-text translation pipeline",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--src", default=None,
                        help="Source language code: hin | eng | hoc | sat | unr")
    parser.add_argument("--tgt", default=None,
                        help="Target language code: hin | eng | hoc | sat | unr")
    parser.add_argument("--text",   default=None, help="Input text to translate")
    parser.add_argument("--file",   default=None, help="Input file: one sentence per line")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    parser.add_argument("--num_beams", type=int, default=4, help="Beam search width")
    parser.add_argument("--show_steps", action="store_true",
                        help="Show intermediate pivot steps")
    parser.add_argument("--list_routes", action="store_true",
                        help="List all available translation routes and exit")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress messages")
    return parser.parse_args()


def main():
    args = parse_args()
    pipe = TranslationPipeline(num_beams=args.num_beams, verbose=not args.quiet)

    if args.list_routes:
        print("\nAvailable translation routes:")
        for route in pipe.list_routes():
            print(f"  {route}")
        print()
        sys.exit(0)

    if not args.src or not args.tgt:
        print("ERROR: --src and --tgt are required (or use --list_routes)")
        sys.exit(1)

    src = args.src.lower()
    tgt = args.tgt.lower()

    # Validate codes
    valid_codes = set(LANG_NAMES.keys())
    for code, label in [(src, "--src"), (tgt, "--tgt")]:
        if code not in valid_codes:
            print(f"ERROR: {label} '{code}' is not a valid language code.")
            print(f"       Valid codes: {sorted(valid_codes)}")
            sys.exit(1)

    # Show route info
    try:
        route_desc = pipe.describe_route(src, tgt)
        print(f"\nRoute: {route_desc}")
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Collect inputs
    if args.text:
        texts = [args.text]
    elif args.file:
        if not os.path.exists(args.file):
            print(f"ERROR: file not found: {args.file}")
            sys.exit(1)
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        print("ERROR: provide --text or --file")
        sys.exit(1)

    print(f"Translating {len(texts)} sentence(s)...\n")
    start = time.time()

    if args.show_steps and len(texts) == 1:
        result_data = pipe.translate(texts[0], src, tgt, return_intermediate=True)
        print("\n--- Pivot Steps ---")
        for step in result_data["steps"]:
            s, t = step["direction"].split("_")
            print(f"  [{step['pair']}] {LANG_NAMES.get(s, s)} -> {LANG_NAMES.get(t, t)}")
            print(f"    IN : {step['input']}")
            print(f"    OUT: {step['output']}")
        print(f"\nFinal: {result_data['result']}")
        translations = [result_data["result"]]
    elif len(texts) == 1:
        translations = [pipe.translate(texts[0], src, tgt)]
    else:
        translations = pipe.translate_batch(texts, src, tgt)

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s  ({len(texts)/elapsed:.1f} sentences/sec)\n")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for t in translations:
                f.write(t + "\n")
        print(f"Saved {len(translations)} translation(s) to {args.output}")
    else:
        print("--- Results ---")
        for src_text, tgt_text in zip(texts, translations):
            print(f"  IN : {src_text}")
            print(f"  OUT: {tgt_text}")
            print()


if __name__ == "__main__":
    main()
