from abc import ABC, abstractmethod

from models import Notification


class NotificationProcessor(ABC):
    @abstractmethod
    async def process(self, notification: Notification) -> None:
        ...
