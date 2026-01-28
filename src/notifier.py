import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Notifier:
    def notify(self, changes: List[Dict]):
        raise NotImplementedError

class EmailNotifier(Notifier):
    def __init__(self, host: str, port: int, user: str, password: str, recipients: List[str]):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.recipients = recipients

    def notify(self, changes: List[Dict]):
        if not changes or not self.recipients:
            return

        subject = f"App Store Price Alert: {len(changes)} app(s) changed price"
        body = self._format_body(changes)
        
        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = ", ".join(self.recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP_SSL(self.host, self.port) as server:
                server.login(self.user, self.password)
                server.send_message(msg)
            logger.info("Email notification sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def _format_body(self, changes: List[Dict]) -> str:
        lines = ["The following apps have changed price:\n"]
        for change in changes:
            name = change.get('name', 'Unknown App')
            old_price = change.get('old_price', 'N/A')
            new_price = change.get('new_price', 'N/A')
            currency = change.get('currency', '')
            url = change.get('url', '')
            
            lines.append(f"- {name}")
            lines.append(f"  Price: {old_price} -> {new_price} {currency}")
            lines.append(f"  Link: {url}")
            lines.append("")
        return "\n".join(lines)

class WebhookNotifier(Notifier):
    def __init__(self, url: str):
        self.url = url

    def notify(self, changes: List[Dict]):
        if not changes or not self.url:
            return

        # Prepare message for generic webhook (e.g. Feishu/Slack compatible format often preferred)
        # Here implementing a simple JSON payload. 
        # For Feishu/Lark specifically, the structure might need adjustment (e.g. msg_type: text or interactive)
        # We will assume a simple text or markdown payload for now, or adapt based on user preference later if needed.
        # This implementation tries to be generic but structured.
        
        # Example for Feishu text message
        text_content = self._format_content(changes)
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": text_content
            }
        }
        
        # Some webhooks (like Slack) just take {"text": "..."}
        # To be safe, we can try to detect or just send a flexible payload.
        # Given the "Feishu/Slack/DingTalk" requirement, let's keep it simple text first.
        # If it's a Slack webhook, it usually ends in hooks.slack.com
        
        if "feishu" in self.url or "lark" in self.url:
             payload = {
                "msg_type": "text",
                "content": {
                    "text": text_content
                }
            }
        elif "slack" in self.url:
             payload = {"text": text_content}
        elif "dingtalk" in self.url:
             payload = {
                 "msgtype": "text",
                 "text": {
                     "content": text_content
                 }
             }
        else:
             # Default fallback
             payload = {"text": text_content}

        try:
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code >= 400:
                logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
            else:
                logger.info("Webhook notification sent successfully.")
        except requests.RequestException as e:
            logger.error(f"Failed to send webhook: {e}")

    def _format_content(self, changes: List[Dict]) -> str:
        lines = ["App Store Price Alert:"]
        for change in changes:
            name = change.get('name', 'Unknown App')
            old_price = change.get('old_price', 'N/A')
            new_price = change.get('new_price', 'N/A')
            currency = change.get('currency', '')
            url = change.get('url', '')
            lines.append(f"\n{name}\n{old_price} -> {new_price} {currency}\n{url}")
        return "\n".join(lines)
