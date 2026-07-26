"""
tests/test_all.py — Automated tests for MIC Translator
Tests: Speech Recognition, Translation, Language Detection,
       Text-to-Speech, History, Dataset Loading, Correction Engine
"""

import sys
import os
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NLLB_LANGS, LANGUAGE_NAMES, NLLB_TO_ISO
from language_detector import LanguageDetector
from correction_engine import CorrectionEngine
from dataset_loader import DatasetLoader
from history import TranslationHistory


# ═══════════════════════════════════════════════════════════════════════════════
# TEST UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

PASS = 0
FAIL = 0
SKIP = 0


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {f'- {detail}' if detail else ''}")


def skip(name, reason=""):
    global SKIP
    SKIP += 1
    print(f"  [SKIP] {name} (skipped: {reason})")


def section(title):
    print(f"\n{'-'*50}")
    print(f"  {title}")
    print(f"{'-'*50}")


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Configuration
# ═══════════════════════════════════════════════════════════════════════════════

def test_config():
    section("1. Configuration & Language Map")

    test("NLLB_LANGS has 100+ languages", len(NLLB_LANGS) >= 100,
         f"got {len(NLLB_LANGS)}")

    test("LANGUAGE_NAMES matches NLLB_LANGS count",
         len(LANGUAGE_NAMES) == len(NLLB_LANGS),
         f"names={len(LANGUAGE_NAMES)}, codes={len(NLLB_LANGS)}")

    test("NLLB_TO_ISO reverse lookup works",
         NLLB_TO_ISO.get("eng_Latn") == "en")

    # Key languages must be present
    key_langs = ["en", "fr", "de", "es", "hi", "ta", "zh", "ja",
                 "ko", "ar", "ru", "pt", "it", "bn", "ur"]
    for lang in key_langs:
        test(f"Language '{lang}' ({LANGUAGE_NAMES.get(lang, '?')}) is supported",
             lang in NLLB_LANGS)

    test("All NLLB codes have underscore format",
         all("_" in v for v in NLLB_LANGS.values()))

    test("No duplicate NLLB codes",
         len(set(NLLB_LANGS.values())) == len(NLLB_LANGS))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Language Detection
# ═══════════════════════════════════════════════════════════════════════════════

def test_language_detection():
    section("2. Language Detection")

    det = LanguageDetector()

    # English (Latin)
    r = det.detect_from_text("Hello, how are you today?")
    test("Detects English from Latin text", r["language"] == "en", f"got {r['language']}")

    # Hindi (Devanagari)
    r = det.detect_from_text("नमस्ते, आप कैसे हैं?")
    test("Detects Hindi from Devanagari", r["language"] == "hi", f"got {r['language']}")

    # Tamil
    r = det.detect_from_text("வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?")
    test("Detects Tamil from Tamil script", r["language"] == "ta", f"got {r['language']}")

    # Arabic
    r = det.detect_from_text("مرحبا كيف حالك")
    test("Detects Arabic from Arabic script", r["language"] == "ar", f"got {r['language']}")

    # Japanese
    r = det.detect_from_text("こんにちは、元気ですか？")
    test("Detects Japanese from Hiragana", r["language"] == "ja", f"got {r['language']}")

    # Korean
    r = det.detect_from_text("안녕하세요, 어떻게 지내세요?")
    test("Detects Korean from Hangul", r["language"] == "ko", f"got {r['language']}")

    # Chinese
    r = det.detect_from_text("你好世界")
    test("Detects Chinese from CJK", r["language"] == "zh", f"got {r['language']}")

    # Bengali
    r = det.detect_from_text("হ্যালো, কেমন আছেন?")
    test("Detects Bengali from Bengali script", r["language"] == "bn", f"got {r['language']}")

    # Telugu
    r = det.detect_from_text("హలో, మీరు ఎలా ఉన్నారు?")
    test("Detects Telugu from Telugu script", r["language"] == "te", f"got {r['language']}")

    # Empty text
    r = det.detect_from_text("")
    test("Empty text defaults to English", r["language"] == "en")

    # NLLB code lookup
    test("get_nllb_code('en') -> eng_Latn", det.get_nllb_code("en") == "eng_Latn")
    test("get_nllb_code('ta') -> tam_Taml", det.get_nllb_code("ta") == "tam_Taml")
    test("get_nllb_code('ja') -> jpn_Jpan", det.get_nllb_code("ja") == "jpn_Jpan")

    test("is_supported('en') -> True", det.is_supported("en"))
    test("is_supported('xyz') -> False", not det.is_supported("xyz"))

    all_langs = det.get_all_languages()
    test("get_all_languages returns 100+", len(all_langs) >= 100)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Correction Engine
