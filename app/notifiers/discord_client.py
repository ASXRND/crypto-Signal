"""Notify a user via discord
"""

import structlog
try:
    from discord_webhook import DiscordWebhook
except ImportError:
    raise ImportError(
        "Пакет 'discord_webhook' не установлен. Установите его командой: pip install discord-webhook --break-system-packages"
    )

class DiscordNotifier():
    """Class for handling Discord notifications
    """

    def __init__(self, webhook, username, avatar=None):
        """Initialize DiscordNotifier class

        Args:
            webhook (str): Discord web hook to allow message sending.
            username (str): Display name for the discord bot.
            avatar (str, optional): Defaults to None. Url of an image to use as an avatar.
        """

        self.logger = structlog.get_logger()
        self.discord_username = username
        self.webhook_url = webhook
        self.avatar_url = avatar


    def notify(self, message):
        """Sends the message.

        Args:
            message (str): The message to send.
        """

        webhook = DiscordWebhook(url=self.webhook_url, username=self.discord_username, avatar_url=self.avatar_url, content=message)
        response = webhook.execute()
        if response.status_code != 200 and response.status_code != 204:
            self.logger.error(f"Discord notification failed: {response.status_code} - {response.text}")
