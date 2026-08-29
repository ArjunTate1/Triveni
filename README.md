# Triveni — Hindi ⇄ Mundari Voice & Text Translator

Bidirectional Hindi ↔ Mundari translator with speech recognition (ASR), a
fine-tuned Seq2Seq translation model, and text-to-speech (TTS). Runs as a
FastAPI web app (`http://localhost:8000`) plus an interactive CLI, with no
database — everything is direct model inference, and outputs are written to
`output/text/` and `output/audio/`.

## Requirements

- Python 3.10+
- A GPU is optional (falls back to CPU automatically)
- Your fine-tuned Hindi↔Mundari translation model (not included in this repo
  — see below)
- For microphone recording (CLI option 1) only: PortAudio installed on the
  system (`apt install portaudio19-dev` on Debian/Ubuntu, `brew install
  portaudio` on macOS). Not required for the web API or typed-text mode.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Translation model

The fine-tuned Hindi↔Mundari Seq2Seq model is not committed to this repo
(it's a trained-weights artifact, not source code). Place it at:

```
hindi-mundari-final/content/hindi-mundari-final/
```

or point the app at wherever it lives:

```bash
export TRIVENI_TRANSLATION_MODEL_PATH=/path/to/your/model
```

The ASR backbone (`facebook/mms-1b-all`) and both TTS models
(`facebook/mms-tts-hin`, `facebook/mms-tts-unr`) download automatically from
the Hugging Face Hub on first run.

### Run

```bash
python triveni.py
```

This starts the API at `http://localhost:8000` in a background thread and
drops you into an interactive CLI in the same terminal.

## API

- `GET /health` — model load status
- `POST /load` — force model loading
- `POST /translate/auto-text` — `{"text": "..."}` → detects Hindi vs Mundari,
  translates, and synthesizes speech
- `POST /translate/auto-audio` — multipart audio upload → same pipeline via ASR
- `GET /audio/mundari` / `GET /audio/hindi` — latest synthesized WAV

## Integrating into a larger project

This is a standalone FastAPI service, so the simplest integration is to run
it as its own process/container and call its HTTP API from the main project
(or mount `app` from `triveni.py` as a sub-application of a larger FastAPI
app via `main_app.mount("/triveni", app)`).

## Notes on what changed from the original script

- Cross-platform fixes: the `.venv` auto-relaunch, audio playback, and
  UTF-8 stdout wrapping all previously assumed Windows; they now degrade
  gracefully on Linux/macOS.
- Microphone recording is now optional at import time, so the app (and the
  web API in particular) still runs on machines without PortAudio.
- The translation model path can be overridden via
  `TRIVENI_TRANSLATION_MODEL_PATH`, and a clear error is raised if it's
  missing, instead of an opaque `transformers` stack trace.
