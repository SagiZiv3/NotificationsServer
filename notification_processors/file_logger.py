import datetime
import aiofiles
from models import Notification


class FileLogger:
    async def process(self, notification: Notification) -> None:
        ts = datetime.datetime.now().isoformat()
        async with aiofiles.open(f"logs/{notification.source.lower()}.log", mode="a") as f:
            await f.write(f"[{ts}] {notification.severity.upper()}: {notification.title} - {notification.message}\n")
