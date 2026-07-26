"""
history.py — Translation history management
Persistent storage, export, and analytics for translation history.
"""

import csv
import io
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from config import HISTORY_FILE, MAX_HISTORY


class TranslationHistory:
    """Manage persistent translation history."""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.favorites: List[str] = []  # Favorite language codes
        self.recent_langs: List[str] = []  # Recently used language codes

    def load(self):
        """Load history from disk."""
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    self.entries = data.get("entries", [])
                    self.favorites = data.get("favorites", [])
                    self.recent_langs = data.get("recent_langs", [])
                elif isinstance(data, list):
                    self.entries = data
                    self.favorites = []
                    self.recent_langs = []

                print(f"[History] Loaded {len(self.entries)} entries.")
            except Exception as e:
                print(f"[History] Error loading history: {e}")
                self.entries = []

    def save(self):
        """Save history to disk."""
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            data = {
                "entries": self.entries[:MAX_HISTORY],
                "favorites": self.favorites,
                "recent_langs": self.recent_langs[:20]
            }
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[History] Error saving: {e}")

    def add(self, entry: Dict[str, Any]):
        """
        Add a new translation entry.

        Expected entry format:
        {
            "original": str,
            "corrected": str,
            "translated": str,
            "source_lang": str,
            "target_lang": str,
            "timestamp": str,
            "time_ms": int,
            "confidence": float,
            "corrections": list,
            "validation": dict
        }
        """
        entry.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        entry.setdefault("id", len(self.entries))

        self.entries.insert(0, entry)

        # Trim to max
        if len(self.entries) > MAX_HISTORY:
            self.entries = self.entries[:MAX_HISTORY]

        # Update recent languages
        target = entry.get("target_lang")
        if target:
            if target in self.recent_langs:
                self.recent_langs.remove(target)
            self.recent_langs.insert(0, target)
            self.recent_langs = self.recent_langs[:20]

        self.save()

    def get_all(self, limit: int = 50) -> List[Dict]:
        """Return recent history entries."""
        return self.entries[:limit]

    def clear(self):
        """Clear all history."""
        self.entries = []
        self.save()

    def search(self, query: str) -> List[Dict]:
        """Search history by text content."""
        query_lower = query.lower()
        results = []
        for entry in self.entries:
            if (query_lower in entry.get("original", "").lower() or
                query_lower in entry.get("translated", "").lower()):
                results.append(entry)
        return results

    # ── Favorites ─────────────────────────────────────────────────────────────

    def add_favorite(self, lang_code: str):
        """Add a language to favorites."""
        if lang_code not in self.favorites:
            self.favorites.append(lang_code)
            self.save()

    def remove_favorite(self, lang_code: str):
        """Remove a language from favorites."""
        if lang_code in self.favorites:
            self.favorites.remove(lang_code)
            self.save()

    def get_favorites(self) -> List[str]:
        """Return favorite language codes."""
        return self.favorites

    def get_recent_langs(self) -> List[str]:
        """Return recently used language codes."""
        return self.recent_langs[:10]

    # ── Export ────────────────────────────────────────────────────────────────

    def export_json(self) -> str:
        """Export history as JSON string."""
        return json.dumps(self.entries, indent=2, ensure_ascii=False)

    def export_csv(self) -> str:
        """Export history as CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "timestamp", "original", "corrected", "translated",
            "source_lang", "target_lang", "time_ms", "confidence"
        ])

        for entry in self.entries:
            writer.writerow([
                entry.get("timestamp", ""),
                entry.get("original", ""),
                entry.get("corrected", ""),
                entry.get("translated", ""),
                entry.get("source_lang", ""),
                entry.get("target_lang", ""),
                entry.get("time_ms", ""),
                entry.get("confidence", "")
            ])

        return output.getvalue()

    # ── Analytics ─────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Return history analytics."""
        if not self.entries:
            return {
                "total_translations": 0,
                "avg_time_ms": 0,
                "top_target_langs": [],
                "top_source_langs": [],
                "recent_count_today": 0
            }

        # Count language usage
        target_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {}
        total_time = 0
        time_count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = 0

        for entry in self.entries:
            tl = entry.get("target_lang", "")
            sl = entry.get("source_lang", "")
            if tl:
                target_counts[tl] = target_counts.get(tl, 0) + 1
            if sl:
                source_counts[sl] = source_counts.get(sl, 0) + 1

            t = entry.get("time_ms", 0)
            if t:
                total_time += t
                time_count += 1

            ts = entry.get("timestamp", "")
            if ts.startswith(today):
                today_count += 1

        top_targets = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_translations": len(self.entries),
            "avg_time_ms": round(total_time / time_count) if time_count else 0,
            "top_target_langs": [{"lang": k, "count": v} for k, v in top_targets],
            "top_source_langs": [{"lang": k, "count": v} for k, v in top_sources],
            "recent_count_today": today_count,
            "favorites": self.favorites,
            "recent_langs": self.recent_langs[:10]
        }
