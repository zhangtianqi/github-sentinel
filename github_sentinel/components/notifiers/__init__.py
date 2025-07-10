from github_sentinel.components.config_loader import config
from .slack_notifier import SlackNotifier
# from .discord_notifier import DiscordNotifier # Uncomment when implemented

def dispatch_notification(report: str):
    """
    Dispatches the report to all enabled notification channels.
    """
    print("Dispatching notifications...")
    
    if config.get('notifications', {}).get('slack', {}).get('enabled'):
        print("Slack notifier is enabled.")
        try:
            SlackNotifier().send(report)
        except Exception as e:
            print(f"Error sending to Slack: {e}")
    
    # Example for Discord
    # if config.get('notifications', {}).get('discord', {}).get('enabled'):
    #     print("Discord notifier is enabled.")
    #     try:
    #         DiscordNotifier().send(report)
    #     except Exception as e:
    #         print(f"Error sending to Discord: {e}")
