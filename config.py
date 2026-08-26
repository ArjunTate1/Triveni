"""
config.py
=========
Central configuration for the Triveni LoRA translation pipeline.

Language pairs handled:
    ht  : Hindi  <-> Mundari (Unr)     — direct dataset
    eh  : English <-> Ho (Hoc)          — direct dataset
    es  : English <-> Santali           — direct dataset
    he  : Hindi  <-> English            — direct dataset (bridge for pivot)

Pivot pipelines (no direct Hindi <-> Ho / Hindi <-> Santali data):
    Hindi -> Ho       : Hindi --[he]--> English --[eh]--> Ho
    Hindi -> Santali  : Hindi --[he]--> English --[es]--> Santali
    Ho    -> Hindi    : Ho    --[eh]--> English --[he]--> Hindi
    Santali -> Hindi  : Santali --[es]--> English --[he]--> Hindi
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = BASE_DIR                          # each pair is a sub-folder
ADAPTORS_DIR  = os.path.join(BASE_DIR, "adaptors")  # saved LoRA weights go here
RESULTS_DIR   = os.path.join(BASE_DIR, "results")   # evaluation results
LOGS_DIR      = os.path.join(BASE_DIR, "logs")      # training logs

# ---------------------------------------------------------------------------
# Base model
# ---------------------------------------------------------------------------
# Helsinki-NLP/opus-mt-mul-en is a good multilingual seq2seq baseline that
# runs on CPU.  Switch to "ai4bharat/indictrans2-indic-en-1B" for production
# (requires GPU). The code is base-model-agnostic — just change this string.
BASE_MODEL = "Helsinki-NLP/opus-mt-mul-en"

# For a lighter test run on CPU use a tiny MarianMT:
# BASE_MODEL = "Helsinki-NLP/opus-mt-en-hi"

# ---------------------------------------------------------------------------
# Per-pair dataset configurations
# ---------------------------------------------------------------------------
PAIR_CONFIGS = {
    # ------------------------------------------------------------------
    # ht : Hindi <-> Mundari (Unr)
    # ------------------------------------------------------------------
    "ht": {
        "name":        "Hindi-Mundari",
        "data_dir":    os.path.join(DATA_DIR, "ht"),
        "direction_a": "hin_unr",          # key in the JSONL translation dict
        "direction_b": "unr_hin",
        "lang_a":      "Hindi",
        "lang_b":      "Mundari",
        "lang_a_code": "hin",
        "lang_b_code": "unr",
        "adaptor_dir": os.path.join(ADAPTORS_DIR, "ht"),
        "num_train_epochs": 5,             # larger dataset — fewer epochs needed
        "per_device_train_batch_size": 4,
        "learning_rate": 3e-4,
        "max_source_length": 128,
        "max_target_length": 128,
    },

    # ------------------------------------------------------------------
    # eh : English <-> Ho (Hoc)
    # ------------------------------------------------------------------
    "eh": {
        "name":        "English-Ho",
        "data_dir":    os.path.join(DATA_DIR, "eh"),
        "direction_a": "eng_hoc",
        "direction_b": "hoc_eng",
        "lang_a":      "English",
        "lang_b":      "Ho",
        "lang_a_code": "eng",
        "lang_b_code": "hoc",
        "adaptor_dir": os.path.join(ADAPTORS_DIR, "eh"),
        "num_train_epochs": 15,            # very small dataset — more epochs
        "per_device_train_batch_size": 4,
        "learning_rate": 1e-4,             # lower LR for small dataset
        "max_source_length": 128,
        "max_target_length": 128,
    },

    # ------------------------------------------------------------------
    # es : English <-> Santali
    # ------------------------------------------------------------------
    "es": {
        "name":        "English-Santali",
        "data_dir":    os.path.join(DATA_DIR, "es"),
        "direction_a": "eng_sat",
        "direction_b": "sat_eng",
        "lang_a":      "English",
        "lang_b":      "Santali",
        "lang_a_code": "eng",
        "lang_b_code": "sat",
        "adaptor_dir": os.path.join(ADAPTORS_DIR, "es"),
        "num_train_epochs": 3,             # largest dataset — 3 epochs fine
        "per_device_train_batch_size": 8,
        "learning_rate": 3e-4,
        "max_source_length": 128,
        "max_target_length": 128,
    },

    # ------------------------------------------------------------------
    # he : Hindi <-> English   (also used as the pivot bridge)
    # ------------------------------------------------------------------
    "he": {
        "name":        "Hindi-English",
        "data_dir":    os.path.join(DATA_DIR, "he"),
        "direction_a": "eng_hin",
        "direction_b": "hin_eng",
        "lang_a":      "English",
        "lang_b":      "Hindi",
        "lang_a_code": "eng",
        "lang_b_code": "hin",
        "adaptor_dir": os.path.join(ADAPTORS_DIR, "he"),
        "num_train_epochs": 10,            # small dataset
        "per_device_train_batch_size": 4,
        "learning_rate": 2e-4,
        "max_source_length": 128,
        "max_target_length": 128,
    },
}

# ---------------------------------------------------------------------------
# Shared LoRA hyperparameters (override per-pair if needed)
# ---------------------------------------------------------------------------
LORA_CONFIG = {
    "r":             16,        # rank — increase to 32 for better quality (more VRAM)
    "lora_alpha":    32,        # scaling factor (alpha / r = 2 is a good ratio)
    "lora_dropout":  0.05,
    "bias":          "none",
    # Modules to inject LoRA into. Works for MarianMT and mBART families.
    # For decoder-only (e.g. LLaMA), add "o_proj", "gate_proj", "up_proj"
    "target_modules": ["q_proj", "v_proj"],
}

# ---------------------------------------------------------------------------
# Training — shared defaults (individual pair values in PAIR_CONFIGS override)
# ---------------------------------------------------------------------------
TRAINING_DEFAULTS = {
    "warmup_steps":              100,
    "weight_decay":              0.01,
    "eval_strategy":             "epoch",
    "save_strategy":             "epoch",
    "load_best_model_at_end":    True,
    "metric_for_best_model":     "eval_loss",
    "fp16":                      False,    # True only with CUDA GPU
    "bf16":                      False,    # True only with Ampere+ GPU
    "gradient_accumulation_steps": 4,      # effective batch = batch * accum
    "dataloader_num_workers":    0,        # 0 = main process (safe on Windows)
    "logging_steps":             50,
    "seed":                      42,
    "predict_with_generate":     True,
    "generation_max_length":     128,
}

# ---------------------------------------------------------------------------
# Pivot routing table
# Used by pipeline.py to resolve a (source_lang, target_lang) pair to a
# sequence of (pair_id, direction_key) steps.
# ---------------------------------------------------------------------------
PIVOT_ROUTES = {
    # Direct routes
    ("hin", "unr"): [("ht", "hin_unr")],
    ("unr", "hin"): [("ht", "unr_hin")],
    ("eng", "hoc"): [("eh", "eng_hoc")],
    ("hoc", "eng"): [("eh", "hoc_eng")],
    ("eng", "sat"): [("es", "eng_sat")],
    ("sat", "eng"): [("es", "sat_eng")],
    ("eng", "hin"): [("he", "eng_hin")],
    ("hin", "eng"): [("he", "hin_eng")],

    # Pivot: Hindi -> Ho  (Hindi->English->Ho)
    ("hin", "hoc"): [("he", "hin_eng"), ("eh", "eng_hoc")],
    # Pivot: Ho -> Hindi  (Ho->English->Hindi)
    ("hoc", "hin"): [("eh", "hoc_eng"), ("he", "eng_hin")],

    # Pivot: Hindi -> Santali  (Hindi->English->Santali)
    ("hin", "sat"): [("he", "hin_eng"), ("es", "eng_sat")],
    # Pivot: Santali -> Hindi  (Santali->English->Hindi)
    ("sat", "hin"): [("es", "sat_eng"), ("he", "eng_hin")],
}

# ---------------------------------------------------------------------------
# Language display names (for prompts and UI)
# ---------------------------------------------------------------------------
LANG_NAMES = {
    "hin": "Hindi",
    "eng": "English",
    "hoc": "Ho",
    "sat": "Santali",
    "unr": "Mundari",
}

# ---------------------------------------------------------------------------
# Prompt template
# Used consistently across training, inference, and evaluation.
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = (
    "Translate the following sentence from {source_lang} to {target_lang}:\n"
    "{source}\n"
    "Translation:"
)
