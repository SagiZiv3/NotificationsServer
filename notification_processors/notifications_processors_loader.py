import importlib
import pkgutil
from types import FunctionType, ModuleType
from typing import Final, Sequence, Iterable

from .base_class import NotificationProcessor

GET_INSTANCE_METHOD: Final[str] = "get_instance"


def load_notification_processors() -> Sequence[NotificationProcessor]:
    processors_list: list[NotificationProcessor] = []

    for module in _find_implementations():
        get_instance_function: FunctionType = getattr(module, GET_INSTANCE_METHOD)
        processors_list.append(get_instance_function())

    print(f"Loaded {len(processors_list)} processor(s): {[p.__class__.__name__ for p in processors_list]}")
    return processors_list


def _find_implementations() -> Iterable[ModuleType]:
    package = importlib.import_module(__package__)
    package_name = package.__name__

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")
        if not hasattr(module, GET_INSTANCE_METHOD):
            continue

        yield module
