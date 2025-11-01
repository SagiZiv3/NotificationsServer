from abc import ABC, abstractmethod
from enum import Enum

from models import Notification


class ProcessingResult(Enum):
    Success = 0
    Fail = 1
    Skip = 2


class NotificationPublisher(ABC):
    async def process(self, notification: Notification) -> ProcessingResult:
        try:
            return await self._process(notification)
        except:
            return ProcessingResult.Fail

    @abstractmethod
    async def _process(self, notification: Notification) -> ProcessingResult:
        ...
