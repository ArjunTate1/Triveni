# ht — Hindi ↔ Mundari (Unr) Translation Dataset

## Overview

This folder contains the bilingual dataset for training a **LoRA fine-tuned translation model** between **Hindi** and **Mundari (Unr)** — an Austroasiatic language spoken by the Munda people primarily in Jharkhand, Odisha, and West Bengal, India.

The dataset supports **bidirectional translation**:
- Hindi → Mundari
- Mundari → Hindi

---

## Language Information

| Property | Value |
|----------|-------|
| Language pair | Hindi (`hin`) ↔ Mundari/Unr (`unr`) |
| Language family | Hindi: Indo-European (Indo-Aryan); Mundari: Austroasiatic (Munda) |
| Script | Hindi: Devanagari; Mundari: Devanagari (romanized in some sources) |
| ISO codes | `hi` / `unr` |

---

## Dataset Statistics

| Split | File | Rows | % of total |
|-------|------|------|-----------|
| Train | `train.jsonl` | 14,247 | ~80% |
| Validation | `val.jsonl` | 1,780 | ~10% |
| Test | `test.jsonl` | 1,782 | ~10% |
| **Total** | | **17,809** | 100% |

> Original source file: `translation-hi-unr.tsv`
> Note: 17 rows from the original 17,826 were skipped due to missing values.

---

## File Format

Each `.jsonl` file is a **JSONL** (JSON Lines) file — one JSON object per line.

### Schema

```json
{
  "translation": {
    "hin_unr": { "source": "<Hindi sentence>",   "target": "<Mundari sentence>" },
    "unr_hin": { "source": "<Mundari sentence>", "target": "<Hindi sentence>" }
  }
}
```

### Example

```json
{
  "translation": {
    "hin_unr": {
      "source": "वे भी कमजोर पड़ रहे हैं",
      "target": "इनकु कमजोरोःतानाको"
    },
    "unr_hin": {
      "source": "इनकु कमजोरोःतानाको",
      "target": "वे भी कमजोर पड़ रहे हैं"
    }
  }
}
```

---

## Usage with LoRA Fine-Tuning

Each sample stores **both translation directions**. During training, sample either `hin_unr` or `unr_hin` as the active direction per batch.

### Prompt template example

```
Translate the following sentence from Hindi to Mundari:
{source}
Translation: {target}
```

```
Translate the following sentence from Mundari to Hindi:
{source}
Translation: {target}
```

---

## Directory Structure

```
ht/
├── train.jsonl              # 14,247 bidirectional pairs (training)
├── val.jsonl                # 1,780 bidirectional pairs (validation)
├── test.jsonl               # 1,782 bidirectional pairs (test)
├── translation-hi-unr.tsv  # Original source TSV (Hindi TAB Mundari, no header)
└── README.md                # This file
```

---

## Notes

- Split ratio: 80% / 10% / 10%. Random seed: `42`.
- The original TSV has no header row. Column order is: `Hindi \t Mundari`.
- Both languages in this dataset use the **Devanagari** script. The Mundari text may contain characters and vowel markers not typical in standard Hindi; ensure your tokeniser is trained on a broad Unicode range.
- This is a **low-resource** language pair. The relatively large dataset (~17 K pairs) makes it well-suited for LoRA adaptor fine-tuning.
