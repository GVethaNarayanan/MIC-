"""
config.py — Central configuration for MIC Translator Dashboard
Supports ALL 200+ NLLB languages for Any-to-Any translation.
"""

import os

# ── App Info ──────────────────────────────────────────────────────────────────
APP_TITLE = "MIC Translator"
APP_SUBTITLE = "AI-Powered Real-Time Multilingual Voice Translation"
APP_VERSION = "v3.0"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")
CORRECTIONS_FILE = os.path.join(DATASETS_DIR, "corrections.json")
VOICES_DIR = os.path.join(BASE_DIR, "voices")

# ── Whisper model size ────────────────────────────────────────────────────────
WHISPER_MODEL = "base"  # tiny | base | small | medium | large

# ── NLLB model ────────────────────────────────────────────────────────────────
NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# ── Audio defaults ────────────────────────────────────────────────────────────
DEFAULT_ENERGY_THRESHOLD = 300
DEFAULT_PAUSE_THRESHOLD = 0.8
DEFAULT_TTS_SPEED = False
DEFAULT_AUTOPLAY = True

# ── UI refresh interval (seconds) ────────────────────────────────────────────
REFRESH_INTERVAL = 1.5

# ── Maximum history entries ──────────────────────────────────────────────────
MAX_HISTORY = 500

# ── Default target language ──────────────────────────────────────────────────
DEFAULT_TARGET_LANG = "fr"

# ══════════════════════════════════════════════════════════════════════════════
# NLLB-200 FULL LANGUAGE MAP
# Maps ISO 639-1/3 codes → NLLB Flores-200 codes
# Covers ALL 200+ languages supported by facebook/nllb-200-distilled-600M
# ══════════════════════════════════════════════════════════════════════════════

