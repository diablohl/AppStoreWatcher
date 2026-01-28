import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AppStoreAPI:
    BASE_URL = "https://itunes.apple.com/lookup"

    @staticmethod
    def fetch_app_details(app_ids: List[str], country: str = "cn") -> Dict[str, dict]:
        """
        Fetch app details from iTunes API.
        
        Args:
            app_ids: List of App Store IDs (as strings or ints).
            country: Two-letter country code (e.g., 'cn', 'us').
            
        Returns:
            Dictionary mapping app_id (str) to app details.
        """
        if not app_ids:
            return {}

        params = {
            "id": ",".join(map(str, app_ids)),
            "country": country
        }

        try:
            response = requests.get(AppStoreAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = {}
            if "results" in data:
                for item in data["results"]:
                    # Ensure app_id is string for consistency
                    app_id = str(item.get("trackId"))
                    results[app_id] = item
            
            return results
        except requests.RequestException as e:
            logger.error(f"Error fetching data from App Store API: {e}")
            return {}
