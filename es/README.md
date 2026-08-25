# es — English ↔ Santali Translation Dataset

## Overview

This folder contains the bilingual dataset for training a **LoRA fine-tuned translation model** between **English** and **Santali** — an Austroasiatic language spoken by the Santal people across Eastern India (Jharkhand, West Bengal, Odisha, Bihar, Assam).

The dataset supports **bidirectional translation**:
- English → Santali
- Santali → English

---

## Language Information

| Property | Value |
|----------|-------|
| Language pair | English (`eng`) ↔ Santali (`sat`) |
| Language family | English: Indo-European; Santali: Austroasiatic (Munda) |
| Script | English: Latin; Santali: Ol Chiki (ᱚᱞ ᱪᱤᱠᱤ) |
| ISO codes | `en` / `sat` |

---

## Dataset Statistics

| Split | File | Rows | % of total |
|-------|------|------|-----------|
| Train | `train.jsonl` | 50,085 | ~80% |
| Validation | `val.jsonl` | 6,260 | ~10% |
| Test | `test.jsonl` | 6,262 | ~10% |
| **Total** | | **62,607** | 100% |

> Original source file: `train.csv`

---

## File Format

Each `.jsonl` file is a **JSONL** (JSON Lines) file — one JSON object per line.

### Schema

```json
{
  "translation": {
    "eng_sat": { "source": "<English sentence>", "target": "<Santali sentence>" },
    "sat_eng": { "source": "<Santali sentence>", "target": "<English sentence>" }
  }
}
```

### Example

```json
{
  "translation": {
    "eng_sat": {
      "source": "Around 6500 BCE, agriculture emerged in Balochistan.",
      "target": "ᱞᱟᱹᱜᱵᱷᱟᱹᱜ ᱖,᱕᱐᱐ ᱠᱷᱤᱥᱴᱚᱯᱩᱨᱵᱟᱵᱫᱚ ᱨᱮ ᱵᱮᱞᱩᱪᱤᱥᱛᱟᱱ ᱨᱮ ᱪᱟᱥᱠᱟᱹᱢᱤ ᱨᱮᱭᱟᱜ ᱩᱯᱮᱞ ᱦᱩᱭᱞᱮᱱᱟ ᱾"
    },
    "sat_eng": {
      "source": "ᱞᱟᱹᱜᱵᱷᱟᱹᱜ ᱖,᱕᱐᱐ ᱠᱷᱤᱥᱴᱚᱯᱩᱨᱵᱟᱵᱫᱚ ᱨᱮ ᱵᱮᱞᱩᱪᱤᱥᱛᱟᱱ ᱨᱮ ᱪᱟᱥᱠᱟᱹᱢᱤ ᱨᱮᱭᱟᱜ ᱩᱯᱮᱞ ᱦᱩᱭᱞᱮᱱᱟ ᱾",
      "target": "Around 6500 BCE, agriculture emerged in Balochistan."
    }
  }
}
```

---

## Usage with LoRA Fine-Tuning

Each sample stores **both translation directions**. During training, sample either `eng_sat` or `sat_eng` as the active direction per batch.

### Prompt template example

```
Translate the following sentence from English to Santali:
{source}
Translation: {target}
```

```
Translate the following sentence from Santali to English:
{source}
Translation: {target}
```

---

## Directory Structure

```
es/
├── train.jsonl   # 50,085 bidirectional pairs (training)
├── val.jsonl     # 6,260 bidirectional pairs (validation)
├── test.jsonl    # 6,262 bidirectional pairs (test)
├── train.csv     # Original source CSV
└── README.md     # This file
```

---

## Notes

- Split ratio: 80% / 10% / 10%. Random seed: `42`.
- Santali text uses the **Ol Chiki** script (Unicode block U+1C50–U+1C7F). Ensure your tokeniser has Unicode/UTF-8 support.
- The original CSV had a `english,santali` header row which is excluded from the JSONL files.
- 1 row from the original CSV was skipped due to a missing value (62,608 raw rows → 62,607 valid pairs).
