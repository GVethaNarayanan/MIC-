"""
speech.py — Whisper-based offline Speech-to-Text module
Uses OpenAI Whisper (tiny model) for offline speech recognition.
"""

import os
import tempfile
import traceback
from typing import Optional, Dict, Any

import whisper

from config import WHISPER_MODEL


class SpeechRecognizer:
    """Offline speech-to-text using OpenAI Whisper."""

    def __init__(self):
        self.model = None
        self.model_name = WHISPER_MODEL
        self.ready = False

    def load(self):
        """Load the Whisper model."""
        try:
            print(f"[Speech] Loading Whisper '{self.model_name}' model...")
            self.model = whisper.load_model(self.model_name)
            self.ready = True
            print(f"[Speech] Whisper '{self.model_name}' loaded successfully.")
        except Exception as e:
            print(f"[Speech] ERROR loading Whisper: {e}")
            traceback.print_exc()
            self.ready = False

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file (WAV, MP3, etc.)
            language: Optional ISO 639-1 language code to force.
                      If None, Whisper auto-detects the language.

        Returns:
            dict with keys:
                - text: transcribed text
                - language: detected/forced language code
                - confidence: detection confidence (0-1)
                - segments: list of timed segments
        """
        if not self.ready or self.model is None:
            return {
                "text": "",
                "language": None,
                "confidence": 0.0,
                "segments": [],
                "error": "Whisper model not loaded"
            }

        try:
            options = {}
            if language:
                options["language"] = language

            result = self.model.transcribe(audio_path, **options)

            # Extract language detection info
            detected_lang = result.get("language", language or "en")

            # Get detection confidence from the model
            confidence = self._get_language_confidence(audio_path, detected_lang)

            segments = []
            for seg in result.get("segments", []):
                segments.append({
                    "start": round(seg["start"], 2),
                    "end": round(seg["end"], 2),
                    "text": seg["text"].strip()
                })

            return {
                "text": result["text"].strip(),
                "language": detected_lang,
                "confidence": confidence,
                "segments": segments,
                "error": None
            }

        except Exception as e:
            print(f"[Speech] Transcription error: {e}")
            traceback.print_exc()
            return {
                "text": "",
                "language": None,
                "confidence": 0.0,
                "segments": [],
                "error": str(e)
            }

    def transcribe_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe raw audio bytes by saving to a temp file first."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            return self.transcribe(tmp_path, language)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def detect_language(self, audio_path: str) -> Dict[str, Any]:
        """
        Detect the spoken language in an audio file without full transcription.

        Returns:
            dict with language code and confidence scores
        """
        if not self.ready or self.model is None:
            return {"language": None, "confidence": 0.0, "error": "Model not loaded"}

        try:
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            _, probs = self.model.detect_language(mel)

            # Get top 5 languages
            sorted_langs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            top_lang = sorted_langs[0]

            return {
                "language": top_lang[0],
                "confidence": round(top_lang[1], 4),
                "top_5": {k: round(v, 4) for k, v in sorted_langs[:5]},
                "error": None
            }
        except Exception as e:
            return {"language": None, "confidence": 0.0, "error": str(e)}

    def _get_language_confidence(self, audio_path: str, detected_lang: str) -> float:
        """Get confidence score for a detected language."""
        try:
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            _, probs = self.model.detect_language(mel)
            return round(probs.get(detected_lang, 0.0), 4)
        except Exception:
            return 0.0
