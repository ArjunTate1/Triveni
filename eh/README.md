# eh — English ↔ Hoc (Ho) Translation Dataset

## Overview

This folder contains the bilingual dataset for training a **LoRA fine-tuned translation model** between **English** and **Hoc (Ho)** — an Austroasiatic language spoken primarily in the Jharkhand / Odisha region of India.

The dataset supports **bidirectional translation**:
- English → Hoc
- Hoc → English

---

## Language Information

| Property | Value |
|----------|-------|
| Language pair | English (`eng`) ↔ Hoc/Ho (`hoc`) |
| Language family | English: Indo-European; Hoc: Austroasiatic (Munda) |
| Script | English: Latin; Hoc: Latin (romanized with diacritics) |
| ISO codes | `en` / `hoc` |

---

## Dataset Statistics

| Split | File | Rows | % of total |
|-------|------|------|-----------|
| Train | `train.jsonl` | 1,284 | ~80% |
| Validation | `val.jsonl` | 161 | ~10% |
| Test | `test.jsonl` | 161 | ~10% |
| **Total** | | **1,606** | 100% |

> Original source files: `train-data_eng-hoc.json`, `validation-data_eng-hoc.json`, `test-data_eng-hoc.json`

---

## File Format

Each file is a **JSONL** (JSON Lines) file — one JSON object per line.

### Schema

```json
{
  "translation": {
    "eng_hoc": { "source": "<English sentence>", "target": "<Hoc sentence>" },
    "hoc_eng": { "source": "<Hoc sentence>",     "target": "<English sentence>" }
  }
}
```

### Example

```json
{
  "translation": {
    "eng_hoc": { "source": "Where do you come from?", "target": "Ape do okon renko?" },
    "hoc_eng": { "source": "Ape do okon renko?",       "target": "Where do you come from?" }
  }
}
```

---

## Usage with LoRA Fine-Tuning

Each sample intentionally stores **both translation directions** so a single training pass teaches the model to translate in both directions. During training, you can sample either `eng_hoc` or `hoc_eng` as the active direction per batch.

### Prompt template example

```
Translate the following sentence from English to Hoc:
{source}
Translation: {target}
```

```
Translate the following sentence from Hoc to English:
{source}
Translation: {target}
```

---

## Directory Structure

```
eh/
├── train.jsonl                  # 1,284 bidirectional pairs (training)
├── val.jsonl                    # 161 bidirectional pairs (validation)
├── test.jsonl                   # 161 bidirectional pairs (test)
├── train-data_eng-hoc.json      # Original source (train)
├── validation-data_eng-hoc.json # Original source (validation)
├── test-data_eng-hoc.json       # Original source (test)
└── README.md                    # This file
```

---

## Notes

- The original dataset was already pre-split; the JSONL files are a normalised re-export.
- Split seed: `42` (reproducible).
- Romanised Hoc text includes special diacritics (e.g. `ḱ`, `ć`, `ṅ`). Ensure your tokeniser handles Unicode correctly.
