---
title: Mic Translator
emoji: 🌍
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
---

# MIC Translator – Offline AI-Powered Real-Time Multilingual Voice Translation System


MIC Translator v3.0 is a production-grade, modular translation system. It performs high-precision voice transcription, text correction, automatic source language detection, offline/online hybrid text-to-speech synthesis, and multi-language translation entirely on your local machine.

---

## 🚀 Quick Start

### Step 1 — Install Dependencies
Run the install batch script to set up packages (Flask, Whisper, NLLB-200, Piper support, and dependencies):
```bat
install.bat
```

### Step 2 — Start the Translation Dashboard
Launch the server:
```bat
run_dashboard.bat
```
Then open your web browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 📁 Modular Project Structure

```
MIC dashboard/
├── app.py                  ← Clean Flask router (routes & endpoints)
├── config.py               ← App configuration & NLLB-200 language mapping
├── speech.py               ← Offline Speech-to-Text (OpenAI Whisper)
├── translator.py           ← Offline Translation Engine (Meta NLLB-200)
├── language_detector.py    ← Offline language script analysis
├── correction_engine.py    ← Real-time slang/short-form/spoken-word correction pipeline
├── dataset_loader.py       ← FLORES, OPUS, Tatoeba, and custom dataset manager
├── history.py              ← Saved translations, favorites, CSV/JSON exports, and analytics
├── tts.py                  ← Hybrid TTS (Offline Piper + Online gTTS fallback)
├── static/
│   ├── app.js              ← Searchable selection, recorder, history, & status polling
│   └── style.css           ← Premium dark mode user interface
├── templates/
│   └── index.html          ← Main dashboard markup
├── datasets/
│   ├── custom/             ← Directory for custom parallel translation files (JSON/CSV)
│   └── corrections.json    ← 180+ pre & post-translation correction dictionary rules
├── tests/
│   └── test_all.py         ← 80-test verification suite
└── README.md
```

---

## 🎙️ Core Pipelines

```
Voice Speech
     ↓
OpenAI Whisper (Offline STT)
     ↓
Correction Engine (Pre-translation cleanup: slang, abbreviations)
     ↓
Language Detector (Script/Heuristic auto-detection)
     ↓
Meta NLLB-200 (Offline Translation)
     ↓
Correction Engine (Post-translation refinement)
     ↓
TTS Engine (Offline Piper Voice -> fall back to gTTS Online)
```

---

## ⚙️ Requirements & Offline Compatibility

* **Python:** Version 3.9 or higher
* **FFmpeg:** Required for offline Whisper audio processing ([Download FFmpeg](https://ffmpeg.org/download.html)) and added to your system's `PATH`.
* **Microphone:** Built-in or external mic.
* **Fully Offline Support:** 
  * **Speech Recognition:** 100% Offline (Whisper base model).
  * **Translation:** 100% Offline (NLLB-Distilled-600M).
  * **Text-to-Speech:** Offline voice synthesis is configured for **English (`en`)** and **Hindi (`hi`)** using local Piper ONNX files.
  * **Adding Offline Voices:** To speak other languages offline, download `.onnx` and `.json` model files from the [Piper Repository](https://huggingface.co/rhasspy/piper-voices/tree/main) and drop them inside the `voices/` directory. If a local model is not present, the system automatically uses the online `gTTS` fallback to speak.

---

## 🧪 Verification

Run the automated test suite to verify configuration, translation, history caching, script detection, and corrector pipeline components:
```bash
python tests/test_all.py
```

*Built for high-performance offline voice and text translation.*