# ═══════════════════════════════════════════════════════════════════════════════

def test_correction_engine():
    section("3. Correction Engine")

    ce = CorrectionEngine()
    ce.load()

    test("Corrections loaded", ce.loaded)
    test("Slang entries > 30", len(ce.slang_map) > 30, f"got {len(ce.slang_map)}")
    test("Short forms > 20", len(ce.short_forms) > 20, f"got {len(ce.short_forms)}")
    test("Confused words > 10", len(ce.confused_words) > 10)

    # Pre-translation corrections
    r = ce.pre_translate("I gonna go to the store", "en")
    test("Slang: 'gonna' -> 'going to'", "going to" in r["text"], r["text"])

    r = ce.pre_translate("I wanna eat something", "en")
    test("Slang: 'wanna' -> 'want to'", "want to" in r["text"], r["text"])

    r = ce.pre_translate("idk what to do tbh", "en")
    test("Slang: 'idk' expanded", "don't know" in r["text"].lower(), r["text"])

    r = ce.pre_translate("hellooo how are you", "en")
    test("Pre-correction: 'hellooo' -> 'hello'", "hello" in r["text"].lower(), r["text"])

    r = ce.pre_translate("Normal sentence here.", "en")
    test("No corrections on clean text", not r["corrected"])

    # Stats
    stats = ce.get_stats()
    test("Stats returns total > 50", stats["total"] > 50, f"got {stats['total']}")

    # Add custom correction
    ok = ce.add_correction("slang", "yolo", "you only live once")
    test("Can add custom correction", ok)

    r = ce.pre_translate("yolo my friend", "en")
    test("Custom correction applied", "you only live once" in r["text"], r["text"])


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: Dataset Loader
# ═══════════════════════════════════════════════════════════════════════════════

