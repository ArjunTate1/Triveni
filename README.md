# Triveni — LoRA Translation Pipeline

Neural machine translation for low-resource Indian tribal languages using LoRA fine-tuning.
Translates between **Hindi, Ho, Santali, Mundari** and **English**.

---

## Quick Start (for teammates)

```bash
# 1. Clone
git clone https://github.com/ArjunTate1/Triveni.git
cd Triveni

# 2. Install dependencies
pip install torch transformers peft datasets accelerate sentencepiece sacrebleu tqdm

# 3. Translate immediately — no training needed, adaptors are included
python pipeline.py --src hin --tgt hoc --text "आप कैसे हैं?"
python pipeline.py --src hin --tgt eng --text "नमस्ते दुनिया"
python pipeline.py --list_routes
```

> The base model (`Helsinki-NLP/opus-mt-mul-en`, ~300 MB) downloads automatically
> from HuggingFace on first run. Internet required once.

---

## Supported Languages

| Code  | Language | Script           |
|-------|----------|------------------|
| `hin` | Hindi    | Devanagari       |
| `eng` | English  | Latin            |
| `hoc` | Ho       | Latin+diacritics |
| `sat` | Santali  | Ol Chiki         |
| `unr` | Mundari  | Devanagari       |

---

## Translation Routes

### Currently available (trained adaptors included)

| Route | Model | Status |
|-------|-------|--------|
| Hindi ↔ English | `he` adaptor | ✅ Ready |
| English ↔ Ho | `eh` adaptor | ✅ Ready |
| **Hindi → Ho** | `he` + `eh` (pivot via English) | ✅ Ready |
| **Ho → Hindi** | `eh` + `he` (pivot via English) | ✅ Ready |

### Coming soon (training in progress)

| Route | Model | Status |
|-------|-------|--------|
| Hindi ↔ Mundari | `ht` adaptor | 🔄 Training |
| English ↔ Santali | `es` adaptor | 🔄 Training |
| Hindi → Santali | `he` + `es` (pivot) | 🔄 Training |

---

## Usage

### pipeline.py — recommended for all translations

```bash
# Hindi → Ho  (pivot: Hindi → English → Ho)
python pipeline.py --src hin --tgt hoc --text "आप कहाँ जा रहे हैं?"

# Ho → Hindi
python pipeline.py --src hoc --tgt hin --text "Ape do okon renko?"

# Hindi → English
python pipeline.py --src hin --tgt eng --text "नमस्ते, आप कैसे हैं?"

# English → Hindi
python pipeline.py --src eng --tgt hin --text "Where are you going?"

# Show intermediate pivot steps
python pipeline.py --src hin --tgt hoc --text "नमस्ते" --show_steps

# Translate a file (one sentence per line)
python pipeline.py --src hin --tgt hoc --file input.txt --output output.txt

# List all available routes
python pipeline.py --list_routes
```

### translate.py — single model, direct control

```bash
# Hindi → English
python translate.py --pair he --direction hin_eng --text "आप कैसे हैं?"

# English → Hindi
python translate.py --pair he --direction eng_hin --text "How are you?"

# English → Ho
python translate.py --pair eh --direction eng_hoc --text "Where are you going?"

# Ho → English
python translate.py --pair eh --direction hoc_eng --text "Ape do okon renko?"
```

### Python API

```python
from pipeline import TranslationPipeline

pipe = TranslationPipeline()

# Single translation
result = pipe.translate("आप कैसे हैं?", src="hin", tgt="hoc")
print(result)

# Batch translation
results = pipe.translate_batch(
    ["नमस्ते", "आप कैसे हैं?", "कहाँ जा रहे हो?"],
    src="hin",
    tgt="hoc"
)

# See pivot steps
data = pipe.translate("नमस्ते", "hin", "hoc", return_intermediate=True)
for step in data["steps"]:
    print(f"{step['pair']}: {step['input']} -> {step['output']}")
```

---

## Project Structure

