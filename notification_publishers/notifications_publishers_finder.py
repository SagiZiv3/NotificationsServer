import importlib
import inspect
import pkgutil
from typing import Iterator

import notification_publishers
from .notification_publisher import NotificationPublisher


def find_notification_publishers() -> Iterator[type[NotificationPublisher]]:
    package = notification_publishers
    package_name = package.__name__

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")

        yield from (t for _, t in inspect.getmembers(module, predicate=_is_notification_processor_implementation))


def _is_notification_processor_implementation(t: type) -> bool:
    return inspect.isclass(t) and issubclass(t, NotificationPublisher) and not inspect.isabstract(t)