NLLB_LANGS = {
    # ── A ─────────────────────────────────────────────────────────────────────
    "ace": "ace_Latn",      # Acehnese (Latin)
    "acm": "acm_Arab",      # Mesopotamian Arabic
    "acq": "acq_Arab",      # Ta'izzi-Adeni Arabic
    "aeb": "aeb_Arab",      # Tunisian Arabic
    "af":  "afr_Latn",      # Afrikaans
    "ajp": "ajp_Arab",      # South Levantine Arabic
    "ak":  "aka_Latn",      # Akan / Twi
    "am":  "amh_Ethi",      # Amharic
    "apc": "apc_Arab",      # North Levantine Arabic
    "ar":  "arb_Arab",      # Modern Standard Arabic
    "ars": "ars_Arab",      # Najdi Arabic
    "ary": "ary_Arab",      # Moroccan Arabic
    "arz": "arz_Arab",      # Egyptian Arabic
    "as":  "asm_Beng",      # Assamese
    "ast": "ast_Latn",      # Asturian
    "awa": "awa_Deva",      # Awadhi
    "ayr": "ayr_Latn",      # Central Aymara
    "az":  "azj_Latn",      # Azerbaijani (North)
    "azb": "azb_Arab",      # South Azerbaijani

    # ── B ─────────────────────────────────────────────────────────────────────
    "ba":  "bak_Cyrl",      # Bashkir
    "bm":  "bam_Latn",      # Bambara
    "ban": "ban_Latn",      # Balinese
    "be":  "bel_Cyrl",      # Belarusian
    "bem": "bem_Latn",      # Bemba
    "bn":  "ben_Beng",      # Bengali
    "bho": "bho_Deva",      # Bhojpuri
    "bjn": "bjn_Latn",      # Banjar (Latin)
    "bo":  "bod_Tibt",      # Tibetan
    "bs":  "bos_Latn",      # Bosnian
    "bug": "bug_Latn",      # Buginese
    "bg":  "bul_Cyrl",      # Bulgarian

    # ── C ─────────────────────────────────────────────────────────────────────
    "ca":  "cat_Latn",      # Catalan
    "ceb": "ceb_Latn",      # Cebuano
    "cs":  "ces_Latn",      # Czech
    "cjk": "cjk_Latn",      # Chokwe
    "ckb": "ckb_Arab",      # Central Kurdish
    "crh": "crh_Latn",      # Crimean Tatar
    "cy":  "cym_Latn",      # Welsh

    # ── D ─────────────────────────────────────────────────────────────────────
    "da":  "dan_Latn",      # Danish
    "de":  "deu_Latn",      # German
    "dik": "dik_Latn",      # Southwestern Dinka
    "dyu": "dyu_Latn",      # Dyula
    "dz":  "dzo_Tibt",      # Dzongkha

    # ── E ─────────────────────────────────────────────────────────────────────
    "el":  "ell_Grek",      # Greek
    "en":  "eng_Latn",      # English
    "eo":  "epo_Latn",      # Esperanto
    "et":  "est_Latn",      # Estonian
    "eu":  "eus_Latn",      # Basque
    "ee":  "ewe_Latn",      # Ewe
    "es":  "spa_Latn",      # Spanish

    # ── F ─────────────────────────────────────────────────────────────────────
    "fa":  "pes_Arab",      # Persian (Western)
    "ff":  "fuv_Latn",      # Nigerian Fulfulde
    "fi":  "fin_Latn",      # Finnish
    "fj":  "fij_Latn",      # Fijian
    "fo":  "fao_Latn",      # Faroese
    "fon": "fon_Latn",      # Fon
    "fr":  "fra_Latn",      # French
    "fur": "fur_Latn",      # Friulian

    # ── G ─────────────────────────────────────────────────────────────────────
    "ga":  "gle_Latn",      # Irish
    "gd":  "gla_Latn",      # Scottish Gaelic
    "gl":  "glg_Latn",      # Galician
    "gn":  "grn_Latn",      # Guarani
    "gu":  "guj_Gujr",      # Gujarati

    # ── H ─────────────────────────────────────────────────────────────────────
    "ha":  "hau_Latn",      # Hausa
    "he":  "heb_Hebr",      # Hebrew
    "hi":  "hin_Deva",      # Hindi
    "hne": "hne_Deva",      # Chhattisgarhi
    "hr":  "hrv_Latn",      # Croatian
    "ht":  "hat_Latn",      # Haitian Creole
    "hu":  "hun_Latn",      # Hungarian
    "hy":  "hye_Armn",      # Armenian

    # ── I ─────────────────────────────────────────────────────────────────────
    "id":  "ind_Latn",      # Indonesian
    "ig":  "ibo_Latn",      # Igbo
    "ilo": "ilo_Latn",      # Ilocano
    "is":  "isl_Latn",      # Icelandic
    "it":  "ita_Latn",      # Italian

    # ── J ─────────────────────────────────────────────────────────────────────
    "ja":  "jpn_Jpan",      # Japanese
    "jv":  "jav_Latn",      # Javanese

    # ── K ─────────────────────────────────────────────────────────────────────
    "ka":  "kat_Geor",      # Georgian
    "kab": "kab_Latn",      # Kabyle
    "kac": "kac_Latn",      # Jingpho / Kachin
    "kam": "kam_Latn",      # Kamba
    "kbp": "kbp_Latn",      # Kabiyè
    "kea": "kea_Latn",      # Kabuverdianu
    "kg":  "kon_Latn",      # Kikongo
    "ki":  "kik_Latn",      # Kikuyu
    "kk":  "kaz_Cyrl",      # Kazakh
    "km":  "khm_Khmr",      # Khmer
    "kmb": "kmb_Latn",      # Kimbundu
    "kmr": "kmr_Latn",      # Northern Kurdish (Kurmanji)
    "kn":  "kan_Knda",      # Kannada
    "ko":  "kor_Hang",      # Korean
    "kr":  "knc_Latn",      # Central Kanuri (Latin)
    "ks":  "kas_Arab",      # Kashmiri (Arabic script)
    "ky":  "kir_Cyrl",      # Kyrgyz

    # ── L ─────────────────────────────────────────────────────────────────────
    "lb":  "ltz_Latn",      # Luxembourgish
    "lg":  "lug_Latn",      # Ganda / Luganda
    "li":  "lim_Latn",      # Limburgish
    "lij": "lij_Latn",      # Ligurian
    "lmo": "lmo_Latn",      # Lombard
    "ln":  "lin_Latn",      # Lingala
    "lo":  "lao_Laoo",      # Lao
    "lt":  "lit_Latn",      # Lithuanian
    "ltg": "ltg_Latn",      # Latgalian
    "lu":  "lua_Latn",      # Luba-Kasai
    "luo": "luo_Latn",      # Luo
    "lus": "lus_Latn",      # Mizo
    "lv":  "lvs_Latn",      # Latvian

    # ── M ─────────────────────────────────────────────────────────────────────
    "mag": "mag_Deva",      # Magahi
    "mai": "mai_Deva",      # Maithili
    "mg":  "plt_Latn",      # Malagasy (Plateau)
    "mi":  "mri_Latn",      # Maori
    "min": "min_Latn",      # Minangkabau (Latin)
    "mk":  "mkd_Cyrl",      # Macedonian
    "ml":  "mal_Mlym",      # Malayalam
    "mn":  "khk_Cyrl",      # Mongolian (Halh)
    "mni": "mni_Beng",      # Manipuri (Bengali script)
    "mos": "mos_Latn",      # Mossi
    "mr":  "mar_Deva",      # Marathi
    "ms":  "zsm_Latn",      # Standard Malay
    "mt":  "mlt_Latn",      # Maltese
    "my":  "mya_Mymr",      # Burmese

    # ── N ─────────────────────────────────────────────────────────────────────
    "ne":  "npi_Deva",      # Nepali
    "nl":  "nld_Latn",      # Dutch
    "nn":  "nno_Latn",      # Norwegian Nynorsk
    "no":  "nob_Latn",      # Norwegian Bokmål
    "nso": "nso_Latn",      # Northern Sotho / Pedi
    "nus": "nus_Latn",      # Nuer
    "ny":  "nya_Latn",      # Chichewa / Nyanja

    # ── O ─────────────────────────────────────────────────────────────────────
    "oc":  "oci_Latn",      # Occitan
    "om":  "gaz_Latn",      # Oromo (West Central)
    "or":  "ory_Orya",      # Odia

    # ── P ─────────────────────────────────────────────────────────────────────
    "pa":  "pan_Guru",      # Punjabi (Eastern, Gurmukhi)
    "pag": "pag_Latn",      # Pangasinan
    "pap": "pap_Latn",      # Papiamento
    "pl":  "pol_Latn",      # Polish
    "ps":  "pbt_Arab",      # Pashto (Southern)
    "pt":  "por_Latn",      # Portuguese

    # ── Q ─────────────────────────────────────────────────────────────────────
    "qu":  "quy_Latn",      # Ayacucho Quechua

    # ── R ─────────────────────────────────────────────────────────────────────
    "ro":  "ron_Latn",      # Romanian
    "rn":  "run_Latn",      # Rundi
    "ru":  "rus_Cyrl",      # Russian
    "rw":  "kin_Latn",      # Kinyarwanda

    # ── S ─────────────────────────────────────────────────────────────────────
    "sa":  "san_Deva",      # Sanskrit
    "sat": "sat_Olck",      # Santali (Ol Chiki)
    "scn": "scn_Latn",      # Sicilian
    "sd":  "snd_Arab",      # Sindhi
    "sg":  "sag_Latn",      # Sango
    "shn": "shn_Mymr",      # Shan
    "si":  "sin_Sinh",      # Sinhala
    "sk":  "slk_Latn",      # Slovak
    "sl":  "slv_Latn",      # Slovenian
    "sm":  "smo_Latn",      # Samoan
    "sn":  "sna_Latn",      # Shona
    "so":  "som_Latn",      # Somali
    "sq":  "als_Latn",      # Albanian
    "sr":  "srp_Cyrl",      # Serbian
    "ss":  "ssw_Latn",      # Swati
    "st":  "sot_Latn",      # Southern Sotho
    "su":  "sun_Latn",      # Sundanese
    "sv":  "swe_Latn",      # Swedish
    "sw":  "swh_Latn",      # Swahili
    "szl": "szl_Latn",      # Silesian

    # ── T ─────────────────────────────────────────────────────────────────────
    "ta":  "tam_Taml",      # Tamil
    "taq": "taq_Latn",      # Tamasheq (Latin)
    "te":  "tel_Telu",      # Telugu
    "tg":  "tgk_Cyrl",      # Tajik
    "th":  "tha_Thai",      # Thai
    "ti":  "tir_Ethi",      # Tigrinya
    "tk":  "tuk_Latn",      # Turkmen
    "tl":  "tgl_Latn",      # Tagalog / Filipino
    "tn":  "tsn_Latn",      # Tswana
    "to":  "ton_Latn",      # Tongan
    "tpi": "tpi_Latn",      # Tok Pisin
    "tr":  "tur_Latn",      # Turkish
    "ts":  "tso_Latn",      # Tsonga
    "tt":  "tat_Cyrl",      # Tatar
    "tum": "tum_Latn",      # Tumbuka
    "tw":  "twi_Latn",      # Twi

    # ── U ─────────────────────────────────────────────────────────────────────
    "ug":  "uig_Arab",      # Uyghur
    "uk":  "ukr_Cyrl",      # Ukrainian
    "umb": "umb_Latn",      # Umbundu
    "ur":  "urd_Arab",      # Urdu
    "uz":  "uzn_Latn",      # Uzbek (Northern)

    # ── V ─────────────────────────────────────────────────────────────────────
    "vec": "vec_Latn",      # Venetian
    "vi":  "vie_Latn",      # Vietnamese

    # ── W ─────────────────────────────────────────────────────────────────────
    "war": "war_Latn",      # Waray
    "wo":  "wol_Latn",      # Wolof

    # ── X ─────────────────────────────────────────────────────────────────────
    "xh":  "xho_Latn",      # Xhosa

    # ── Y ─────────────────────────────────────────────────────────────────────
    "yo":  "yor_Latn",      # Yoruba

    # ── Z ─────────────────────────────────────────────────────────────────────
    "zh":  "zho_Hans",      # Chinese (Simplified)
    "zht": "zho_Hant",      # Chinese (Traditional)
    "zu":  "zul_Latn",      # Zulu
}

