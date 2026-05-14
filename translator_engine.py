"""
translator_engine.py — Core speech recognition + translation + TTS backend
"""

import io
import os
import time
import threading
import queue
import tempfile
import traceback
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

# Whisper (optional – graceful fallback to Google SR if unavailable)
try:
    import whisper
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init()
    _PYGAME_AVAILABLE = True
except Exception:
    _PYGAME_AVAILABLE = False

from config import WHISPER_MODEL, DEFAULT_ENERGY_THRESHOLD, DEFAULT_PAUSE_THRESHOLD


# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TranslationEntry:
    timestamp: str
    original: str
    translated: str
    source_lang: str
    target_lang: str
    audio_path: Optional[str] = None


@dataclass
class SystemStatus:
    mic_connected: bool = False
    recognizer_ready: bool = False
    translator_ready: bool = False
    audio_engine_ready: bool = False
    internet_ok: bool = False
    is_listening: bool = False
    last_error: str = ""
    last_activity: str = ""


# ─────────────────────────────────────────────────────────────────────────────
class MICTranslatorEngine:
    """
    Continuously captures microphone audio, recognises speech with Whisper /
    Google SR, translates via googletrans, synthesises audio with gTTS, and
    plays back via pygame.
    """

    def __init__(self):
        self.status        = SystemStatus()
        self.history: list[TranslationEntry] = []
        self.history_lock  = threading.Lock()

        self._stop_event   = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None

        self._recognizer   = sr.Recognizer()
        self._translator   = Translator()
        self._whisper_model = None

        self._audio_queue: queue.Queue = queue.Queue(maxsize=5)
        self._audio_thread: Optional[threading.Thread] = None

        # Settings (can be tweaked live from UI)
        self.energy_threshold  = DEFAULT_ENERGY_THRESHOLD
        self.pause_threshold   = DEFAULT_PAUSE_THRESHOLD
        self.tts_slow          = False
        self.autoplay          = True
        self.target_lang_code  = "fr"
        self.target_lang_name  = "French"

        self._init_components()

    # ── Initialisation ────────────────────────────────────────────────────────
    def _init_components(self):
        # Recognizer
        try:
            self._recognizer.energy_threshold = self.energy_threshold
            self._recognizer.pause_threshold  = self.pause_threshold
            self.status.recognizer_ready = True
        except Exception as e:
            self.status.last_error = f"Recognizer init failed: {e}"

        # Translator
        try:
            _ = self._translator.translate("test", dest="en")
            self.status.translator_ready = True
            self.status.internet_ok = True
        except Exception:
            self.status.translator_ready = False
            self.status.internet_ok = False

        # Whisper (lazy load on first use to avoid blocking startup)
        self.status.audio_engine_ready = _PYGAME_AVAILABLE

        # Mic
        try:
            mics = sr.Microphone.list_microphone_names()
            self.status.mic_connected = len(mics) > 0
        except Exception:
            self.status.mic_connected = False

    def load_whisper(self):
        if _WHISPER_AVAILABLE and self._whisper_model is None:
            try:
                self._whisper_model = whisper.load_model(WHISPER_MODEL)
            except Exception as e:
                self.status.last_error = f"Whisper load failed: {e}"

    # ── Public Controls ───────────────────────────────────────────────────────
    def start(self):
        self._stop_event.clear()
        self.status.is_listening = True

        # Audio playback worker
        self._audio_thread = threading.Thread(
            target=self._audio_worker, daemon=True
        )
        self._audio_thread.start()

        # Listening/translation worker
        self._listen_thread = threading.Thread(
            target=self._listen_loop, daemon=True
        )
        self._listen_thread.start()

    def stop(self):
        self._stop_event.set()
        self.status.is_listening = False
        self.status.last_activity = "Translator stopped."

    def is_running(self) -> bool:
        return (
            self._listen_thread is not None
            and self._listen_thread.is_alive()
        )

    def get_history(self) -> list[TranslationEntry]:
        with self.history_lock:
            return list(self.history)

    def update_settings(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self._recognizer.energy_threshold = self.energy_threshold
        self._recognizer.pause_threshold  = self.pause_threshold

    # ── Core Listen Loop ──────────────────────────────────────────────────────
    def _listen_loop(self):
        while not self._stop_event.is_set():
            try:
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    self.status.last_activity = "🎙 Listening…"
                    audio = self._recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=15,
                    )

                self.status.last_activity = "🔍 Recognising speech…"
                original_text = self._recognise(audio)

                if not original_text or len(original_text.strip()) < 2:
                    continue

                self.status.last_activity = "🌐 Translating…"
                translated_text = self._translate(original_text)

                audio_path = None
                if self.autoplay:
                    self.status.last_activity = "🔊 Synthesising audio…"
                    audio_path = self._synthesise(translated_text, self.target_lang_code)
                    if audio_path:
                        self._audio_queue.put_nowait(audio_path)

                entry = TranslationEntry(
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    original=original_text,
                    translated=translated_text,
                    source_lang="auto",
                    target_lang=self.target_lang_name,
                    audio_path=audio_path,
                )
                with self.history_lock:
                    self.history.append(entry)
                    # keep only last 100
                    if len(self.history) > 100:
                        self.history = self.history[-100:]

                self.status.last_activity = (
                    f"✅ Translated at {entry.timestamp}"
                )

            except sr.WaitTimeoutError:
                self.status.last_activity = "⏳ Waiting for speech…"
            except sr.UnknownValueError:
                self.status.last_activity = "❓ Could not understand audio."
            except sr.RequestError as e:
                self.status.last_error  = f"SR API error: {e}"
                self.status.internet_ok = False
                time.sleep(2)
            except OSError as e:
                self.status.last_error      = f"Microphone error: {e}"
                self.status.mic_connected   = False
                time.sleep(2)
            except Exception:
                self.status.last_error = traceback.format_exc(limit=2)
                time.sleep(1)

    # ── Recognition ──────────────────────────────────────────────────────────
    def _recognise(self, audio: sr.AudioData) -> str:
        # Try Whisper first
        if _WHISPER_AVAILABLE:
            try:
                if self._whisper_model is None:
                    self.load_whisper()
                wav_data = audio.get_wav_data()
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as tmp:
                    tmp.write(wav_data)
                    tmp_path = tmp.name
                result = self._whisper_model.transcribe(tmp_path)
                os.unlink(tmp_path)
                return result.get("text", "").strip()
            except Exception as e:
                self.status.last_error = f"Whisper error: {e} — falling back to Google SR"

        # Fallback: Google SR
        try:
            return self._recognizer.recognize_google(audio)
        except Exception as e:
            raise sr.UnknownValueError() from e

    # ── Translation ───────────────────────────────────────────────────────────
    def _translate(self, text: str) -> str:
        try:
            result = self._translator.translate(text, dest=self.target_lang_code)
            self.status.translator_ready = True
            self.status.internet_ok = True
            return result.text
        except Exception as e:
            self.status.last_error = f"Translation failed: {e}"
            self.status.internet_ok = False
            return f"[Translation unavailable] {text}"

    # ── TTS ───────────────────────────────────────────────────────────────────
    def _synthesise(self, text: str, lang: str) -> Optional[str]:
        try:
            tts = gTTS(text=text, lang=lang, slow=self.tts_slow)
            tmp = tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False,
                dir=tempfile.gettempdir()
            )
            tts.save(tmp.name)
            return tmp.name
        except Exception as e:
            self.status.last_error = f"TTS error: {e}"
            return None

    # ── Pygame Audio Worker ───────────────────────────────────────────────────
    def _audio_worker(self):
        while not self._stop_event.is_set():
            try:
                path = self._audio_queue.get(timeout=1)
                self._play_audio(path)
                self._audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.status.last_error = f"Audio worker error: {e}"

    def _play_audio(self, path: str):
        if not _PYGAME_AVAILABLE:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                if self._stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
            time.sleep(0.05)
        except Exception as e:
            self.status.last_error = f"Playback error: {e}"
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass

    # ── One-shot TTS for manual play from UI ─────────────────────────────────
    def play_text(self, text: str, lang_code: str):
        path = self._synthesise(text, lang_code)
        if path:
            t = threading.Thread(
                target=self._play_audio, args=(path,), daemon=True
            )
            t.start()

    def get_audio_bytes(self, text: str, lang_code: str) -> Optional[bytes]:
        """Return mp3 bytes for download without saving to disk."""
        try:
            tts = gTTS(text=text, lang=lang_code, slow=self.tts_slow)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            self.status.last_error = f"TTS export error: {e}"
            return None
