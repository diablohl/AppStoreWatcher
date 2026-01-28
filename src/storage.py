import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, file_path: str = "data/history.json"):
        self.file_path = file_path
        self._ensure_directory(self.file_path)

    def _ensure_directory(self, path: str):
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if not os.path.exists(self.file_path):
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading file {self.file_path}: {e}")
            return {}

    def save(self, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Error saving file {self.file_path}: {e}")

class TimelineStorage(Storage):
    def __init__(self, file_path: str = "data/timeline.json"):
        super().__init__(file_path)

    def append_daily_log(self, date_str: str, data: Dict[str, dict]):
        """
        Append daily price snapshot to timeline.
        Format:
        {
            "2023-10-27": { ... snapshot data ... },
            "2023-10-28": { ... }
        }
        """
        timeline = self.load()
        timeline[date_str] = data
        self.save(timeline)

    def get_recent_history(self, days: int = 7) -> Dict[str, Dict[str, dict]]:
        """Get history for the last N records (by date sorting)."""
        timeline = self.load()
        sorted_dates = sorted(timeline.keys(), reverse=True)
        recent_dates = sorted_dates[:days]
        
        # Return in chronological order
        result = {}
        for date in reversed(recent_dates):
            result[date] = timeline[date]
        return result
