import requests
from .base_notifier import BaseNotifier
from ..config_loader import config

class SlackNotifier(BaseNotifier):
    def __init__(self):
        self.webhook_url = config['notifications']['slack'].get('webhook_url')
        if not self.webhook_url:
            raise ValueError("Slack webhook URL is not configured in config.yaml")

    def send(self, message: str):
        # Slack has a message size limit, truncate if necessary
        if len(message) > 3800:
            message = message[:3800] + "\n\n... (message truncated)"

        # Slack's 'mrkdwn' format is very similar to GitHub's Markdown
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print("Successfully sent notification to Slack.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack notification: {e}")
            # Re-raise or handle as needed
            raise
