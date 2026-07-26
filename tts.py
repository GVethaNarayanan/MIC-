"""
tts.py — Text-to-Speech module using Piper (offline)
Falls back to a simple beep/notification if no voice model is available.
"""

import os
import subprocess
import uuid
from typing import Optional, Dict, Any, List

from config import PIPER_VOICES, VOICES_DIR


class TextToSpeech:
    """Offline text-to-speech using Piper ONNX voice models."""

    def __init__(self):
        self.voices = {}
        self.audio_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "static", "audio"
        )
        self.piper_available = False
        self.ready = False

    def load(self):
        """Initialize TTS engine and discover available voices."""
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(VOICES_DIR, exist_ok=True)

        # Check if Piper is installed
        self.piper_available = self._check_piper()

        # Discover available voice models
        self._discover_voices()

        self.ready = True
        print(f"[TTS] Ready. Piper: {self.piper_available}, "
              f"Voices: {len(self.voices)}")

    def synthesize(self, text: str, lang_code: str = "en") -> Dict[str, Any]:
        """
        Convert text to speech audio file.
        Uses offline Piper if voice model is available, otherwise falls back to online gTTS.

        Args:
            text: Text to synthesize
            lang_code: ISO language code

        Returns:
            dict with audio_url, file_path, and metadata
        """
        if not text or not text.strip():
            return {"error": "No text provided", "success": False}

        os.makedirs(self.audio_dir, exist_ok=True)

        # Find the best voice model for this language
        model_path = self._get_voice_model(lang_code)

        is_offline = False
        if model_path and self.piper_available:
            filename = f"{uuid.uuid4()}.wav"
            audio_path = os.path.join(self.audio_dir, filename)
            result = self._synthesize_piper(text, model_path, audio_path)
            is_offline = True
        else:
            filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(self.audio_dir, filename)
            result = self._synthesize_gtts(text, lang_code, audio_path)

        if result["success"] and os.path.exists(audio_path):
            return {
                "success": True,
                "audio_url": f"/static/audio/{filename}",
                "file_path": audio_path,
                "voice_model": os.path.basename(model_path) if is_offline else "Google TTS (Online Fallback)",
                "lang_code": lang_code,
                "is_offline": is_offline,
                "error": None
            }
        else:
            return result

    def _synthesize_gtts(self, text: str, lang_code: str, output_path: str) -> Dict[str, Any]:
        """Synthesize using gTTS (online fallback)."""
        try:
            from gtts import gTTS
            # Map NLLB/common codes to gTTS standard codes
            gtts_lang = lang_code
            if lang_code == "zht":
                gtts_lang = "zh-TW"
            elif lang_code == "zh":
                gtts_lang = "zh-CN"
            
            tts_engine = gTTS(text=text, lang=gtts_lang, slow=False)
            tts_engine.save(output_path)
            return {"success": True, "error": None}
        except Exception as e:
            return {
                "success": False,
                "error": f"Offline Piper model not found for '{lang_code}', and online gTTS fallback failed: {e}"
            }

    def _synthesize_piper(self, text: str, model_path: str,
                          output_path: str) -> Dict[str, Any]:
        """Synthesize using Piper TTS."""
        try:
            # Write text to temp file (handles Unicode)
            temp_txt = os.path.join(self.audio_dir, "temp_tts.txt")
            with open(temp_txt, "w", encoding="utf-8") as f:
                f.write(text)

            result = subprocess.run(
                ["piper", "-m", model_path, "-f", output_path, "-i", temp_txt],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Cleanup temp file
            try:
                os.unlink(temp_txt)
            except OSError:
                pass

            if result.returncode == 0 and os.path.exists(output_path):
                return {"success": True, "error": None}
            else:
                return {
                    "success": False,
                    "error": f"Piper error: {result.stderr or 'Unknown error'}"
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "TTS timed out (30s)"}
        except FileNotFoundError:
            return {"success": False, "error": "Piper not found. Install Piper TTS."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_voice_model(self, lang_code: str) -> Optional[str]:
        """Find the best Piper voice model for a language."""
        # Direct match
        if lang_code in self.voices:
            return self.voices[lang_code]

        # Fallback to English
        if "en" in self.voices:
            return self.voices["en"]

        return None

    def _discover_voices(self):
        """Scan voices/ directory for available ONNX models."""
        self.voices = {}

        if not os.path.exists(VOICES_DIR):
            return

        # Load configured voices
        for lang, model_file in PIPER_VOICES.items():
            model_path = os.path.join(VOICES_DIR, model_file)
            if os.path.exists(model_path):
                self.voices[lang] = model_path

        # Auto-discover additional ONNX models by filename convention
        # Expected format: {lang_code}_{country}-{name}-{quality}.onnx
        for filename in os.listdir(VOICES_DIR):
            if filename.endswith(".onnx"):
                model_path = os.path.join(VOICES_DIR, filename)
                # Try to extract language code from filename
                parts = filename.split("_")
                if len(parts) >= 1:
                    lang = parts[0].lower()
                    if lang not in self.voices:
                        self.voices[lang] = model_path

        if self.voices:
            print(f"[TTS] Discovered voices: {list(self.voices.keys())}")

    def _check_piper(self) -> bool:
        """Check if Piper TTS is installed and accessible."""
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_available_voices(self) -> Dict[str, str]:
        """Return available voice models as {lang_code: model_file}."""
        return {k: os.path.basename(v) for k, v in self.voices.items()}

    def get_stats(self) -> Dict[str, Any]:
        """Return TTS statistics."""
        return {
            "piper_available": self.piper_available,
            "voice_count": len(self.voices),
            "voices": self.get_available_voices(),
            "ready": self.ready
        }

    def cleanup_old_audio(self, max_files: int = 100):
        """Remove old audio files to save disk space."""
        try:
            files = []
            for f in os.listdir(self.audio_dir):
                if f.endswith((".wav", ".mp3")) and f != "temp_tts.txt":
                    path = os.path.join(self.audio_dir, f)
                    files.append((path, os.path.getmtime(path)))

            files.sort(key=lambda x: x[1])

            while len(files) > max_files:
                old_file = files.pop(0)
                try:
                    os.unlink(old_file[0])
                except OSError:
                    pass
        except Exception:
            pass
