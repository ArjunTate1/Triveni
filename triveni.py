# ============================================================
# TRIVENI - FINAL ALL-IN-ONE VOICE & TEXT TRANSLATOR
# ============================================================
#
# Complete Bidirectional Hindi <-> Mundari Voice & Text Translator
# - Direct Model Inference (Zero SQLite/Database dependency)
# - Outputs saved exclusively in output/text/ and output/audio/
# - Interactive CLI & Full FastAPI Web Application UI (http://localhost:8000)
# ============================================================

# Self-healing virtual environment resolver (cross-platform)
try:
    import torch
except ModuleNotFoundError:
    import os, sys, subprocess
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if os.name == "nt":
        venv_python = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(project_dir, ".venv", "bin", "python")
    if os.path.exists(venv_python) and sys.executable != venv_python:
        print("[Triveni] Switching to configured virtual environment (.venv)...")
        result = subprocess.run([venv_python] + sys.argv)
        sys.exit(result.returncode)
    else:
        print(
            "[Triveni] 'torch' is not installed and no .venv was found.\n"
            "Run: python -m venv .venv && source .venv/bin/activate "
            "(or .venv\\Scripts\\activate on Windows) && pip install -r requirements.txt"
        )
        raise

import os
import sys
import io
import time
import datetime
import shutil
import platform
import subprocess
import threading
import numpy as np
import soundfile as sf

# Force UTF-8 output on Windows only (on POSIX this wrapping is unnecessary
# and can break interactive input()/pipes)
if os.name == "nt":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace",
        line_buffering=True,
    )

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from transformers import (
    AutoProcessor,
    AutoModelForCTC,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    VitsTokenizer,
    VitsModel,
    set_seed,
)
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Microphone recording is optional — sounddevice needs PortAudio installed
# on the host system. The web API and text-mode CLI work without it.
try:
    import sounddevice as sd
    MIC_AVAILABLE = True
except Exception as _mic_err:
    sd = None
    MIC_AVAILABLE = False
    _MIC_IMPORT_ERROR = str(_mic_err)

# ── Paths & Folder Setup ─────────────────────────────────────
PROJECT_DIR      = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR       = os.path.join(PROJECT_DIR, "output")
TEXT_OUTPUT_DIR  = os.path.join(OUTPUT_DIR, "text")
AUDIO_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "audio")

os.makedirs(TEXT_OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

MUNDARI_WAV_LATEST = os.path.join(AUDIO_OUTPUT_DIR, "mundari_latest.wav")
HINDI_WAV_LATEST   = os.path.join(AUDIO_OUTPUT_DIR, "hindi_latest.wav")
INPUT_WAV_TEMP     = os.path.join(AUDIO_OUTPUT_DIR, "input_temp.wav")

# Allow overriding the fine-tuned translation model location via env var so
# this repo doesn't have to ship (or hardcode a path to) the model weights.
TRANSLATION_MODEL_PATH = os.environ.get(
    "TRIVENI_TRANSLATION_MODEL_PATH",
    os.path.join(PROJECT_DIR, "hindi-mundari-final", "content", "hindi-mundari-final"),
)
ASR_MODEL_NAME   = "facebook/mms-1b-all"
TTS_MUNDARI_NAME = "facebook/mms-tts-unr"
TTS_HINDI_NAME   = "facebook/mms-tts-hin"

SAMPLE_RATE = 16000
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

# ── Global Model State ─────────────────────────────────────────
M = {
    "asr_proc":      None,
    "asr_model":     None,
    "trans_tok":     None,
    "trans_model":   None,
    "unr_tts_tok":   None,
    "unr_tts_model": None,
    "hin_tts_tok":   None,
    "hin_tts_model": None,
    "loaded":        False,
    "loading":       False,
    "error":         None,
}


def load_all_models():
    """Load all ASR, Translation, and TTS models directly into memory."""
    if M["loaded"] or M["loading"]:
        return
    M["loading"] = True
    M["error"]   = None
    print(f"\n[Triveni Final] Loading all AI models on device: {DEVICE.upper()}...")

    try:
        # 1. Unified MMS 1B ASR Backbone (Shared for Hindi & Mundari)
        print("[1/4] Loading Shared MMS ASR Backbone (facebook/mms-1b-all)...")
        M["asr_proc"]  = AutoProcessor.from_pretrained(ASR_MODEL_NAME)
        M["asr_model"] = AutoModelForCTC.from_pretrained(ASR_MODEL_NAME).to(DEVICE).eval()

        # 2. Seq2Seq Translation Model (your fine-tuned Hindi<->Mundari model)
        if not os.path.isdir(TRANSLATION_MODEL_PATH):
            raise FileNotFoundError(
                f"Translation model not found at '{TRANSLATION_MODEL_PATH}'.\n"
                "This fine-tuned model is not part of the repo (it's too large for git).\n"
                "Set TRIVENI_TRANSLATION_MODEL_PATH to point at your local copy, "
                "or place it at hindi-mundari-final/content/hindi-mundari-final/."
            )
        print(f"[2/4] Loading Translation Model ({TRANSLATION_MODEL_PATH})...")
        M["trans_tok"]   = AutoTokenizer.from_pretrained(TRANSLATION_MODEL_PATH, local_files_only=True)
        M["trans_model"] = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATION_MODEL_PATH, local_files_only=True).to(DEVICE).eval()

        # 3. Mundari TTS
        print("[3/4] Loading Mundari TTS (MMS)...")
        M["unr_tts_tok"]   = VitsTokenizer.from_pretrained(TTS_MUNDARI_NAME)
        M["unr_tts_model"] = VitsModel.from_pretrained(TTS_MUNDARI_NAME).to(DEVICE).eval()

        # 4. Hindi TTS
        print("[4/4] Loading Hindi TTS (MMS)...")
        M["hin_tts_tok"]   = VitsTokenizer.from_pretrained(TTS_HINDI_NAME)
        M["hin_tts_model"] = VitsModel.from_pretrained(TTS_HINDI_NAME).to(DEVICE).eval()

        M["loaded"]  = True
        M["loading"] = False
        print("[Triveni Final] All models loaded successfully! \u2713\n")

    except Exception as e:
        M["error"]   = str(e)
        M["loading"] = False
        print(f"[Triveni Final] ERROR loading models: {e}")
        raise e


