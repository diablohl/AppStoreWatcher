import os
import yaml
import logging
import argparse
import datetime
from typing import List, Dict
from api import AppStoreAPI
from storage import Storage, TimelineStorage
from notifier import EmailNotifier, WebhookNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_env_var(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def main():
    parser = argparse.ArgumentParser(description="App Store Price Watcher")
    parser.add_argument("--config", default="config/apps.yaml", help="Path to config file")
    parser.add_argument("--data", default="data/history.json", help="Path to data file")
    parser.add_argument("--timeline", default="data/timeline.json", help="Path to timeline file")
    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return

    apps_config = config.get("apps", [])
    if not apps_config:
        logger.warning("No apps configured to monitor.")
        return

    # Group apps by country for efficient API calls
    apps_by_country = {}
    for app in apps_config:
        country = app.get("country", "cn")
        apps_by_country.setdefault(country, []).append(app)

    # Initialize storage
    storage = Storage(args.data)
    history = storage.load()
    
    timeline_storage = TimelineStorage(args.timeline)
    
    # Initialize notifiers
    notifiers = []
    email_notifier = None
    
    # Email Notifier
    email_host = get_env_var("EMAIL_HOST")
    email_user = get_env_var("EMAIL_USER")
    email_pass = get_env_var("EMAIL_PASS")
    email_port = int(get_env_var("EMAIL_PORT", "465"))
    email_to = get_env_var("EMAIL_TO")
    
    if email_host and email_user and email_pass and email_to:
        recipients = [r.strip() for r in email_to.split(",")]
        email_notifier = EmailNotifier(email_host, email_port, email_user, email_pass, recipients)
        notifiers.append(email_notifier)
    
    # Webhook Notifier
    webhook_url = get_env_var("WEBHOOK_URL")
    if webhook_url:
        notifiers.append(WebhookNotifier(webhook_url))

    changes = []
    current_data_map = {}

    # Fetch current data
    for country, apps in apps_by_country.items():
        app_ids = [app["id"] for app in apps]
        logger.info(f"Fetching data for {len(app_ids)} apps in {country}...")
        
        api_results = AppStoreAPI.fetch_app_details(app_ids, country)
        
        for app in apps:
            app_id = str(app["id"])
            if app_id not in api_results:
                logger.warning(f"Could not fetch details for app ID {app_id}")
                continue

            details = api_results[app_id]
            current_price = details.get("price", 0.0)
            currency = details.get("currency", "")
            track_name = details.get("trackName", app.get("name", "Unknown"))
            track_view_url = details.get("trackViewUrl", "")
            
            # Save relevant data
            current_data_map[app_id] = {
                "name": track_name,
                "price": current_price,
                "currency": currency,
                "url": track_view_url,
                "country": country
            }

            # Check for changes
            previous_info = history.get(app_id)
            if previous_info:
                previous_price = previous_info.get("price")
                if previous_price is not None and previous_price != current_price:
                    logger.info(f"Price change detected for {track_name}: {previous_price} -> {current_price}")
                    changes.append({
                        "name": track_name,
                        "old_price": previous_price,
                        "new_price": current_price,
                        "currency": currency,
                        "url": track_view_url
                    })
            else:
                logger.info(f"New app tracked: {track_name} at {current_price} {currency}")

    # Send notifications for immediate changes
    if changes:
        logger.info(f"Sending notifications for {len(changes)} changes...")
        for notifier in notifiers:
            notifier.notify(changes)
    else:
        logger.info("No price changes detected.")

    # Update history (current state)
    history.update(current_data_map)
    storage.save(history)

    # Update timeline (daily log)
    today_str = datetime.date.today().isoformat()
    timeline_storage.append_daily_log(today_str, current_data_map)
    logger.info(f"Saved daily log for {today_str}")

    # Weekly Report Check (Sunday)
    # 0 = Monday, 6 = Sunday
    if datetime.date.today().weekday() == 6:
        logger.info("Today is Sunday. Generating weekly report...")
        if email_notifier:
            # Get last 7 days of history
            recent_history = timeline_storage.get_recent_history(days=7)
            email_notifier.send_weekly_report(recent_history)
        else:
            logger.warning("Email notifier not configured. Skipping weekly report.")

if __name__ == "__main__":
    main()
