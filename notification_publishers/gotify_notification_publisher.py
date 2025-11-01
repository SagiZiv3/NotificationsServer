import requests_async

from models import Notification
from .configs import GotifyConfig
from .notification_publisher import NotificationPublisher, ProcessingResult


class GotifyNotificationPublisher(NotificationPublisher):
    def __init__(self, config: GotifyConfig):
        self._config = config

    async def _process(self, notification: Notification) -> ProcessingResult:
        api_token = self._get_api_token_for_source(notification.source)

        if not api_token:
            print(f'Unable to find API token for source {notification.source}')
            return ProcessingResult.Skip

        server_url = self._config.server_url
        resp = await requests_async.post(f"https://{server_url}/message?token={api_token}", json={
            "message": notification.message,
            "priority": _severity_to_priority(notification.severity),
            "title": notification.title
        })
        return ProcessingResult.Success if resp.is_success else ProcessingResult.Fail

    def _get_api_token_for_source(self, source: str) -> str:
        token = self._config.api_token_per_source.get(source, None)
        if not token:
            return self._config.general_api_token

        return token


def _severity_to_priority(severity: str) -> int:
    match severity.lower():
        case 'debug':
            return 1
        case 'info' | 'notice':
            return 3
        case 'warn' | 'warning':
            return 5
        case 'error':
            return 9
        case 'critical' | 'fatal':
            return 10
        case _:
            return 3
