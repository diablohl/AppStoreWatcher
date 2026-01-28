import json
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, file_path: str = "data/history.json"):
        self.file_path = file_path
        self._ensure_directory()

    def _ensure_directory(self):
        dirname = os.path.dirname(self.file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    def load(self) -> Dict[str, dict]:
        """Load history from JSON file."""
        if not os.path.exists(self.file_path):
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading history file: {e}")
            return {}

    def save(self, data: Dict[str, dict]):
        """Save history to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Error saving history file: {e}")
