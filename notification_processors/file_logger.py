import datetime
import aiofiles
from models import Notification

from .notification_processor import NotificationProcessor, ProcessingResult


class FileLogger(NotificationProcessor):
    async def _process(self, notification: Notification) -> ProcessingResult:
        ts = datetime.datetime.now().isoformat()
        try:
            async with aiofiles.open(f"logs/{notification.source.lower()}.log", mode="a") as f:
                await f.write(f"[{ts}] {notification.severity.upper()}: {notification.title} - {notification.message}\n")
            return ProcessingResult.Success
        except:
            return ProcessingResult.Fail

def get_instance() -> NotificationProcessor:
    return FileLogger()
