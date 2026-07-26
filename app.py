"""
app.py — MIC Translator Flask Backend
Clean routing layer using modular components.
"""

import os
import time
import traceback
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from config import APP_TITLE, APP_VERSION, LANGUAGE_NAMES, NLLB_LANGS
from speech import SpeechRecognizer
from translator import Translator
from language_detector import LanguageDetector
from correction_engine import CorrectionEngine
from dataset_loader import DatasetLoader
from tts import TextToSpeech
from history import TranslationHistory

# ═══════════════════════════════════════════════════════════════════════════════
# FLASK SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZE MODULES
# ═══════════════════════════════════════════════════════════════════════════════

speech = SpeechRecognizer()
translator = Translator()
detector = LanguageDetector()
corrector = CorrectionEngine()
datasets = DatasetLoader()
tts = TextToSpeech()
history = TranslationHistory()

def init_modules():
    """Load all modules at startup."""
    print(f"\n{'='*50}")
    print(f"  {APP_TITLE} {APP_VERSION}")
    print(f"  Initializing modules...")
    print(f"{'='*50}\n")

    speech.load()
    translator.load()
    corrector.load()
    datasets.load_all()
    tts.load()
    history.load()

    lang_count = len(NLLB_LANGS)
    print(f"\n{'='*50}")
    print(f"  [OK] All modules loaded!")
    print(f"  Languages: {lang_count} supported")
    print(f"  Corrections: {corrector.get_stats()['total']} loaded")
    print(f"  Datasets: {datasets.get_stats()['total_pairs']} pairs loaded")
    print(f"  Voices: {len(tts.get_available_voices())} voice models")
    print(f"{'='*50}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Pages
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/test")
def api_test():
    return jsonify({"success": True, "message": "Backend working"})


@app.route("/api/status")
def api_status():
    return jsonify({
        "whisper_ready": speech.ready,
        "translator_ready": translator.ready,
        "tts_ready": tts.ready,
        "corrections_loaded": corrector.loaded,
        "language_count": len(NLLB_LANGS),
        "voice_count": len(tts.get_available_voices()),
        "dataset_stats": datasets.get_stats(),
        "correction_stats": corrector.get_stats(),
        "version": APP_VERSION
    })


# ── Languages ────────────────────────────────────────────────────────────────

@app.route("/api/languages")
def api_languages():
    """Return all supported languages with metadata."""
    languages = {}
    for code, name in sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]):
        languages[code] = {
            "name": name,
            "nllb_code": NLLB_LANGS.get(code, ""),
            "has_voice": code in tts.get_available_voices()
        }
    return jsonify(languages)


@app.route("/api/languages/favorites")
def api_get_favorites():
    return jsonify({
        "favorites": history.get_favorites(),
        "recent": history.get_recent_langs()
    })


@app.route("/api/languages/favorites", methods=["POST"])
def api_set_favorite():
    data = request.get_json()
    action = data.get("action", "add")
    lang = data.get("lang_code", "")

    if action == "add":
        history.add_favorite(lang)
    elif action == "remove":
        history.remove_favorite(lang)

    return jsonify({"success": True, "favorites": history.get_favorites()})


# ── Transcribe (Speech-to-Text) ──────────────────────────────────────────────

