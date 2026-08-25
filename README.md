# LoRA Translation Adaptors — Dataset Collection

This repository contains bilingual translation datasets and LoRA adaptor training data for **4 low-resource Indian language pairs**. Each folder is self-contained and ready to use for fine-tuning a seq2seq or decoder-only language model using the **LoRA (Low-Rank Adaptation)** method.

All datasets support **bidirectional translation** — both directions are encoded in every sample.

---

## Folder Overview

| Folder | Languages | Direction | Total Pairs | Train | Val | Test |
|--------|-----------|-----------|-------------|-------|-----|------|
| [`eh/`](./eh/) | English ↔ Hoc (Ho) | `eng_hoc` / `hoc_eng` | 1,606 | 1,284 | 161 | 161 |
| [`es/`](./es/) | English ↔ Santali | `eng_sat` / `sat_eng` | 62,607 | 50,085 | 6,260 | 6,262 |
| [`he/`](./he/) | Hindi ↔ English | `eng_hin` / `hin_eng` | 2,867 | 2,293 | 286 | 288 |
| [`ht/`](./ht/) | Hindi ↔ Mundari (Unr) | `hin_unr` / `unr_hin` | 17,809 | 14,247 | 1,780 | 1,782 |

**Total across all datasets: 84,889 bilingual pairs**

---

## Data Format

Every split file (`.jsonl`) uses the same schema:

```json
{
  "translation": {
    "<direction_A>": { "source": "...", "target": "..." },
    "<direction_B>": { "source": "...", "target": "..." }
  }
}
```

Each line is a complete, self-contained JSON object. The two direction keys (e.g. `eng_hoc` / `hoc_eng`) let you train both directions in a single pass.

---

## Language Details

| Code | Language | Family | Script |
|------|----------|--------|--------|
| `eng` | English | Indo-European (Germanic) | Latin |
| `hoc` | Hoc / Ho | Austroasiatic (Munda) | Latin + diacritics |
| `sat` | Santali | Austroasiatic (Munda) | Ol Chiki (ᱚᱞ ᱪᱤᱠᱤ) |
| `hin` | Hindi | Indo-European (Indo-Aryan) | Devanagari |
| `unr` | Mundari / Unr | Austroasiatic (Munda) | Devanagari |

---

## Splits & Reproducibility

All datasets were split with:
- **Ratio**: 80% train / 10% validation / 10% test
- **Random seed**: `42`
- **Script**: `split_datasets.py` (included at root)

---

## Training with LoRA

### Recommended prompt format

```
Translate the following sentence from {source_lang} to {target_lang}:
{source}
Translation: {target}
```

### Tips

- **Both directions in one adaptor**: Each sample already encodes both translation directions. Randomly pick one direction per training step to train a single adaptor that handles both.
- **Tokeniser**: All languages use Unicode. Use a tokeniser with a broad multilingual vocabulary (e.g. `google/mt5-base`, `facebook/mbart-large-cc25`, `ai4bharat/indictrans2`, or `llama` with a multilingual tokeniser).
- **LoRA target modules**: For encoder-decoder models, target `q_proj`, `v_proj` in both encoder and decoder. For decoder-only, target `q_proj`, `v_proj` in all transformer blocks.
- **Low-resource languages** (`eh`, `he`): Use a lower learning rate and more epochs. Consider data augmentation via back-translation.

### Example LoRA config (PEFT / HuggingFace)

```python
from peft import LoraConfig, TaskType

lora_config = LoraConfig(
    task_type=TaskType.SEQ_2_SEQ_LM,  # or CAUSAL_LM for decoder-only
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
)
```

---

## Directory Structure

```
lora adaptor/
├── eh/
│   ├── train.jsonl
│   ├── val.jsonl
│   ├── test.jsonl
│   ├── train-data_eng-hoc.json
│   ├── validation-data_eng-hoc.json
│   ├── test-data_eng-hoc.json
│   └── README.md
├── es/
│   ├── train.jsonl
│   ├── val.jsonl
│   ├── test.jsonl
│   ├── train.csv
│   └── README.md
├── he/
│   ├── train.jsonl
│   ├── val.jsonl
│   ├── test.jsonl
│   ├── DATASET.tsv
│   └── README.md
├── ht/
│   ├── train.jsonl
│   ├── val.jsonl
│   ├── test.jsonl
│   ├── translation-hi-unr.tsv
│   └── README.md
├── split_datasets.py   # Data splitting script
└── README.md           # This file
```

---

## Regenerating the Splits

```bash
python split_datasets.py
```

This re-reads the original source files and regenerates all JSONL splits from scratch.
