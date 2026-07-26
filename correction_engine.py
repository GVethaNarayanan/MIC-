"""
correction_engine.py — Pre- and Post-translation correction pipeline
Handles: misheard words, slang, short forms, spoken English,
         confused words, and domain-specific corrections.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any

from config import CORRECTIONS_FILE, DATASETS_DIR


class CorrectionEngine:
    """
    Two-stage correction pipeline:
    1. PRE-TRANSLATION:  Fix speech recognition errors before translation
    2. POST-TRANSLATION: Fix known translation errors after NLLB output
    """

    def __init__(self):
        self.pre_corrections: Dict[str, Dict] = {}   # lang → {pattern: replacement}
        self.post_corrections: Dict[str, Dict] = {}   # lang_pair → {pattern: replacement}
        self.slang_map: Dict[str, str] = {}
        self.short_forms: Dict[str, str] = {}
        self.confused_words: Dict[str, str] = {}
        self.domain_terms: Dict[str, Dict[str, str]] = {}
        self.loaded = False

    def load(self):
        """Load all correction datasets."""
        os.makedirs(DATASETS_DIR, exist_ok=True)

        # Create default corrections file if it doesn't exist
        if not os.path.exists(CORRECTIONS_FILE):
            self._create_default_corrections()

        try:
            with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.slang_map = data.get("slang", {})
            self.short_forms = data.get("short_forms", {})
            self.confused_words = data.get("confused_words", {})
            self.domain_terms = data.get("domain_terms", {})
            self.pre_corrections = data.get("pre_corrections", {})
            self.post_corrections = data.get("post_corrections", {})

            total = (len(self.slang_map) + len(self.short_forms) +
                     len(self.confused_words) + sum(len(v) for v in self.domain_terms.values()))
            print(f"[Correction] Loaded {total} correction entries.")
            self.loaded = True

        except Exception as e:
            print(f"[Correction] Error loading corrections: {e}")
            self._create_default_corrections()
            self.loaded = True

        # Load any additional custom correction files
        self._load_custom_corrections()

    def pre_translate(self, text: str, source_lang: str = "en") -> Dict[str, Any]:
        """
        Apply pre-translation corrections to recognized speech text.

        Pipeline:
            Raw Whisper text → Slang fix → Short forms → Confused words
            → Domain terms → Custom pre-corrections → Cleaned text

        Returns:
            dict with 'text' (corrected), 'corrections' (list of changes made)
        """
        corrections = []
        original = text

        # 1. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # 2. Apply slang corrections (case-insensitive)
        for slang, replacement in self.slang_map.items():
            pattern = re.compile(r'\b' + re.escape(slang) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(replacement, text)
                corrections.append({"type": "slang", "from": slang, "to": replacement})

        # 3. Apply short form expansions
        for short, full in self.short_forms.items():
            pattern = re.compile(r'\b' + re.escape(short) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(full, text)
                corrections.append({"type": "short_form", "from": short, "to": full})

        # 4. Fix commonly confused words
        for wrong, correct in self.confused_words.items():
            pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(correct, text)
                corrections.append({"type": "confused", "from": wrong, "to": correct})

        # 5. Apply domain-specific corrections
        for domain, terms in self.domain_terms.items():
            for wrong, correct in terms.items():
                pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
                if pattern.search(text):
                    text = pattern.sub(correct, text)
                    corrections.append({
                        "type": "domain",
                        "domain": domain,
                        "from": wrong,
                        "to": correct
                    })

        # 6. Apply language-specific pre-corrections
        lang_corrections = self.pre_corrections.get(source_lang, {})
        for wrong, correct in lang_corrections.items():
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(correct, text)
                corrections.append({"type": "pre_lang", "from": wrong, "to": correct})

        return {
            "text": text,
            "original": original,
            "corrected": text != original,
            "corrections": corrections,
            "correction_count": len(corrections)
        }

    def post_translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Apply post-translation corrections to NLLB output.

        Returns:
            dict with 'text' (corrected), 'corrections' (list of changes)
        """
        corrections = []
        original = text
        lang_pair = f"{source_lang}_{target_lang}"

        # Apply language-pair-specific post-corrections
        pair_corrections = self.post_corrections.get(lang_pair, {})
        for wrong, correct in pair_corrections.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                corrections.append({"type": "post_lang", "from": wrong, "to": correct})

        # Target-language-specific corrections
        target_corrections = self.post_corrections.get(target_lang, {})
        for wrong, correct in target_corrections.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                corrections.append({"type": "post_target", "from": wrong, "to": correct})

        return {
            "text": text,
            "original": original,
            "corrected": text != original,
            "corrections": corrections
        }

    def add_correction(self, category: str, wrong: str, correct: str,
                       domain: Optional[str] = None) -> bool:
        """
        Add a new correction entry and persist to file.

        Args:
            category: 'slang', 'short_forms', 'confused_words', 'domain_terms'
            wrong: The incorrect/misheard form
            correct: The correct replacement
            domain: Domain name (only for 'domain_terms' category)
        """
        try:
            if category == "slang":
                self.slang_map[wrong] = correct
            elif category == "short_forms":
                self.short_forms[wrong] = correct
            elif category == "confused_words":
                self.confused_words[wrong] = correct
            elif category == "domain_terms" and domain:
                if domain not in self.domain_terms:
                    self.domain_terms[domain] = {}
                self.domain_terms[domain][wrong] = correct
            else:
                return False

            self._save_corrections()
            return True
        except Exception as e:
            print(f"[Correction] Error adding correction: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """Return statistics about loaded corrections."""
        return {
            "slang_entries": len(self.slang_map),
            "short_form_entries": len(self.short_forms),
            "confused_word_entries": len(self.confused_words),
            "domain_entries": sum(len(v) for v in self.domain_terms.values()),
            "pre_correction_langs": len(self.pre_corrections),
            "post_correction_pairs": len(self.post_corrections),
            "total": (len(self.slang_map) + len(self.short_forms) +
                      len(self.confused_words) +
                      sum(len(v) for v in self.domain_terms.values()))
        }

    def _load_custom_corrections(self):
        """Load additional correction files from datasets/ folder."""
        custom_dir = os.path.join(DATASETS_DIR, "custom_corrections")
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir, exist_ok=True)
            return

        for filename in os.listdir(custom_dir):
            if filename.endswith(".json"):
                try:
                    filepath = os.path.join(custom_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Merge custom corrections
                    if "slang" in data:
                        self.slang_map.update(data["slang"])
                    if "short_forms" in data:
                        self.short_forms.update(data["short_forms"])
                    if "confused_words" in data:
                        self.confused_words.update(data["confused_words"])
                    if "domain_terms" in data:
                        for domain, terms in data["domain_terms"].items():
                            if domain not in self.domain_terms:
                                self.domain_terms[domain] = {}
                            self.domain_terms[domain].update(terms)

                    print(f"[Correction] Loaded custom: {filename}")
                except Exception as e:
                    print(f"[Correction] Error loading {filename}: {e}")

    def _save_corrections(self):
        """Persist corrections to disk."""
        data = {
            "slang": self.slang_map,
            "short_forms": self.short_forms,
            "confused_words": self.confused_words,
            "domain_terms": self.domain_terms,
            "pre_corrections": self.pre_corrections,
            "post_corrections": self.post_corrections,
        }
        os.makedirs(os.path.dirname(CORRECTIONS_FILE), exist_ok=True)
        with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _create_default_corrections(self):
        """Create the default corrections dataset."""
        data = {
            "slang": {
                "gonna": "going to",
                "wanna": "want to",
                "gotta": "got to",
                "lemme": "let me",
                "gimme": "give me",
                "kinda": "kind of",
                "sorta": "sort of",
                "dunno": "don't know",
                "ain't": "is not",
                "y'all": "you all",
                "bro": "brother",
                "sis": "sister",
                "dude": "friend",
                "nah": "no",
                "yep": "yes",
                "yup": "yes",
                "nope": "no",
                "ok": "okay",
                "coz": "because",
                "cuz": "because",
                "cos": "because",
                "sup": "what is up",
                "wassup": "what is up",
                "whatcha": "what are you",
                "imma": "I am going to",
                "fam": "family",
                "lit": "exciting",
                "lowkey": "slightly",
                "highkey": "very much",
                "salty": "upset",
                "shook": "shocked",
                "vibe": "feeling",
                "flex": "show off",
                "ghost": "disappear",
                "slay": "do excellently",
                "bet": "agreed",
                "cap": "lie",
                "no cap": "no lie",
                "fire": "excellent",
                "sus": "suspicious",
                "bruh": "brother",
                "hella": "very",
                "bougie": "fancy",
                "clap back": "respond sharply",
                "shade": "disrespect",
                "tea": "gossip",
                "mood": "relatable",
                "stan": "admire greatly",
                "simp": "overly devoted person",
                "yeet": "throw",
                "oof": "expressing discomfort",
                "periodt": "period",
                "deadass": "seriously",
                "idk": "I don't know",
                "tbh": "to be honest",
                "imo": "in my opinion",
                "smh": "shaking my head",
                "lol": "laughing out loud",
                "omg": "oh my god",
                "brb": "be right back",
                "btw": "by the way",
                "fyi": "for your information",
                "asap": "as soon as possible"
            },

            "short_forms": {
                "govt": "government",
                "dept": "department",
                "mgr": "manager",
                "prof": "professor",
                "doc": "doctor",
                "info": "information",
                "tech": "technology",
                "app": "application",
                "bio": "biography",
                "exam": "examination",
                "lab": "laboratory",
                "math": "mathematics",
                "stats": "statistics",
                "ref": "reference",
                "temp": "temperature",
                "approx": "approximately",
                "etc": "etcetera",
                "vs": "versus",
                "min": "minute",
                "max": "maximum",
                "avg": "average",
                "qty": "quantity",
                "yr": "year",
                "mo": "month",
                "wk": "week",
                "hr": "hour",
                "sec": "second",
                "Mon": "Monday",
                "Tue": "Tuesday",
                "Wed": "Wednesday",
                "Thu": "Thursday",
                "Fri": "Friday",
                "Sat": "Saturday",
                "Sun": "Sunday",
                "Jan": "January",
                "Feb": "February",
                "Mar": "March",
                "Apr": "April",
                "Jun": "June",
                "Jul": "July",
                "Aug": "August",
                "Sep": "September",
                "Oct": "October",
                "Nov": "November",
                "Dec": "December"
            },

            "confused_words": {
                "their there": "there",
                "your you're": "you are",
                "its it's": "it is",
                "affect effect": "effect",
                "then than": "than",
                "loose lose": "lose",
                "weather whether": "whether",
                "to too": "too",
                "accept except": "except",
                "advise advice": "advice",
                "principal principle": "principle",
                "stationary stationery": "stationery",
                "complement compliment": "compliment",
                "desert dessert": "dessert",
                "alot": "a lot",
                "definately": "definitely",
                "seperate": "separate",
                "occured": "occurred",
                "recieve": "receive",
                "untill": "until",
                "writting": "writing",
                "calender": "calendar",
                "goverment": "government",
                "enviroment": "environment",
                "tommorrow": "tomorrow",
                "accomodate": "accommodate",
                "concious": "conscious",
                "necesary": "necessary",
                "occassion": "occasion",
                "priviledge": "privilege",
                "pronounciation": "pronunciation",
                "recomend": "recommend",
                "refered": "referred",
                "succesful": "successful",
                "wierd": "weird"
            },

            "domain_terms": {
                "medical": {
                    "BP": "blood pressure",
                    "HR": "heart rate",
                    "temp": "temperature",
                    "RX": "prescription",
                    "OPD": "outpatient department",
                    "ICU": "intensive care unit",
                    "ER": "emergency room",
                    "MRI": "magnetic resonance imaging",
                    "CT scan": "computed tomography scan",
                    "ECG": "electrocardiogram"
                },
                "education": {
                    "GPA": "grade point average",
                    "CGPA": "cumulative grade point average",
                    "HOD": "head of department",
                    "PhD": "Doctor of Philosophy",
                    "MSc": "Master of Science",
                    "BSc": "Bachelor of Science",
                    "sem": "semester",
                    "assign": "assignment",
                    "ppt": "presentation"
                },
                "technology": {
                    "API": "application programming interface",
                    "UI": "user interface",
                    "UX": "user experience",
                    "DB": "database",
                    "OS": "operating system",
                    "CPU": "central processing unit",
                    "GPU": "graphics processing unit",
                    "RAM": "random access memory",
                    "SSD": "solid state drive",
                    "URL": "uniform resource locator"
                },
                "business": {
                    "CEO": "Chief Executive Officer",
                    "CFO": "Chief Financial Officer",
                    "CTO": "Chief Technology Officer",
                    "HR": "human resources",
                    "KPI": "key performance indicator",
                    "ROI": "return on investment",
                    "B2B": "business to business",
                    "B2C": "business to consumer",
                    "ETA": "estimated time of arrival",
                    "RSVP": "please respond"
                }
            },

            "pre_corrections": {
                "en": {
                    "hii": "hi",
                    "hiii": "hi",
                    "hellooo": "hello",
                    "byeee": "bye",
                    "yesss": "yes",
                    "nooo": "no",
                    "pleaseee": "please",
                    "thanksss": "thanks",
                    "sorryyy": "sorry",
                    "okayyyy": "okay",
                    "wowww": "wow",
                    "ummm": "",
                    "uhhh": "",
                    "ahhh": "",
                    "hmmmm": "",
                    "errr": "",
                    "like like": "like",
                    "you know you know": "you know",
                    "I mean I mean": "I mean"
                }
            },

            "post_corrections": {}
        }

        os.makedirs(os.path.dirname(CORRECTIONS_FILE), exist_ok=True)
        with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Load into memory
        self.slang_map = data["slang"]
        self.short_forms = data["short_forms"]
        self.confused_words = data["confused_words"]
        self.domain_terms = data["domain_terms"]
        self.pre_corrections = data["pre_corrections"]
        self.post_corrections = data["post_corrections"]

        print(f"[Correction] Created default corrections dataset.")
