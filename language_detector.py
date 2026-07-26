"""
language_detector.py — Automatic source language detection
Uses Whisper's built-in language detection + text-based heuristics.
"""

import re
from typing import Optional, Dict, Any

from config import NLLB_LANGS, LANGUAGE_NAMES, NLLB_TO_ISO


class LanguageDetector:
    """Detect source language from text or delegate to Whisper for audio."""

    # Unicode script ranges for text-based detection
    SCRIPT_PATTERNS = {
        "hi":  re.compile(r'[\u0900-\u097F]'),    # Devanagari
        "ta":  re.compile(r'[\u0B80-\u0BFF]'),    # Tamil
        "te":  re.compile(r'[\u0C00-\u0C7F]'),    # Telugu
        "kn":  re.compile(r'[\u0C80-\u0CFF]'),    # Kannada
        "ml":  re.compile(r'[\u0D00-\u0D7F]'),    # Malayalam
        "bn":  re.compile(r'[\u0980-\u09FF]'),    # Bengali
        "gu":  re.compile(r'[\u0A80-\u0AFF]'),    # Gujarati
        "pa":  re.compile(r'[\u0A00-\u0A7F]'),    # Gurmukhi (Punjabi)
        "or":  re.compile(r'[\u0B00-\u0B7F]'),    # Odia
        "si":  re.compile(r'[\u0D80-\u0DFF]'),    # Sinhala
        "my":  re.compile(r'[\u1000-\u109F]'),    # Myanmar
        "th":  re.compile(r'[\u0E00-\u0E7F]'),    # Thai
        "lo":  re.compile(r'[\u0E80-\u0EFF]'),    # Lao
        "km":  re.compile(r'[\u1780-\u17FF]'),    # Khmer
        "bo":  re.compile(r'[\u0F00-\u0FFF]'),    # Tibetan
        "ka":  re.compile(r'[\u10A0-\u10FF]'),    # Georgian
        "hy":  re.compile(r'[\u0530-\u058F]'),    # Armenian
        "he":  re.compile(r'[\u0590-\u05FF]'),    # Hebrew
        "ar":  re.compile(r'[\u0600-\u06FF]'),    # Arabic
        "ja":  re.compile(r'[\u3040-\u309F\u30A0-\u30FF]'),  # Hiragana/Katakana
        "zh":  re.compile(r'[\u4E00-\u9FFF]'),    # CJK Unified
        "ko":  re.compile(r'[\uAC00-\uD7AF]'),    # Hangul
        "el":  re.compile(r'[\u0370-\u03FF]'),    # Greek
        "ru":  re.compile(r'[\u0400-\u04FF]'),    # Cyrillic (default Russian)
        "am":  re.compile(r'[\u1200-\u137F]'),    # Ethiopic (Amharic/Tigrinya)
    }

    def detect_from_text(self, text: str) -> Dict[str, Any]:
        """
        Detect language from text using Unicode script analysis.

        Returns:
            dict with 'language' (ISO code), 'confidence', 'method'
        """
        if not text or not text.strip():
            return {"language": "en", "confidence": 0.0, "method": "default"}

        text = text.strip()

        # Count characters matching each script
        script_scores = {}
        total_alpha = 0

        for lang, pattern in self.SCRIPT_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                script_scores[lang] = len(matches)
                total_alpha += len(matches)

        # Count Latin characters
        latin_count = len(re.findall(r'[a-zA-Z]', text))
        total_alpha += latin_count

        if total_alpha == 0:
            return {"language": "en", "confidence": 0.0, "method": "default"}

        # If non-Latin script dominates
        if script_scores:
            top_lang = max(script_scores, key=script_scores.get)
            top_score = script_scores[top_lang]

            if top_score > latin_count:
                confidence = round(top_score / total_alpha, 4)
                return {
                    "language": top_lang,
                    "confidence": confidence,
                    "method": "script_analysis"
                }

        # Default to English for Latin script
        if latin_count > 0:
            return {
                "language": "en",
                "confidence": round(latin_count / total_alpha, 4),
                "method": "latin_default"
            }

        return {"language": "en", "confidence": 0.0, "method": "fallback"}

    def get_nllb_code(self, iso_code: str) -> Optional[str]:
        """Convert ISO language code to NLLB Flores-200 code."""
        return NLLB_LANGS.get(iso_code)

    def get_iso_code(self, nllb_code: str) -> Optional[str]:
        """Convert NLLB Flores-200 code to ISO language code."""
        return NLLB_TO_ISO.get(nllb_code)

    def get_language_name(self, iso_code: str) -> str:
        """Get human-readable language name from ISO code."""
        return LANGUAGE_NAMES.get(iso_code, iso_code)

    def is_supported(self, iso_code: str) -> bool:
        """Check if a language code is supported by NLLB."""
        return iso_code in NLLB_LANGS

    def get_all_languages(self) -> Dict[str, str]:
        """Return all supported languages as {code: name} dict, sorted by name."""
        return dict(sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]))
