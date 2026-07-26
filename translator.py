"""
translator.py — NLLB-200 offline translation engine
Wraps Meta's NLLB-200-distilled-600M for any-to-any translation.
"""

import time
import traceback
from typing import Dict, Any, Optional

from config import NLLB_MODEL_NAME, NLLB_LANGS, LANGUAGE_NAMES, NLLB_TO_ISO


try:
    import spaces
    @spaces.GPU
    def dummy_gpu_func():
        pass
except ImportError:
    pass


class Translator:
    """Offline translation using Meta NLLB-200."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.ready = False
        self.model_name = NLLB_MODEL_NAME

    def load(self):
        """Load the NLLB model and tokenizer."""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

            print(f"[Translator] Loading NLLB model: {self.model_name}...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                local_files_only=True
            )
            print("[Translator] Tokenizer loaded.")

            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                local_files_only=True
            )
            print("[Translator] Model loaded.")

            self.ready = True
            print("[Translator] NLLB ready for translation!")

        except Exception as e:
            print(f"[Translator] ERROR loading NLLB: {e}")
            traceback.print_exc()

            # Try downloading if not available locally
            try:
                print("[Translator] Trying to download model...")
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.ready = True
                print("[Translator] NLLB downloaded and loaded!")
            except Exception as e2:
                print(f"[Translator] Download also failed: {e2}")
                traceback.print_exc()
                self.ready = False

    def translate(self, text: str, source_lang: str, target_lang: str,
                  max_length: int = 512) -> Dict[str, Any]:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: ISO language code (e.g., 'en', 'fr', 'ta')
            target_lang: ISO language code
            max_length: Maximum output token length

        Returns:
            dict with translated text, timing info, etc.
        """
        if not self.ready or self.model is None or self.tokenizer is None:
            return {
                "translated": text,
                "error": "NLLB model not loaded",
                "time_ms": 0
            }

        # Get NLLB codes
        source_nllb = NLLB_LANGS.get(source_lang)
        target_nllb = NLLB_LANGS.get(target_lang)

        if not source_nllb:
            return {
                "translated": text,
                "error": f"Unsupported source language: {source_lang}",
                "time_ms": 0
            }

        if not target_nllb:
            return {
                "translated": text,
                "error": f"Unsupported target language: {target_lang}",
                "time_ms": 0
            }

        # Same language — no translation needed
        if source_lang == target_lang:
            return {
                "translated": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "time_ms": 0,
                "error": None
            }

        try:
            start = time.time()

            # Set source language
            self.tokenizer.src_lang = source_nllb

            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                     max_length=max_length)

            # Get target language token ID
            target_token_id = self.tokenizer.convert_tokens_to_ids(target_nllb)

            # Generate translation
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=target_token_id,
                max_length=max_length
            )

            # Decode
            translated_text = self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0]

            elapsed = round((time.time() - start) * 1000)  # ms

            return {
                "translated": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "source_nllb": source_nllb,
                "target_nllb": target_nllb,
                "time_ms": elapsed,
                "error": None
            }

        except Exception as e:
            print(f"[Translator] Translation error: {e}")
            traceback.print_exc()
            return {
                "translated": text,
                "error": str(e),
                "time_ms": 0
            }

    def get_supported_languages(self) -> Dict[str, str]:
        """Return all supported languages as {code: name}."""
        return dict(sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]))

    def get_language_count(self) -> int:
        """Return the number of supported languages."""
        return len(NLLB_LANGS)

    def is_language_supported(self, lang_code: str) -> bool:
        """Check if a language is supported."""
        return lang_code in NLLB_LANGS
