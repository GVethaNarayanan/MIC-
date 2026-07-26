"""
dataset_loader.py — Dataset loading and management
Supports: FLORES-200, OPUS, Tatoeba, Custom Parallel Datasets
Datasets are used for validation, correction, domain adaptation, and benchmarking.
"""

import csv
import json
import os
from typing import Dict, List, Optional, Any

from config import DATASETS_DIR


class DatasetLoader:
    """
    Load and manage translation datasets for validation and benchmarking.
    Does NOT retrain the model — datasets are used for:
    - Translation quality validation
    - Correction rule generation
    - Domain-specific term extraction
    - Benchmarking translation accuracy
    """

    def __init__(self):
        self.datasets: Dict[str, Dict] = {}
        self.parallel_data: Dict[str, List[Dict]] = {}  # lang_pair → [{src, tgt}]
        self.stats: Dict[str, Any] = {}

    def load_all(self):
        """Load all available datasets from the datasets/ folder."""
        os.makedirs(DATASETS_DIR, exist_ok=True)
        os.makedirs(os.path.join(DATASETS_DIR, "flores"), exist_ok=True)
        os.makedirs(os.path.join(DATASETS_DIR, "opus"), exist_ok=True)
        os.makedirs(os.path.join(DATASETS_DIR, "tatoeba"), exist_ok=True)
        os.makedirs(os.path.join(DATASETS_DIR, "custom"), exist_ok=True)
        os.makedirs(os.path.join(DATASETS_DIR, "custom_corrections"), exist_ok=True)

        # Create README for each dataset folder
        self._create_dataset_readmes()

        # Load each dataset type
        self._load_flores()
        self._load_opus()
        self._load_tatoeba()
        self._load_custom()

        total_pairs = sum(len(v) for v in self.parallel_data.values())
        print(f"[Dataset] Loaded {len(self.datasets)} datasets, {total_pairs} parallel sentence pairs.")

    def _load_flores(self):
        """Load FLORES-200 benchmark dataset."""
        flores_dir = os.path.join(DATASETS_DIR, "flores")
        self._load_from_directory(flores_dir, "flores")

    def _load_opus(self):
        """Load OPUS parallel corpus data."""
        opus_dir = os.path.join(DATASETS_DIR, "opus")
        self._load_from_directory(opus_dir, "opus")

    def _load_tatoeba(self):
        """Load Tatoeba sentence pairs."""
        tatoeba_dir = os.path.join(DATASETS_DIR, "tatoeba")
        self._load_from_directory(tatoeba_dir, "tatoeba")

    def _load_custom(self):
        """Load custom parallel datasets."""
        custom_dir = os.path.join(DATASETS_DIR, "custom")
        self._load_from_directory(custom_dir, "custom")

    def _load_from_directory(self, directory: str, dataset_name: str):
        """
        Load all CSV and JSON files from a directory as parallel data.

        Expected CSV format:
            source_lang, target_lang, source_text, target_text

        Expected JSON format:
            [{"source_lang": "en", "target_lang": "fr",
              "source_text": "Hello", "target_text": "Bonjour"}]
        """
        if not os.path.exists(directory):
            return

        file_count = 0
        pair_count = 0

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)

            if filename.endswith(".csv"):
                pairs = self._load_csv(filepath)
                if pairs:
                    file_count += 1
                    pair_count += len(pairs)
                    self._merge_pairs(pairs)

            elif filename.endswith(".json") and not filename.startswith("README"):
                pairs = self._load_json_pairs(filepath)
                if pairs:
                    file_count += 1
                    pair_count += len(pairs)
                    self._merge_pairs(pairs)

            elif filename.endswith(".tsv"):
                pairs = self._load_tsv(filepath)
                if pairs:
                    file_count += 1
                    pair_count += len(pairs)
                    self._merge_pairs(pairs)

        if file_count > 0:
            self.datasets[dataset_name] = {
                "directory": directory,
                "files": file_count,
                "pairs": pair_count
            }
            print(f"[Dataset] {dataset_name}: {file_count} files, {pair_count} pairs")

    def _load_csv(self, filepath: str) -> List[Dict]:
        """Load parallel sentences from CSV."""
        pairs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if all(k in row for k in ["source_lang", "target_lang",
                                               "source_text", "target_text"]):
                        pairs.append({
                            "source_lang": row["source_lang"].strip(),
                            "target_lang": row["target_lang"].strip(),
                            "source_text": row["source_text"].strip(),
                            "target_text": row["target_text"].strip(),
                            "source": os.path.basename(filepath)
                        })
        except Exception as e:
            print(f"[Dataset] Error loading CSV {filepath}: {e}")
        return pairs

    def _load_tsv(self, filepath: str) -> List[Dict]:
        """Load parallel sentences from TSV (tab-separated, Tatoeba format)."""
        pairs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if len(row) >= 4:
                        pairs.append({
                            "source_lang": row[0].strip(),
                            "target_lang": row[1].strip(),
                            "source_text": row[2].strip(),
                            "target_text": row[3].strip(),
                            "source": os.path.basename(filepath)
                        })
                    elif len(row) == 2:
                        # Simple two-column format (assume en → other)
                        pairs.append({
                            "source_lang": "en",
                            "target_lang": "unknown",
                            "source_text": row[0].strip(),
                            "target_text": row[1].strip(),
                            "source": os.path.basename(filepath)
                        })
        except Exception as e:
            print(f"[Dataset] Error loading TSV {filepath}: {e}")
        return pairs

    def _load_json_pairs(self, filepath: str) -> List[Dict]:
        """Load parallel sentences from JSON."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return [
                    {
                        "source_lang": item.get("source_lang", "en"),
                        "target_lang": item.get("target_lang", ""),
                        "source_text": item.get("source_text", ""),
                        "target_text": item.get("target_text", ""),
                        "source": os.path.basename(filepath)
                    }
                    for item in data
                    if item.get("source_text") and item.get("target_text")
                ]
        except Exception as e:
            print(f"[Dataset] Error loading JSON {filepath}: {e}")
        return []

    def _merge_pairs(self, pairs: List[Dict]):
        """Merge loaded pairs into the parallel_data store."""
        for pair in pairs:
            lang_pair = f"{pair['source_lang']}_{pair['target_lang']}"
            if lang_pair not in self.parallel_data:
                self.parallel_data[lang_pair] = []
            self.parallel_data[lang_pair].append(pair)

    def get_reference(self, source_text: str, source_lang: str,
                      target_lang: str) -> Optional[str]:
        """
        Look up a reference translation for benchmarking.
        Returns the target text if found, None otherwise.
        """
        lang_pair = f"{source_lang}_{target_lang}"
        pairs = self.parallel_data.get(lang_pair, [])

        source_lower = source_text.lower().strip()
        for pair in pairs:
            if pair["source_text"].lower().strip() == source_lower:
                return pair["target_text"]
        return None

    def validate_translation(self, source_text: str, translated_text: str,
                              source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Validate a translation against known reference data.

        Returns:
            dict with validation results
        """
        reference = self.get_reference(source_text, source_lang, target_lang)

        if reference is None:
            return {
                "has_reference": False,
                "reference": None,
                "match": None,
                "quality_score": None
            }

        # Simple exact match check
        exact_match = translated_text.strip().lower() == reference.strip().lower()

        # Word overlap score (simple metric)
        ref_words = set(reference.lower().split())
        trans_words = set(translated_text.lower().split())
        if ref_words:
            overlap = len(ref_words & trans_words) / len(ref_words)
        else:
            overlap = 0.0

        return {
            "has_reference": True,
            "reference": reference,
            "match": exact_match,
            "quality_score": round(overlap, 4)
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return dataset statistics."""
        return {
            "datasets_loaded": len(self.datasets),
            "language_pairs": len(self.parallel_data),
            "total_pairs": sum(len(v) for v in self.parallel_data.values()),
            "datasets": self.datasets,
            "available_pairs": list(self.parallel_data.keys())
        }

    def _create_dataset_readmes(self):
        """Create README files in each dataset folder explaining the format."""
        readmes = {
            "flores": {
                "name": "FLORES-200",
                "description": "Meta's FLORES-200 benchmark dataset for evaluating NLLB translations.",
                "url": "https://github.com/facebookresearch/flores",
                "format": "CSV or JSON with columns: source_lang, target_lang, source_text, target_text"
            },
            "opus": {
                "name": "OPUS Parallel Corpus",
                "description": "Parallel sentence pairs from OPUS (the largest open parallel corpus).",
                "url": "https://opus.nlpl.eu/",
                "format": "CSV or TSV with columns: source_lang, target_lang, source_text, target_text"
            },
            "tatoeba": {
                "name": "Tatoeba Sentence Pairs",
                "description": "Community-contributed sentence pairs from Tatoeba.",
                "url": "https://tatoeba.org/",
                "format": "TSV with columns: source_lang, target_lang, source_text, target_text"
            },
            "custom": {
                "name": "Custom Parallel Dataset",
                "description": "Your own parallel sentence pairs for domain-specific validation.",
                "url": "",
                "format": "CSV or JSON with columns: source_lang, target_lang, source_text, target_text"
            }
        }

        for folder, info in readmes.items():
            readme_path = os.path.join(DATASETS_DIR, folder, "README.md")
            if not os.path.exists(readme_path):
                content = f"""# {info['name']}

{info['description']}

## Download
{info['url'] if info['url'] else 'Add your own parallel sentence pairs here.'}

## Expected Format

### CSV Format
```csv
source_lang,target_lang,source_text,target_text
en,fr,Hello,Bonjour
en,ta,Good morning,காலை வணக்கம்
```

### JSON Format
```json
[
  {{"source_lang": "en", "target_lang": "fr", "source_text": "Hello", "target_text": "Bonjour"}},
  {{"source_lang": "en", "target_lang": "ta", "source_text": "Good morning", "target_text": "காலை வணக்கம்"}}
]
```

### TSV Format (tab-separated)
```
en\\tfr\\tHello\\tBonjour
en\\tta\\tGood morning\\tகாலை வணக்கம்
```

Place your files in this folder and restart the application.
"""
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(content)
