import html

from telegram import Bot
from telegram.error import TelegramError

from models import Notification
from .configs import TelegramConfig
from .notification_processor import get_short_message
from .notification_publisher import NotificationPublisher, ProcessingResult


class TelegramNotificationPublisher(NotificationPublisher):
    def __init__(self, config: TelegramConfig):
        self._config = config

    async def _process(self, notification: Notification) -> ProcessingResult:
        chat_id = self._config.chat_id
        try:
            async with Bot(token=self._config.bot_token) as bot:
                await bot.send_message(chat_id=chat_id, text=_generate_text_for_notification(notification),
                                       parse_mode='HTML')
                return ProcessingResult.Success
        except TelegramError as e:
            # Optional: Log the error or handle specific cases
            print(f"Telegram API error: {e}")
            return ProcessingResult.Fail
        except Exception as e:
            # Catch other unexpected errors
            print(f"Unexpected error: {e}")
            return ProcessingResult.Fail


def _generate_text_for_notification(notification: Notification):
    icon = _get_severity_icon(notification.severity.lower())
    source = notification.source
    title = html.escape(notification.title)
    message = html.escape(get_short_message(notification))

    return (
        f"<b>{icon} {title}</b>\n"
        f"<i>Source:</i> <code>{source}</code>\n"
        f"<i>Severity:</i> <b>{notification.severity}</b>\n\n"
        f"{message}"
    )


def _get_severity_icon(severity: str) -> str:
    match severity.lower():
        case 'info' | 'notice':
            return "ℹ️"
        case 'warn' | 'warning':
            return "⚠️"
        case 'error':
            return "❌"
        case 'critical' | 'fatal':
            return "🔥"
        case _:
            return "📢"