@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    """Transcribe audio to text using Whisper."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    source_lang = request.form.get("source_lang", None)

    # Don't force language if "auto" is selected
    if source_lang == "auto":
        source_lang = None

    temp_file = "temp_audio.wav"
    try:
        audio.save(temp_file)
        result = speech.transcribe(temp_file, language=source_lang)

        # Apply pre-translation corrections
        if result.get("text"):
            detected_lang = result.get("language", "en")
            correction = corrector.pre_translate(result["text"], detected_lang)
            result["corrected_text"] = correction["text"]
            result["corrections"] = correction["corrections"]
            result["correction_count"] = correction["correction_count"]
        else:
            result["corrected_text"] = ""
            result["corrections"] = []
            result["correction_count"] = 0

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except OSError:
                pass


# ── Translate ────────────────────────────────────────────────────────────────

@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    Full translation pipeline:
    Text → Pre-correction → Language Detection → NLLB Translation
    → Post-correction → Validation → History → Response
    """
    data = request.get_json()
    text = data.get("text", "").strip()
    source_lang = data.get("source_lang", "auto")
    target_lang = data.get("target_lang", "en")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    pipeline_start = time.time()

    # 1. Detect source language if "auto"
    if source_lang == "auto":
        detection = detector.detect_from_text(text)
        source_lang = detection["language"]
        detection_confidence = detection["confidence"]
        detection_method = detection["method"]
    else:
        detection_confidence = 1.0
        detection_method = "manual"

    # 2. Pre-translation correction
    pre_result = corrector.pre_translate(text, source_lang)
    corrected_text = pre_result["text"]

    # 3. NLLB Translation
    trans_result = translator.translate(corrected_text, source_lang, target_lang)
    translated_text = trans_result.get("translated", corrected_text)

    # 4. Post-translation correction
    post_result = corrector.post_translate(translated_text, source_lang, target_lang)
    final_text = post_result["text"]

    # 5. Validate against datasets (if available)
    validation = datasets.validate_translation(
        text, final_text, source_lang, target_lang
    )

    total_time = round((time.time() - pipeline_start) * 1000)

    # 6. Build response
    result = {
        "original": text,
        "corrected": corrected_text,
        "translated": final_text,
        "source_lang": source_lang,
        "source_lang_name": LANGUAGE_NAMES.get(source_lang, source_lang),
        "target_lang": target_lang,
        "target_lang_name": LANGUAGE_NAMES.get(target_lang, target_lang),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "time_ms": total_time,
        "translation_time_ms": trans_result.get("time_ms", 0),
        "detection": {
            "language": source_lang,
            "confidence": detection_confidence,
            "method": detection_method
        },
        "pre_corrections": pre_result["corrections"],
        "post_corrections": post_result["corrections"],
        "validation": validation,
        "error": trans_result.get("error")
    }

    # 7. Save to history
    history.add(result)

    return jsonify(result)


# ── Text-to-Speech ───────────────────────────────────────────────────────────

@app.route("/api/tts", methods=["POST"])
def api_tts():
    """Convert text to speech using Piper (offline)."""
    data = request.get_json()
    text = data.get("text", "").strip()
    lang_code = data.get("lang_code", "en")

    if not text:
        return jsonify({"error": "No text"}), 400

    result = tts.synthesize(text, lang_code)

    # Cleanup old files periodically
    tts.cleanup_old_audio()

    return jsonify(result)


@app.route("/api/tts/voices")
def api_tts_voices():
    """Return available TTS voice models."""
    return jsonify(tts.get_stats())


# ── History ──────────────────────────────────────────────────────────────────

@app.route("/api/history")
def api_history():
    limit = request.args.get("limit", 50, type=int)
    return jsonify(history.get_all(limit))


@app.route("/api/history/stats")
def api_history_stats():
    return jsonify(history.get_stats())


@app.route("/api/history/search")
def api_history_search():
    query = request.args.get("q", "")
    return jsonify(history.search(query))


@app.route("/api/clear", methods=["POST"])
def api_clear():
    history.clear()
    return jsonify({"success": True})


@app.route("/api/history/export")
def api_export_history():
    """Export history as JSON or CSV."""
    fmt = request.args.get("format", "json")

    if fmt == "csv":
        csv_data = history.export_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=translation_history.csv"}
        )
    else:
        json_data = history.export_json()
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=translation_history.json"}
        )


# ── Corrections ──────────────────────────────────────────────────────────────

@app.route("/api/corrections/stats")
def api_corrections_stats():
    return jsonify(corrector.get_stats())


@app.route("/api/corrections/add", methods=["POST"])
def api_add_correction():
    """Add a new correction entry."""
    data = request.get_json()
    success = corrector.add_correction(
        category=data.get("category", "slang"),
        wrong=data.get("wrong", ""),
        correct=data.get("correct", ""),
        domain=data.get("domain")
    )
    return jsonify({"success": success})


# ── Datasets ─────────────────────────────────────────────────────────────────

@app.route("/api/datasets/stats")
def api_datasets_stats():
    return jsonify(datasets.get_stats())


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_modules()

    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"  {APP_TITLE} {APP_VERSION}")
    print(f"  http://127.0.0.1:{port}")
    print(f"{'='*50}\n")

    app.run(host="0.0.0.0", port=port, debug=False)