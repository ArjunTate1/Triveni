"""
train.py
========
LoRA fine-tuning script for a single language pair.

Usage:
    python train.py --pair ht
    python train.py --pair eh --epochs 20 --lr 5e-5
    python train.py --pair es --batch_size 8 --max_samples 5000

The trained LoRA adaptor is saved to:
    adaptors/<pair_id>/   (contains adapter_config.json + adapter_model.bin)

The full model (base + adaptor merged) is NOT saved by default to save disk.
Use translate.py or pipeline.py to load base model + adaptor at runtime.
"""

import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    EarlyStoppingCallback,
)
from peft import LoraConfig, TaskType, get_peft_model, PeftModel

from config import (
    BASE_MODEL,
    PAIR_CONFIGS,
    LORA_CONFIG,
    TRAINING_DEFAULTS,
    ADAPTORS_DIR,
)
from dataset_utils import load_pair_datasets


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Train LoRA adaptor for one language pair")
    parser.add_argument(
        "--pair", required=True, choices=list(PAIR_CONFIGS.keys()),
        help="Language pair ID: ht | eh | es | he"
    )
    parser.add_argument("--base_model",   default=None, help="Override base model")
    parser.add_argument("--epochs",       type=int,   default=None, help="Override num_train_epochs")
    parser.add_argument("--lr",           type=float, default=None, help="Override learning_rate")
    parser.add_argument("--batch_size",   type=int,   default=None, help="Override per_device_train_batch_size")
    parser.add_argument("--max_samples",  type=int,   default=None, help="Cap training samples (for quick tests)")
    parser.add_argument("--resume",       action="store_true",       help="Resume from existing adaptor checkpoint")
    parser.add_argument("--no_eval",      action="store_true",       help="Skip eval during training (faster on CPU)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main training function
# ---------------------------------------------------------------------------

def train(args):
    pair_id  = args.pair
    pair_cfg = PAIR_CONFIGS[pair_id]
    base_model_name = args.base_model or BASE_MODEL

    print(f"\n{'='*60}")
    print(f"  Triveni LoRA Training")
    print(f"  Pair      : {pair_id} — {pair_cfg['name']}")
    print(f"  Base model: {base_model_name}")
    print(f"  Device    : {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # 1. Load tokenizer
    # ------------------------------------------------------------------
    print("[1/5] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    # Some MarianMT models don't expose as_target_tokenizer — patch it
    if not hasattr(tokenizer, "as_target_tokenizer"):
        from contextlib import contextmanager

        @contextmanager
        def _as_target(self):
            yield

        import types
        tokenizer.as_target_tokenizer = types.MethodType(_as_target, tokenizer)

    # ------------------------------------------------------------------
    # 2. Load datasets
    # ------------------------------------------------------------------
    print("[2/5] Loading datasets...")
    splits_to_load = ["train"] if args.no_eval else ["train", "val"]
    datasets = load_pair_datasets(pair_id, tokenizer, splits=splits_to_load)

    train_dataset = datasets["train"]
    eval_dataset  = datasets.get("val", None)

    # Optional sample cap for quick smoke tests
    if args.max_samples and len(train_dataset) > args.max_samples:
        from torch.utils.data import Subset
        indices = list(range(args.max_samples))
        train_dataset = Subset(train_dataset, indices)
        print(f"  Capped training to {args.max_samples} samples")

    print(f"  Train: {len(train_dataset):,} samples")
    if eval_dataset:
        print(f"  Eval : {len(eval_dataset):,} samples")

    # ------------------------------------------------------------------
    # 3. Load base model + apply LoRA
    # ------------------------------------------------------------------
    print("[3/5] Loading base model + applying LoRA...")
    adaptor_dir = pair_cfg["adaptor_dir"]

    if args.resume and os.path.isdir(adaptor_dir):
        print(f"  Resuming from {adaptor_dir}")
        base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)
        model = PeftModel.from_pretrained(base_model, adaptor_dir, is_trainable=True)
    else:
        base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)

        # Build LoRA config — gracefully fall back if target modules not found
        lora_cfg = LoraConfig(
            task_type=TaskType.SEQ_2_SEQ_LM,
            r=LORA_CONFIG["r"],
            lora_alpha=LORA_CONFIG["lora_alpha"],
            lora_dropout=LORA_CONFIG["lora_dropout"],
            bias=LORA_CONFIG["bias"],
            target_modules=LORA_CONFIG["target_modules"],
        )
        model = get_peft_model(base_model, lora_cfg)

    model.print_trainable_parameters()

    # ------------------------------------------------------------------
    # 4. Build training arguments
    # ------------------------------------------------------------------
    print("[4/5] Setting up training arguments...")

    # Resolve per-pair overrides, then CLI overrides
    num_epochs  = args.epochs    or pair_cfg.get("num_train_epochs", 5)
    lr          = args.lr        or pair_cfg.get("learning_rate",     3e-4)
    batch_size  = args.batch_size or pair_cfg.get("per_device_train_batch_size", 4)

    os.makedirs(adaptor_dir, exist_ok=True)

    training_args = Seq2SeqTrainingArguments(
        output_dir=adaptor_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=lr,
        warmup_steps=TRAINING_DEFAULTS["warmup_steps"],
        weight_decay=TRAINING_DEFAULTS["weight_decay"],
        eval_strategy="epoch" if (eval_dataset and not args.no_eval) else "no",
        save_strategy="epoch",
        save_total_limit=2,         # keep only the 2 best checkpoints
        load_best_model_at_end=(eval_dataset is not None and not args.no_eval),
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=torch.cuda.is_available() and TRAINING_DEFAULTS["fp16"],
        bf16=False,
        gradient_accumulation_steps=TRAINING_DEFAULTS["gradient_accumulation_steps"],
        dataloader_num_workers=TRAINING_DEFAULTS["dataloader_num_workers"],
        logging_steps=TRAINING_DEFAULTS["logging_steps"],
        seed=TRAINING_DEFAULTS["seed"],
        predict_with_generate=TRAINING_DEFAULTS["predict_with_generate"],
        generation_max_length=TRAINING_DEFAULTS["generation_max_length"],
        report_to="none",   # disable wandb/tensorboard unless you set it up
    )

    # Data collator handles dynamic padding
    data_collator = DataCollatorForSeq2Seq(
        tokenizer, model=model, label_pad_token_id=-100, pad_to_multiple_of=8
    )

    # ------------------------------------------------------------------
    # 5. Train
    # ------------------------------------------------------------------
    print("[5/5] Starting training...\n")

    callbacks = []
    if eval_dataset and not args.no_eval:
        callbacks.append(EarlyStoppingCallback(early_stopping_patience=3))

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if not args.no_eval else None,
        processing_class=tokenizer,
        data_collator=data_collator,
        callbacks=callbacks if callbacks else None,
    )

    trainer.train()

    # ------------------------------------------------------------------
    # Save adaptor weights
    # ------------------------------------------------------------------
    print(f"\nSaving LoRA adaptor to {adaptor_dir} ...")
    model.save_pretrained(adaptor_dir)
    tokenizer.save_pretrained(adaptor_dir)
    print(f"Done. Adaptor saved to: {adaptor_dir}")

    return adaptor_dir


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()
    saved_path = train(args)
    print(f"\nTraining complete. Adaptor: {saved_path}")
