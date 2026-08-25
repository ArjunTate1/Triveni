"""
split_datasets.py
Splits raw dataset files in es/, he/, ht/ folders into train/val/test splits.
The eh/ folder is already split -- this script only normalises it.
Split ratio: 80% train / 10% val / 10% test
Random seed: 42 (reproducible)
"""

import json
import csv
import random
import os
import sys
import traceback

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

SEED = 42
TRAIN_RATIO = 0.80
VAL_RATIO   = 0.10

random.seed(SEED)

BASE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def split_indices(n, train_r=TRAIN_RATIO, val_r=VAL_RATIO):
    indices = list(range(n))
    random.shuffle(indices)
    train_end = int(n * train_r)
    val_end   = train_end + int(n * val_r)
    return indices[:train_end], indices[train_end:val_end], indices[val_end:]


def save_jsonl(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("  Saved {:>6,} rows -> {}".format(len(rows), os.path.relpath(path, BASE)))


# ---------------------------------------------------------------------------
# eh  -- English <-> Hoc  (already split, just re-emit as clean JSONL)
# ---------------------------------------------------------------------------

def process_eh():
    print("\n[eh] English <-> Hoc  -- normalising existing splits to clean JSONL")
    folder = os.path.join(BASE, "eh")

    mapping = {
        "train": "train-data_eng-hoc.json",
        "val":   "validation-data_eng-hoc.json",
        "test":  "test-data_eng-hoc.json",
    }

    for split, fname in mapping.items():
        src = os.path.join(folder, fname)
        rows = []
        with open(src, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                t = obj.get("translation", obj)
                eng = t.get("eng", t.get("en", "")).strip()
                hoc = t.get("hoc", t.get("ho", "")).strip()
                if eng and hoc:
                    rows.append({
                        "translation": {
                            "eng_hoc": {"source": eng, "target": hoc},
                            "hoc_eng": {"source": hoc, "target": eng},
                        }
                    })
        dst = os.path.join(folder, "{}.jsonl".format(split))
        save_jsonl(rows, dst)

    print("  [eh] Done.")


# ---------------------------------------------------------------------------
# es  -- English <-> Santali  (CSV, header: english,santali)
# ---------------------------------------------------------------------------

def process_es():
    print("\n[es] English <-> Santali  -- splitting CSV")
    folder = os.path.join(BASE, "es")
    src    = os.path.join(folder, "train.csv")

    rows = []
    with open(src, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            eng = (row.get("english") or row.get("English") or "").strip()
            san = (row.get("santali") or row.get("Santali") or "").strip()
            if eng and san:
                rows.append({
                    "translation": {
                        "eng_sat": {"source": eng, "target": san},
                        "sat_eng": {"source": san, "target": eng},
                    }
                })

    print("  Loaded {:,} valid pairs".format(len(rows)))
    train_idx, val_idx, test_idx = split_indices(len(rows))

    save_jsonl([rows[i] for i in train_idx], os.path.join(folder, "train.jsonl"))
    save_jsonl([rows[i] for i in val_idx],   os.path.join(folder, "val.jsonl"))
    save_jsonl([rows[i] for i in test_idx],  os.path.join(folder, "test.jsonl"))
    print("  [es] Done.")


# ---------------------------------------------------------------------------
# he  -- Hindi <-> English  (TSV: eng\thindi, no header)
# ---------------------------------------------------------------------------

def process_he():
    print("\n[he] Hindi <-> English  -- splitting TSV")
    folder = os.path.join(BASE, "he")
    src    = os.path.join(folder, "DATASET.tsv")

    rows = []
    with open(src, encoding="utf-8", newline="") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            eng = parts[0].strip()
            hin = parts[1].strip()
            if eng and hin:
                rows.append({
                    "translation": {
                        "eng_hin": {"source": eng, "target": hin},
                        "hin_eng": {"source": hin, "target": eng},
                    }
                })

    print("  Loaded {:,} valid pairs".format(len(rows)))
    train_idx, val_idx, test_idx = split_indices(len(rows))

    save_jsonl([rows[i] for i in train_idx], os.path.join(folder, "train.jsonl"))
    save_jsonl([rows[i] for i in val_idx],   os.path.join(folder, "val.jsonl"))
    save_jsonl([rows[i] for i in test_idx],  os.path.join(folder, "test.jsonl"))
    print("  [he] Done.")


# ---------------------------------------------------------------------------
# ht  -- Hindi <-> Mundari/Unr  (TSV: hindi\tmundari, no header)
# ---------------------------------------------------------------------------

def process_ht():
    print("\n[ht] Hindi <-> Mundari (Unr)  -- splitting TSV")
    folder = os.path.join(BASE, "ht")
    src    = os.path.join(folder, "translation-hi-unr.tsv")

    rows = []
    with open(src, encoding="utf-8", newline="") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            hin = parts[0].strip()
            unr = parts[1].strip()
            if hin and unr:
                rows.append({
                    "translation": {
                        "hin_unr": {"source": hin, "target": unr},
                        "unr_hin": {"source": unr, "target": hin},
                    }
                })

    print("  Loaded {:,} valid pairs".format(len(rows)))
    train_idx, val_idx, test_idx = split_indices(len(rows))

    save_jsonl([rows[i] for i in train_idx], os.path.join(folder, "train.jsonl"))
    save_jsonl([rows[i] for i in val_idx],   os.path.join(folder, "val.jsonl"))
    save_jsonl([rows[i] for i in test_idx],  os.path.join(folder, "test.jsonl"))
    print("  [ht] Done.")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        process_eh()
        process_es()
        process_he()
        process_ht()
        print("\n=== All splits complete ===")
    except Exception:
        traceback.print_exc()
        sys.exit(1)