# ══════════════════════════════════════════════════════════════════════════════
# Human-readable language names (for UI display)
# ══════════════════════════════════════════════════════════════════════════════

LANGUAGE_NAMES = {
    "ace": "Acehnese", "acm": "Mesopotamian Arabic", "acq": "Ta'izzi-Adeni Arabic",
    "aeb": "Tunisian Arabic", "af": "Afrikaans", "ajp": "South Levantine Arabic",
    "ak": "Akan / Twi", "am": "Amharic", "apc": "North Levantine Arabic",
    "ar": "Arabic (MSA)", "ars": "Najdi Arabic", "ary": "Moroccan Arabic",
    "arz": "Egyptian Arabic", "as": "Assamese", "ast": "Asturian",
    "awa": "Awadhi", "ayr": "Aymara", "az": "Azerbaijani",
    "azb": "South Azerbaijani", "ba": "Bashkir", "bm": "Bambara",
    "ban": "Balinese", "be": "Belarusian", "bem": "Bemba",
    "bn": "Bengali", "bho": "Bhojpuri", "bjn": "Banjar",
    "bo": "Tibetan", "bs": "Bosnian", "bug": "Buginese",
    "bg": "Bulgarian", "ca": "Catalan", "ceb": "Cebuano",
    "cs": "Czech", "cjk": "Chokwe", "ckb": "Central Kurdish",
    "crh": "Crimean Tatar", "cy": "Welsh", "da": "Danish",
    "de": "German", "dik": "Dinka", "dyu": "Dyula",
    "dz": "Dzongkha", "el": "Greek", "en": "English",
    "eo": "Esperanto", "et": "Estonian", "eu": "Basque",
    "ee": "Ewe", "es": "Spanish", "fa": "Persian / Farsi", "ff": "Fulfulde",
    "fi": "Finnish", "fj": "Fijian", "fo": "Faroese",
    "fon": "Fon", "fr": "French", "fur": "Friulian",
    "ga": "Irish", "gd": "Scottish Gaelic", "gl": "Galician",
    "gn": "Guarani", "gu": "Gujarati", "ha": "Hausa",
    "he": "Hebrew", "hi": "Hindi", "hne": "Chhattisgarhi",
    "hr": "Croatian", "ht": "Haitian Creole", "hu": "Hungarian",
    "hy": "Armenian", "id": "Indonesian", "ig": "Igbo",
    "ilo": "Ilocano", "is": "Icelandic", "it": "Italian",
    "ja": "Japanese", "jv": "Javanese", "ka": "Georgian",
    "kab": "Kabyle", "kac": "Kachin / Jingpho", "kam": "Kamba",
    "kbp": "Kabiyè", "kea": "Kabuverdianu", "kg": "Kikongo",
    "ki": "Kikuyu", "kk": "Kazakh", "km": "Khmer",
    "kmb": "Kimbundu", "kmr": "Kurdish (Kurmanji)", "kn": "Kannada",
    "ko": "Korean", "kr": "Kanuri", "ks": "Kashmiri",
    "ky": "Kyrgyz", "lb": "Luxembourgish", "lg": "Luganda",
    "li": "Limburgish", "lij": "Ligurian", "lmo": "Lombard",
    "ln": "Lingala", "lo": "Lao", "lt": "Lithuanian",
    "ltg": "Latgalian", "lu": "Luba-Kasai", "luo": "Luo",
    "lus": "Mizo", "lv": "Latvian", "mag": "Magahi",
    "mai": "Maithili", "mg": "Malagasy", "mi": "Maori",
    "min": "Minangkabau", "mk": "Macedonian", "ml": "Malayalam",
    "mn": "Mongolian", "mni": "Manipuri", "mos": "Mossi",
    "mr": "Marathi", "ms": "Malay", "mt": "Maltese",
    "my": "Burmese / Myanmar", "ne": "Nepali", "nl": "Dutch",
    "nn": "Norwegian Nynorsk", "no": "Norwegian", "nso": "Northern Sotho",
    "nus": "Nuer", "ny": "Chichewa / Nyanja", "oc": "Occitan",
    "om": "Oromo", "or": "Odia", "pa": "Punjabi",
    "pag": "Pangasinan", "pap": "Papiamento", "pl": "Polish",
    "ps": "Pashto", "pt": "Portuguese", "qu": "Quechua",
    "ro": "Romanian", "rn": "Rundi", "ru": "Russian",
    "rw": "Kinyarwanda", "sa": "Sanskrit", "sat": "Santali",
    "scn": "Sicilian", "sd": "Sindhi", "sg": "Sango",
    "shn": "Shan", "si": "Sinhala", "sk": "Slovak",
    "sl": "Slovenian", "sm": "Samoan", "sn": "Shona",
    "so": "Somali", "sq": "Albanian", "sr": "Serbian",
    "ss": "Swati", "st": "Southern Sotho", "su": "Sundanese",
    "sv": "Swedish", "sw": "Swahili", "szl": "Silesian",
    "ta": "Tamil", "taq": "Tamasheq", "te": "Telugu",
    "tg": "Tajik", "th": "Thai", "ti": "Tigrinya",
    "tk": "Turkmen", "tl": "Tagalog / Filipino", "tn": "Tswana",
    "to": "Tongan", "tpi": "Tok Pisin", "tr": "Turkish",
    "ts": "Tsonga", "tt": "Tatar", "tum": "Tumbuka",
    "tw": "Twi", "ug": "Uyghur", "uk": "Ukrainian",
    "umb": "Umbundu", "ur": "Urdu", "uz": "Uzbek",
    "vec": "Venetian", "vi": "Vietnamese", "war": "Waray",
    "wo": "Wolof", "xh": "Xhosa", "yo": "Yoruba",
    "zh": "Chinese (Simplified)", "zht": "Chinese (Traditional)",
    "zu": "Zulu",
}

# Reverse lookup: NLLB code → ISO code
NLLB_TO_ISO = {v: k for k, v in NLLB_LANGS.items()}

# ── Piper TTS voice model map ────────────────────────────────────────────────
# Maps language codes to available Piper ONNX voice models
# Users can add more .onnx models to the voices/ directory
PIPER_VOICES = {
    "en": "en_US-lessac-medium.onnx",
    "hi": "hi_IN-pratham-medium.onnx",
}

# ── Whisper language codes (for source language detection) ────────────────────
# Whisper uses ISO 639-1 codes for the languages it supports
WHISPER_LANGUAGES = [
    "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
    "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi",
    "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no",
    "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy", "sk",
    "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk",
    "br", "eu", "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw",
    "gl", "mr", "pa", "si", "km", "sn", "yo", "so", "af", "oc",
    "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", "uz", "fo",
    "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl",
    "mg", "as", "tt", "ha", "ba", "jv", "su", "ln",
]