```
Triveni/
├── config.py             # All settings: model, LoRA params, routes
├── dataset_utils.py      # Data loading and prompt formatting
├── train.py              # LoRA fine-tuning (one language pair)
├── train_all.ps1         # Train all pairs sequentially (Windows)
├── translate.py          # Single-pair inference
├── pipeline.py           # Full pipeline with pivot routing
├── evaluate.py           # BLEU / chrF evaluation
├── split_datasets.py     # Raw data → train/val/test splits
│
├── adaptors/             # Trained LoRA weights (included in repo)
│   ├── he/               # Hindi ↔ English adaptor ✅
│   │   ├── adapter_config.json
│   │   ├── adapter_model.safetensors
│   │   └── ...tokenizer files
│   └── eh/               # English ↔ Ho adaptor ✅
│       ├── adapter_config.json
│       ├── adapter_model.safetensors
│       └── ...tokenizer files
│
├── he/                   # Hindi ↔ English dataset
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
└── eh/                   # English ↔ Ho dataset
    ├── train.jsonl
    ├── val.jsonl
    └── test.jsonl
```

---

## Training Your Own Adaptors

If you want to train the remaining pairs (`es`, `ht`) or retrain existing ones:

```bash
# Train one pair
python train.py --pair ht          # Hindi ↔ Mundari
python train.py --pair es          # English ↔ Santali

# Resume an interrupted run
python train.py --pair es --resume

# Train all 4 pairs (Windows PowerShell)
.\train_all.ps1

# Quick test run (200 samples, no evaluation)
.\train_all.ps1 -MaxSamples 200 -NoEval
```

Trained adaptors are saved to `adaptors/<pair_id>/`.

---

## Evaluation

```bash
# Evaluate a trained adaptor on the test set
python evaluate.py --pair he
python evaluate.py --pair eh
python evaluate.py --all           # all pairs

# Quick check on 100 samples
python evaluate.py --pair he --max_samples 100
```

Results saved to `results/`.

---

## How It Works

### LoRA (Low-Rank Adaptation)

Instead of fine-tuning the full ~78M parameter base model, LoRA trains only
**~590K parameters (0.75%)** injected into the attention layers. This means:

- Each adaptor is only **~2.3 MB** (vs ~300 MB for a full model)
- Training is fast even on CPU
- The same base model is shared across all 4 language pairs

### Pivot Translation

No direct Hindi ↔ Ho or Hindi ↔ Santali dataset exists, so those routes chain two models:

```
Hindi → Ho:
  Hindi --[he adaptor]--> English --[eh adaptor]--> Ho

Ho → Hindi:
  Ho --[eh adaptor]--> English --[he adaptor]--> Hindi
```

This is handled automatically by `pipeline.py` — just specify `--src` and `--tgt`.

### Base Model

All adaptors are built on top of `Helsinki-NLP/opus-mt-mul-en` (MarianMT).
For production quality on a GPU, switch `BASE_MODEL` in `config.py` to
`ai4bharat/indictrans2-indic-en-1B`.

---

## Dataset Stats

| Folder | Pair              | Train   | Val   | Test  | Total  |
|--------|-------------------|---------|-------|-------|--------|
| `he/`  | Hindi ↔ English   | 2,293   | 286   | 288   | 2,867  |
| `eh/`  | English ↔ Ho      | 1,284   | 161   | 161   | 1,606  |
| `es/`  | English ↔ Santali | 50,085  | 6,260 | 6,262 | 62,607 |
| `ht/`  | Hindi ↔ Mundari   | 14,247  | 1,780 | 1,782 | 17,809 |

> `es/` and `ht/` datasets are included for training but adaptors not yet pushed.

---

## Requirements

```
Python >= 3.9
torch >= 2.0
transformers >= 5.0
peft >= 0.20
datasets
accelerate
sentencepiece
sacrebleu
tqdm
```

Install all at once:
```bash
pip install torch transformers peft datasets accelerate sentencepiece sacrebleu tqdm
```

---

## Roadmap

- [x] Hindi ↔ English (LoRA adaptor)
- [x] English ↔ Ho (LoRA adaptor)
- [x] Hindi → Ho pivot pipeline
- [ ] English ↔ Santali (LoRA adaptor)
- [ ] Hindi ↔ Mundari (LoRA adaptor)
- [ ] Voice-to-voice: ASR + pipeline + TTS