# ── Direct Core Logic (No DB, pure model inference) ───────────

def devanagari_to_odia(text: str) -> str:
    """Convert Devanagari script to Odia script for Mundari TTS."""
    return transliterate(text, sanscript.DEVANAGARI, sanscript.ORIYA).strip()


def run_translation_model(text: str, is_hindi: bool) -> str:
    """Translate text directly using the loaded Seq2Seq model."""
    prefix = "translate Hindi to Mundari: " if is_hindi else "translate Mundari to Hindi: "
    input_str = prefix + text.strip()

    inputs = M["trans_tok"](
        input_str,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        generated = M["trans_model"].generate(
            **inputs,
            max_length=256,
            num_beams=4,
            early_stopping=True,
        )

    translated = M["trans_tok"].decode(generated[0], skip_special_tokens=True).strip()
    return translated


def run_tts(text: str, target_lang: str, out_wav_path: str) -> str:
    """Synthesise audio directly with TTS model and save as WAV."""
    if target_lang.lower() == "mundari":
        tokenizer = M["unr_tts_tok"]
        model     = M["unr_tts_model"]
        tts_input = devanagari_to_odia(text)
    else:
        tokenizer = M["hin_tts_tok"]
        model     = M["hin_tts_model"]
        tts_input = text.strip()

    if not tts_input:
        raise ValueError("TTS input text is empty.")

    inputs = {k: v.to(DEVICE) for k, v in tokenizer(tts_input, return_tensors="pt").items()}
    if inputs["input_ids"].numel() == 0:
        raise ValueError("Tokenizer produced 0 tokens.")

    set_seed(555)
    with torch.no_grad():
        output = model(**inputs)

    waveform = output.waveform[0].detach().cpu().float().numpy()
    max_val  = abs(waveform).max()
    if max_val > 0:
        waveform = waveform / max_val

    sr = model.config.sampling_rate
    sf.write(out_wav_path, waveform, sr, subtype="PCM_16")
    return out_wav_path


def run_asr_with_score(audio_np: np.ndarray, target_lang: str):
    """Run speech recognition directly on audio array with shared MMS backbone."""
    proc  = M["asr_proc"]
    model = M["asr_model"]
    try:
        proc.tokenizer.set_target_lang(target_lang)
        model.load_adapter(target_lang)
    except Exception:
        pass

    inputs = proc(audio_np, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    iv = inputs.input_values.to(DEVICE)
    am = inputs.attention_mask.to(DEVICE) if hasattr(inputs, "attention_mask") else None

    with torch.no_grad():
        logits = model(iv, attention_mask=am).logits if am is not None else model(iv).logits

    log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
    max_log_probs, _ = torch.max(log_probs, dim=-1)
    score = max_log_probs.mean().item()

    ids = torch.argmax(logits, dim=-1)
    text = proc.batch_decode(ids)[0].strip()
    return text, score


def save_history_files(source_lang: str, target_lang: str, source_text: str, target_text: str, audio_path: str = None):
    """Save text translation log to output/text/ and audio to output/audio/."""
    ts_file = time.strftime("%Y%m%d_%H%M%S")
    millis  = int(time.time() * 1000) % 1000
    basename = f"{ts_file}_{millis:03d}_{source_lang.lower()}_to_{target_lang.lower()}"

    # 1. Text Output File
    txt_path = os.path.join(TEXT_OUTPUT_DIR, f"{basename}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
        f.write(f"Source ({source_lang}): {source_text}\n")
        f.write(f"Target ({target_lang}): {target_text}\n")

    # 2. Audio Output File
    if audio_path and os.path.exists(audio_path):
        history_audio = os.path.join(AUDIO_OUTPUT_DIR, f"{basename}.wav")
        shutil.copyfile(audio_path, history_audio)

    return txt_path


def play_audio_file(path: str):
    """Best-effort cross-platform audio playback for the CLI."""
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME)
        elif system == "Darwin":
            subprocess.run(["afplay", path], check=False)
        else:
            # Most Linux desktops have one of these on PATH.
            for player in ("paplay", "aplay", "xdg-open"):
                if shutil.which(player):
                    subprocess.run([player, path], check=False)
                    return
            print(f"(Could not find an audio player; file saved at {path})")
    except Exception as e:
        print(f"(Playback failed: {e}. File saved at {path})")


# ── FastAPI Application Setup ──────────────────────────────────
app = FastAPI(title="Triveni Final Translator", version="4.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/")
def read_root():
    index_path = os.path.join(PROJECT_DIR, "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Triveni Final Translator API operational."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": M["loaded"],
        "loading": M["loading"],
        "device": DEVICE,
        "mic_available": MIC_AVAILABLE,
        "error": M["error"],
    }


@app.post("/load")
def load_endpoint():
    if M["loaded"]:
        return {"status": "already_loaded"}
    load_all_models()
    return {"status": "loaded"}


class TextRequest(BaseModel):
    text: str


@app.post("/translate/auto-text")
def translate_auto_text_api(req: TextRequest):
    if not M["loaded"]:
        load_all_models()
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Text is empty.")

    t0 = time.time()
    dev_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    is_hindi = dev_count > 0

    if is_hindi:
        source_lang, target_lang = "Hindi", "Mundari"
        target_text = run_translation_model(text, is_hindi=True)
        wav_path    = run_tts(target_text, "Mundari", MUNDARI_WAV_LATEST)
        audio_url   = "/audio/mundari"
    else:
        source_lang, target_lang = "Mundari", "Hindi"
        target_text = run_translation_model(text, is_hindi=False)
        wav_path    = run_tts(target_text, "Hindi", HINDI_WAV_LATEST)
        audio_url   = "/audio/hindi"

    save_history_files(source_lang, target_lang, text, target_text, wav_path)

    return {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source_text": text,
        "target_text": target_text,
        "audio_url": audio_url,
        "elapsed_sec": round(time.time() - t0, 2),
    }


@app.post("/translate/auto-audio")
async def translate_auto_audio_api(file: UploadFile = File(...)):
    if not M["loaded"]:
        load_all_models()

    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty audio file.")

    t0 = time.time()
    buf = io.BytesIO(content)
    audio, sr = sf.read(buf)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SAMPLE_RATE:
        import scipy.signal
        audio = scipy.signal.resample(audio, int(len(audio) * SAMPLE_RATE / sr))
    audio_np = audio.astype(np.float32)

    hin_text, hin_score = run_asr_with_score(audio_np, "hin")
    unr_text, unr_score = run_asr_with_score(audio_np, "unr")

    dev_count_hin = sum(1 for c in hin_text if '\u0900' <= c <= '\u097F')
    is_hindi = (dev_count_hin > 0 and hin_score >= (unr_score - 0.4)) or (hin_score > unr_score)

    if not hin_text.strip() and not unr_text.strip():
        raise HTTPException(400, "No clear speech recognized.")

    if is_hindi and hin_text:
        source_lang, target_lang = "Hindi", "Mundari"
        source_text = hin_text.strip()
        target_text = run_translation_model(source_text, is_hindi=True)
        wav_path    = run_tts(target_text, "Mundari", MUNDARI_WAV_LATEST)
        audio_url   = "/audio/mundari"
    else:
        source_lang, target_lang = "Mundari", "Hindi"
        source_text = (unr_text or hin_text).strip()
        target_text = run_translation_model(source_text, is_hindi=False)
        wav_path    = run_tts(target_text, "Hindi", HINDI_WAV_LATEST)
        audio_url   = "/audio/hindi"

    save_history_files(source_lang, target_lang, source_text, target_text, wav_path)

    return {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source_text": source_text,
        "target_text": target_text,
        "audio_url": audio_url,
        "elapsed_sec": round(time.time() - t0, 2),
    }


@app.get("/audio/mundari")
def get_mundari_audio():
    if not os.path.exists(MUNDARI_WAV_LATEST):
        raise HTTPException(404, "No Mundari audio yet.")
    return FileResponse(MUNDARI_WAV_LATEST, media_type="audio/wav", filename="mundari_output.wav")


@app.get("/audio/hindi")
def get_hindi_audio():
    if not os.path.exists(HINDI_WAV_LATEST):
        raise HTTPException(404, "No Hindi audio yet.")
    return FileResponse(HINDI_WAV_LATEST, media_type="audio/wav", filename="hindi_output.wav")


# ── Interactive CLI Loop ───────────────────────────────────────
def run_cli_interactive():
    print()
    print("=" * 70)
    print("TRIVENI - FINAL TRANSLATOR INTERACTIVE CLI")
    print("=" * 70)
    print("Web Interface running at: http://localhost:8000/")
    print()

    while True:
        print("-" * 70)
        print("Select Mode:")
        mic_note = "" if MIC_AVAILABLE else "  (unavailable: no microphone/PortAudio)"
        print(f"  1. Record Hindi from Microphone (6 seconds) -> Mundari Speech{mic_note}")
        print("  2. Type Text Translation (Hindi <-> Mundari)")
        print("  3. Test Mundari TTS Directly")
        print("  4. Quit")
        print("-" * 70)
        choice = input("Enter choice (1-4): ").strip()

        if choice == "4" or choice.lower() == "q":
            print("\nExiting Triveni Final Translator.")
            os._exit(0)

        elif choice == "1":
            if not MIC_AVAILABLE:
                print(f"\nMicrophone recording unavailable: {_MIC_IMPORT_ERROR}")
                print("Install PortAudio (e.g. `apt install portaudio19-dev` / `brew install portaudio`) "
                      "and `pip install sounddevice`, or use option 2 to translate typed text instead.")
                continue
            print("\nRecording Hindi audio for 6 seconds...")
            audio = sd.rec(int(6 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
            sd.wait()
            sf.write(INPUT_WAV_TEMP, audio, SAMPLE_RATE)
            print("Recording saved to:", INPUT_WAV_TEMP)

            # ASR
            audio_read, sr = sf.read(INPUT_WAV_TEMP)
            hindi_text, _ = run_asr_with_score(audio_read.astype(np.float32), "hin")
            print("Recognized Hindi:", hindi_text)

            if not hindi_text.strip():
                print("No speech detected.")
                continue

            # Translation
            mundari_text = run_translation_model(hindi_text, is_hindi=True)
            print("Translated Mundari:", mundari_text)

            # TTS
            wav_path = run_tts(mundari_text, "Mundari", MUNDARI_WAV_LATEST)
            save_history_files("Hindi", "Mundari", hindi_text, mundari_text, wav_path)

            print("Playing Mundari audio output...")
            play_audio_file(wav_path)

        elif choice == "2":
            input_text = input("\nEnter Hindi or Mundari text: ").strip()
            if not input_text:
                continue

            dev_count = sum(1 for c in input_text if '\u0900' <= c <= '\u097F')
            is_hindi  = dev_count > 0

            if is_hindi:
                src_l, tgt_l = "Hindi", "Mundari"
                out_text = run_translation_model(input_text, is_hindi=True)
                wav_path = run_tts(out_text, "Mundari", MUNDARI_WAV_LATEST)
            else:
                src_l, tgt_l = "Mundari", "Hindi"
                out_text = run_translation_model(input_text, is_hindi=False)
                wav_path = run_tts(out_text, "Hindi", HINDI_WAV_LATEST)

            txt_saved = save_history_files(src_l, tgt_l, input_text, out_text, wav_path)
            print(f"\nResult ({src_l} -> {tgt_l}):")
            print(f"Source: {input_text}")
            print(f"Target: {out_text}")
            print(f"Saved Text Log:  {txt_saved}")
            print(f"Saved WAV Audio: {wav_path}")

        elif choice == "3":
            test_sentence = "नेआ नाम हर्ष मेना।"
            print("\nTesting Mundari TTS with sentence:", test_sentence)
            wav_path = run_tts(test_sentence, "Mundari", MUNDARI_WAV_LATEST)
            print("TTS generated:", wav_path)
            play_audio_file(wav_path)

        else:
            print("Invalid choice, please enter 1-4.")


# ── Main Entrypoint ─────────────────────────────────────────────
def main():
    # 1. Load all AI models
    load_all_models()

    # 2. Start Uvicorn FastAPI web server in a background thread
    import uvicorn
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning"),
        daemon=True
    )
    server_thread.start()
    time.sleep(1.5)

    print("\n" + "=" * 70)
    print("TRIVENI FINAL TRANSLATOR SERVER READY AT http://localhost:8000")
    print("=" * 70 + "\n")

    # 3. Run interactive CLI loop in main thread
    run_cli_interactive()


if __name__ == "__main__":
    main()
