---
base_model: Helsinki-NLP/opus-mt-mul-en
library_name: peft
language:
  - hi
  - unr
tags:
  - lora
  - translation
  - low-resource
  - indic-languages
  - mundari
  - hindi
  - peft
  - transformers
---

# Triveni — Hindi ↔ Mundari (ht) LoRA Adaptor

A LoRA fine-tuned translation model for **Hindi ↔ Mundari (Unr)** — a low-resource
Austroasiatic language spoken primarily in Jharkhand and Odisha, India.

Part of the **Triveni** project: LoRA translation adaptors for Indian tribal languages.

---

## Model Details

| Property | Value |
|----------|-------|
| Base model | `Helsinki-NLP/opus-mt-mul-en` (MarianMT) |
| Fine-tuning method | LoRA (Low-Rank Adaptation) |
| Task | Bidirectional seq2seq translation |
| Languages | Hindi (`hin`) ↔ Mundari (`unr`) |
| Mundari script | Devanagari |
| Hindi script | Devanagari |
| Trainable params | 589,824 / 78,108,672 (0.76%) |
| Adaptor size | ~2.3 MB |
| Developed by | Arjun Tate |
| Framework | HuggingFace Transformers + PEFT 0.20.0 |

---

## Quick Start

### Install dependencies

```bash
pip install torch transformers peft sentencepiece
```

### Load and translate

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Helsinki-NLP/opus-mt-mul-en"
ADAPTOR    = "adaptors/ht"   # path to this folder after cloning

# Load
tokenizer = AutoTokenizer.from_pretrained(ADAPTOR)
base  = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)
model = PeftModel.from_pretrained(base, ADAPTOR)
model = model.merge_and_unload()   # merge for faster inference
model.eval()

def translate(text, src_lang, tgt_lang):
    prompt = (
        f"Translate the following sentence from {src_lang} to {tgt_lang}:\n"
        f"{text}\n"
        f"Translation:"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
    output = model.generate(**inputs, num_beams=4, max_length=256)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Hindi -> Mundari
print(translate("आप कहाँ जा रहे हैं?", "Hindi", "Mundari"))

# Mundari -> Hindi
print(translate("ञाम ओकोन रेन्को?", "Mundari", "Hindi"))
```

---

## Supported Directions

| Direction key | From | To |
|---------------|------|----|
| `hin_unr` | Hindi | Mundari |
| `unr_hin` | Mundari | Hindi |

---

## Training Details

### Dataset

| Split | Pairs |
|-------|-------|
| Train | 14,247 |
| Val   | 1,780  |
| Test  | 1,782  |
| **Total** | **17,809** |

Source: Hindi ↔ Mundari (Unr) parallel corpus. Both translation directions are
encoded in every training sample — the model is trained to translate in both
directions in a single pass.

### LoRA Configuration

```python
LoraConfig(
    task_type     = TaskType.SEQ_2_SEQ_LM,
    r             = 16,
    lora_alpha    = 32,
    lora_dropout  = 0.05,
    bias          = "none",
    target_modules = ["q_proj", "v_proj"],
)
```

### Training Hyperparameters

| Parameter | Value |
|-----------|-------|
| Epochs | 5 |
| Batch size | 4 |
| Gradient accumulation steps | 4 (effective batch = 16) |
| Learning rate | 3e-4 |
| Warmup steps | 100 |
| Weight decay | 0.01 |
| Optimizer | AdamW |
| Precision | fp32 (CPU) |
| Seed | 42 |

### Training Results

| Epoch | Eval Loss |
|-------|-----------|
| 1 | 4.5841 |
| 2 | 4.1712 |
| 3 | 3.9667 |
| 4 | 3.8680 |
| 5 | **3.8359** |

- Training loss: 139.54 → 16.45 (start → end)
- Total training steps: 8,905
- Best eval loss: **3.8359** (epoch 5)

---

## Files in This Adaptor

| File | Purpose |
|------|---------|
| `adapter_model.safetensors` | Trained LoRA weights |
| `adapter_config.json` | LoRA architecture config |
| `tokenizer_config.json` | Tokenizer settings |
| `source.spm` | Source SentencePiece vocabulary |
| `target.spm` | Target SentencePiece vocabulary |
| `vocab.json` | Token → ID mappings |

---

## Limitations

- Trained on **17,809 pairs** — reasonable for a low-resource language but
  translations may be imperfect for complex or domain-specific sentences.
- Base model (`opus-mt-mul-en`) is English-centric. For better quality,
  retrain on `ai4bharat/indictrans2-indic-en-1B` with a GPU.
- No direct Hindi ↔ Ho or Hindi ↔ Santali model in this adaptor — see the
  Triveni repo for pivot pipelines.

---

## Part of Triveni

This adaptor is one of four being developed in the Triveni project:

| Adaptor | Pair | Status |
|---------|------|--------|
| `ht` | Hindi ↔ Mundari | ✅ This model |
| `he` | Hindi ↔ English | ✅ Trained |
| `eh` | English ↔ Ho | ✅ Trained |
| `es` | English ↔ Santali | 🔄 In progress |

Repository: [github.com/ArjunTate1/Triveni](https://github.com/ArjunTate1/Triveni)
