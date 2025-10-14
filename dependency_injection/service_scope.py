from typing import Callable

from .models import ServiceIdentifier


class ServiceScope:
    def __init__(self) -> None:
        self._instances: dict[tuple[ServiceIdentifier, type], object] = {}

    def get_instance[T](self, identifier: ServiceIdentifier, implementation: type,
                        instantiation_method: Callable[[], T]) -> T:
        key = (identifier, implementation)
        if key not in self._instances:
            self._instances[key] = instantiation_method()

        return self._instances[key]

    def dispose_instances(self):
        for instance in self._instances.values():
            dispose_method = getattr(instance, 'dispose', None)
            if dispose_method:
                dispose_method()
        self._instances.clear()
