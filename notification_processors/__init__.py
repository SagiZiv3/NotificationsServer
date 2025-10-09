import importlib
import pkgutil
import inspect
from typing import Protocol
from models import Notification


class NotificationProcessor(Protocol):
    async def process(self, notification: Notification) -> None:
        ...


def load_processors() -> list[NotificationProcessor]:
    """Dynamically load all processors from this package."""
    processors = []
    package = __name__

    for _, module_name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{package}.{module_name}")

        # Find classes that implement the protocol
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, "process"):
                instance = obj()
                processors.append(instance)

    print(f"Loaded {len(processors)} processor(s): {[p.__class__.__name__ for p in processors]}")
    return processors