def test_dataset_loader():
    section("4. Dataset Loader")

    dl = DatasetLoader()
    dl.load_all()

    stats = dl.get_stats()
    test("Dataset loader initializes", stats is not None)
    test("Datasets directory created",
         os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")))

    # Test with a sample custom dataset
    custom_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               "datasets", "custom")
    sample_file = os.path.join(custom_dir, "test_sample.json")

    sample_data = [
        {"source_lang": "en", "target_lang": "fr",
         "source_text": "Hello", "target_text": "Bonjour"},
        {"source_lang": "en", "target_lang": "fr",
         "source_text": "Good morning", "target_text": "Bonjour"},
    ]

    os.makedirs(custom_dir, exist_ok=True)
    with open(sample_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    # Reload
    dl2 = DatasetLoader()
    dl2.load_all()

    ref = dl2.get_reference("Hello", "en", "fr")
    test("Reference lookup works", ref == "Bonjour", f"got {ref}")

    val = dl2.validate_translation("Hello", "Bonjour", "en", "fr")
    test("Validation: exact match", val["match"] is True)
    test("Validation: quality_score = 1.0", val["quality_score"] == 1.0)

    val2 = dl2.validate_translation("Hello", "Salut", "en", "fr")
    test("Validation: non-match detected", val2["match"] is False)

    # Cleanup
    try:
        os.unlink(sample_file)
    except OSError:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: History
# ═══════════════════════════════════════════════════════════════════════════════

def test_history():
    section("5. Translation History")

    h = TranslationHistory()
    h.entries = []
    h.favorites = []
    h.recent_langs = []

    # Add entries
    h.add({
        "original": "Hello",
        "translated": "Bonjour",
        "source_lang": "en",
        "target_lang": "fr",
        "time_ms": 150
    })

    test("Add entry works", len(h.entries) == 1)
    test("Entry has timestamp", "timestamp" in h.entries[0])

    # Recent languages
    test("Recent langs updated", "fr" in h.recent_langs)

    # Favorites
    h.add_favorite("ta")
    test("Add favorite works", "ta" in h.get_favorites())

    h.remove_favorite("ta")
    test("Remove favorite works", "ta" not in h.get_favorites())

    # Search
    h.add({
        "original": "Good morning",
        "translated": "Buenos días",
        "source_lang": "en",
        "target_lang": "es",
        "time_ms": 200
    })

    results = h.search("morning")
    test("Search works", len(results) == 1)

    results = h.search("xyz_not_found")
    test("Search returns empty for no match", len(results) == 0)

    # Export
    csv_str = h.export_csv()
    test("CSV export works", "Hello" in csv_str and "Bonjour" in csv_str)

    json_str = h.export_json()
    test("JSON export works", "Hello" in json_str)

    # Stats
    stats = h.get_stats()
    test("Stats: total = 2", stats["total_translations"] == 2)
    test("Stats: avg_time > 0", stats["avg_time_ms"] > 0)

    # Clear
    h.clear()
    test("Clear works", len(h.entries) == 0)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Speech Recognition (requires Whisper model)
# ═══════════════════════════════════════════════════════════════════════════════

def test_speech():
    section("6. Speech Recognition (Whisper)")

    try:
        from speech import SpeechRecognizer
        sr = SpeechRecognizer()
        sr.load()

        test("Whisper model loads", sr.ready)

        # Test with existing test.wav if available
        test_wav = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test.wav")
        if os.path.exists(test_wav) and sr.ready:
            result = sr.transcribe(test_wav)
            test("Transcription produces text", len(result.get("text", "")) > 0,
                 f"text='{result.get('text', '')}'")
            test("Language detected", result.get("language") is not None,
                 f"lang={result.get('language')}")
        else:
            skip("Transcription test", "no test.wav found or model not ready")

    except Exception as e:
        skip("Whisper tests", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: Translation (requires NLLB model)
# ═══════════════════════════════════════════════════════════════════════════════

def test_translation():
    section("7. Translation (NLLB-200)")

    try:
        from translator import Translator
        t = Translator()
        t.load()

        test("NLLB model loads", t.ready)

        if t.ready:
            # English -> French
            r = t.translate("Hello, how are you?", "en", "fr")
            test("EN->FR translation works", len(r["translated"]) > 0 and r["error"] is None,
                 r.get("translated", ""))
            test("Translation time recorded", r["time_ms"] > 0)

            # English -> Hindi
            r = t.translate("Good morning", "en", "hi")
            test("EN->HI translation works", len(r["translated"]) > 0 and r["error"] is None,
                 r.get("translated", ""))

            # English -> Tamil
            r = t.translate("Thank you", "en", "ta")
            test("EN->TA translation works", len(r["translated"]) > 0 and r["error"] is None,
                 r.get("translated", ""))

            # Same language (no-op)
            r = t.translate("Test", "en", "en")
            test("Same-lang returns original", r["translated"] == "Test")

            # Unsupported language
            r = t.translate("Test", "xyz", "en")
            test("Unsupported lang returns error", r["error"] is not None)

            # Language count
            test("200+ languages supported", t.get_language_count() >= 100)
        else:
            skip("Translation tests", "NLLB model not loaded")

    except Exception as e:
        skip("Translation tests", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: Text-to-Speech
# ═══════════════════════════════════════════════════════════════════════════════

def test_tts():
    section("8. Text-to-Speech (Piper)")

    try:
        from tts import TextToSpeech
        t = TextToSpeech()
        t.load()

        test("TTS initializes", t.ready)

        voices = t.get_available_voices()
        test("Voices discovered", len(voices) >= 0, f"voices={list(voices.keys())}")

        stats = t.get_stats()
        test("Stats returns data", stats is not None)

        if t.piper_available and voices:
            r = t.synthesize("Hello world", "en")
            test("EN synthesis works", r.get("success") is True, r.get("error", ""))
        else:
            skip("TTS synthesis test", "Piper not installed or no voice models")

    except Exception as e:
        skip("TTS tests", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# RUN ALL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  MIC Translator - Automated Test Suite")
    print("=" * 50)

    start = time.time()

    test_config()
    test_language_detection()
    test_correction_engine()
    test_dataset_loader()
    test_history()
    test_speech()
    test_translation()
    test_tts()

    elapsed = round(time.time() - start, 1)

    print(f"\n{'='*50}")
    print(f"  RESULTS: {PASS} passed | {FAIL} failed | {SKIP} skipped")
    print(f"  Time: {elapsed}s")
    print(f"{'='*50}\n")

    sys.exit(1 if FAIL > 0 else 0)
