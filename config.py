"""
config.py — Central configuration for MIC Translator Dashboard
"""

APP_TITLE = "MIC Translator"
APP_SUBTITLE = "AI-Powered Real-Time Multilingual Voice Translation"
APP_VERSION = "v2.0"

# ── Whisper model size ────────────────────────────────────────────────────────
WHISPER_MODEL = "base"          # tiny | base | small | medium | large

# ── Audio defaults ────────────────────────────────────────────────────────────
DEFAULT_ENERGY_THRESHOLD = 300  # SpeechRecognition energy threshold
DEFAULT_PAUSE_THRESHOLD  = 0.8  # seconds of silence before phrase ends
DEFAULT_TTS_SPEED        = False  # gTTS slow flag (False = normal speed)
DEFAULT_AUTOPLAY         = True

# ── UI refresh interval (seconds) ────────────────────────────────────────────
REFRESH_INTERVAL = 1.5

# ── Google Translate language map ─────────────────────────────────────────────
LANGUAGES: dict[str, str] = {
    "Afrikaans":            "af",
    "Albanian":             "sq",
    "Amharic":              "am",
    "Arabic":               "ar",
    "Armenian":             "hy",
    "Azerbaijani":          "az",
    "Basque":               "eu",
    "Belarusian":           "be",
    "Bengali":              "bn",
    "Bosnian":              "bs",
    "Bulgarian":            "bg",
    "Catalan":              "ca",
    "Cebuano":              "ceb",
    "Chinese (Simplified)": "zh-cn",
    "Chinese (Traditional)":"zh-tw",
    "Corsican":             "co",
    "Croatian":             "hr",
    "Czech":                "cs",
    "Danish":               "da",
    "Dutch":                "nl",
    "English":              "en",
    "Esperanto":            "eo",
    "Estonian":             "et",
    "Finnish":              "fi",
    "French":               "fr",
    "Frisian":              "fy",
    "Galician":             "gl",
    "Georgian":             "ka",
    "German":               "de",
    "Greek":                "el",
    "Gujarati":             "gu",
    "Haitian Creole":       "ht",
    "Hausa":                "ha",
    "Hawaiian":             "haw",
    "Hebrew":               "he",
    "Hindi":                "hi",
    "Hmong":                "hmn",
    "Hungarian":            "hu",
    "Icelandic":            "is",
    "Igbo":                 "ig",
    "Indonesian":           "id",
    "Irish":                "ga",
    "Italian":              "it",
    "Japanese":             "ja",
    "Javanese":             "jv",
    "Kannada":              "kn",
    "Kazakh":               "kk",
    "Khmer":                "km",
    "Korean":               "ko",
    "Kurdish":              "ku",
    "Kyrgyz":               "ky",
    "Lao":                  "lo",
    "Latin":                "la",
    "Latvian":              "lv",
    "Lithuanian":           "lt",
    "Luxembourgish":        "lb",
    "Macedonian":           "mk",
    "Malagasy":             "mg",
    "Malay":                "ms",
    "Malayalam":            "ml",
    "Maltese":              "mt",
    "Maori":                "mi",
    "Marathi":              "mr",
    "Mongolian":            "mn",
    "Myanmar (Burmese)":    "my",
    "Nepali":               "ne",
    "Norwegian":            "no",
    "Nyanja (Chichewa)":    "ny",
    "Pashto":               "ps",
    "Persian":              "fa",
    "Polish":               "pl",
    "Portuguese":           "pt",
    "Punjabi":              "pa",
    "Romanian":             "ro",
    "Russian":              "ru",
    "Samoan":               "sm",
    "Scots Gaelic":         "gd",
    "Serbian":              "sr",
    "Sesotho":              "st",
    "Shona":                "sn",
    "Sindhi":               "sd",
    "Sinhala":              "si",
    "Slovak":               "sk",
    "Slovenian":            "sl",
    "Somali":               "so",
    "Spanish":              "es",
    "Sundanese":            "su",
    "Swahili":              "sw",
    "Swedish":              "sv",
    "Tagalog (Filipino)":   "tl",
    "Tajik":                "tg",
    "Tamil":                "ta",
    "Telugu":               "te",
    "Thai":                 "th",
    "Turkish":              "tr",
    "Ukrainian":            "uk",
    "Urdu":                 "ur",
    "Uzbek":                "uz",
    "Vietnamese":           "vi",
    "Welsh":                "cy",
    "Xhosa":                "xh",
    "Yiddish":              "yi",
    "Yoruba":               "yo",
    "Zulu":                 "zu",
}

# Default target language
DEFAULT_TARGET_LANG = "French"
