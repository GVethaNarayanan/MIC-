# MIC Translator Dashboard

> AI-Powered Real-Time Multilingual Voice Translation System

---

## 🚀 Quick Start

### Step 1 — Install Dependencies
```bat
install.bat
```
This installs all Python packages including Whisper, SpeechRecognition, gTTS, pygame, and googletrans.

### Step 2 — Launch the Dashboard
```bat
run_dashboard.bat
```
Then open: **http://localhost:8501**

---

## 📁 Project Structure

```
MIC dashboard/
├── app.py                  ← Streamlit dashboard (main entry point)
├── translator_engine.py    ← Core AI backend (SR + Translation + TTS + Audio)
├── config.py               ← Languages map + app constants
├── styles.py               ← Injected CSS (dark AI theme)
├── requirements.txt        ← Python dependencies
├── install.bat             ← One-click installer (Windows)
├── run_dashboard.bat       ← One-click launcher (Windows)
├── .streamlit/
│   └── config.toml         ← Streamlit theme + server config
└── README.md
```

---

## 🎙 Features

| Feature | Technology |
|---|---|
| Speech Recognition | Whisper AI (with Google SR fallback) |
| Translation Engine | googletrans (Google Translate API) |
| Text-to-Speech | gTTS (Google TTS) |
| Audio Playback | pygame.mixer |
| Dashboard | Streamlit |
| 90+ Languages | Google Translate language codes |

---

## ⚙️ Requirements

- **Python** 3.9 or higher
- **FFmpeg** — required for Whisper AI ([download here](https://ffmpeg.org/download.html))
  - Add `ffmpeg/bin` to your system PATH
  - Without FFmpeg, the app falls back to Google Speech Recognition
- **Microphone** — any USB or built-in mic
- **Internet** — for translation API and gTTS

---

## 🌐 Supported Languages (90+)

The app dynamically supports all Google Translate languages including:
- English, Hindi, French, German, Spanish, Italian
- Arabic, Chinese (Simplified/Traditional), Japanese, Korean
- Portuguese, Russian, Ukrainian, Polish, Turkish
- And 75+ more — selectable from the sidebar dropdown

---

## 🔧 Settings (Sidebar)

| Setting | Description |
|---|---|
| Target Language | Select from 90+ languages |
| Mic Sensitivity | Energy threshold (50–3000) |
| Pause Threshold | Silence before phrase ends (0.3–3.0s) |
| Slow TTS | Slower speech synthesis |
| Auto-Play Audio | Automatically play translated audio |

---

## 🛠 Troubleshooting

| Issue | Fix |
|---|---|
| `PyAudio` install fails | Run `pip install pipwin` then `pipwin install pyaudio` |
| Whisper not available | App auto-falls back to Google SR |
| No audio playback | Check pygame install; system audio must be available |
| Translation fails | Check internet connection |
| Mic not detected | Check OS mic permissions + select correct device |

---

## 📊 Workflow

```
Microphone Input
    ↓
Speech Recognition (Whisper AI / Google SR)
    ↓
Real-Time Translation (googletrans)
    ↓
Text-to-Speech (gTTS)
    ↓
Audio Playback (pygame)
    ↓
Live Dashboard Display (Streamlit)
```

---
redeploy update
*Built for enterprise multilingual communication demos.*
