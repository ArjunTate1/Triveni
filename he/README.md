# he — Hindi ↔ English Translation Dataset

## Overview

This folder contains the bilingual dataset for training a **LoRA fine-tuned translation model** between **Hindi** and **English**.

The dataset supports **bidirectional translation**:
- Hindi → English
- English → Hindi

---

## Language Information

| Property | Value |
|----------|-------|
| Language pair | Hindi (`hin`) ↔ English (`eng`) |
| Language family | Hindi: Indo-European (Indo-Aryan); English: Indo-European (Germanic) |
| Script | Hindi: Devanagari; English: Latin |
| ISO codes | `hi` / `en` |

---

## Dataset Statistics

| Split | File | Rows | % of total |
|-------|------|------|-----------|
| Train | `train.jsonl` | 2,293 | ~80% |
| Validation | `val.jsonl` | 286 | ~10% |
| Test | `test.jsonl` | 288 | ~10% |
| **Total** | | **2,867** | 100% |

> Original source file: `DATASET.tsv`

---

## File Format

Each `.jsonl` file is a **JSONL** (JSON Lines) file — one JSON object per line.

### Schema

```json
{
  "translation": {
    "eng_hin": { "source": "<English sentence>", "target": "<Hindi sentence>" },
    "hin_eng": { "source": "<Hindi sentence>",   "target": "<English sentence>" }
  }
}
```

### Example

```json
{
  "translation": {
    "eng_hin": { "source": "Hello!",    "target": "नमस्ते।" },
    "hin_eng": { "source": "नमस्ते।", "target": "Hello!" }
  }
}
```

---

## Usage with LoRA Fine-Tuning

Each sample stores **both translation directions**. During training, sample either `eng_hin` or `hin_eng` as the active direction per batch.

### Prompt template example

```
Translate the following sentence from English to Hindi:
{source}
Translation: {target}
```

```
Translate the following sentence from Hindi to English:
{source}
Translation: {target}
```

---

## Directory Structure

```
he/
├── train.jsonl    # 2,293 bidirectional pairs (training)
├── val.jsonl      # 286 bidirectional pairs (validation)
├── test.jsonl     # 288 bidirectional pairs (test)
├── DATASET.tsv    # Original source TSV (English TAB Hindi, no header)
└── README.md      # This file
```

---

## Notes

- Split ratio: 80% / 10% / 10%. Random seed: `42`.
- The original TSV has no header row. Column order is: `English \t Hindi`.
- Hindi text uses the **Devanagari** script (Unicode block U+0900–U+097F). Ensure UTF-8 support in your tokeniser.
