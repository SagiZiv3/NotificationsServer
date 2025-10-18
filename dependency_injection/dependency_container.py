import contextlib
from typing import Mapping, Generator, Sequence

from .exceptions import UnregisteredTypeException
from .interfaces import InstantiationMethodType, IServiceScope
from .models import RegisteredService, ServiceIdentifier
from .scoped_service_provider import ScopedServiceProvider
from .service_constructor import ServiceConstructor


class DependencyContainer:
    def __init__(self, registered_services: Mapping[ServiceIdentifier, Sequence[RegisteredService]],
                 custom_instantiation_methods: Mapping[tuple[ServiceIdentifier, type], InstantiationMethodType]):
        self._registered_services = registered_services
        self._custom_instantiation_methods = custom_instantiation_methods
        self._service_constructor = ServiceConstructor(self)
        self._root_scope = ScopedServiceProvider(self._service_constructor, self)

    @contextlib.contextmanager
    def create_scope(self) -> Generator[IServiceScope, None, None]:
        with ScopedServiceProvider(self._service_constructor, self, self._root_scope) as scope:
            yield scope

    def dispose(self):
        self._root_scope.dispose()

    def is_service_registered[T](self, t: type[T]) -> bool:
        identifier = ServiceIdentifier.from_type(t)
        return identifier in self._registered_services


    def get_registered_service_data[T](self, t: type[T]) -> RegisteredService | None:
        registered_services = self.get_registered_services_data(t)

        if len(registered_services) == 0:
            return None

        return registered_services[-1]

    def get_required_registered_service_data[T](self, t: type[T]) -> RegisteredService:
        service = self.get_registered_service_data(t)
        if service is None:
            raise UnregisteredTypeException(t)

        return service

    def get_registered_services_data[T](self, t: type[T]) -> Sequence[RegisteredService]:
        identifier = ServiceIdentifier.from_type(t)
        return self._registered_services.get(identifier, [])

    def get_instantiation_method[T](self, t: type[T], implementation_type: type) -> InstantiationMethodType | None:
        identifier = ServiceIdentifier.from_type(t)
        return self._custom_instantiation_methods.get((identifier, implementation_type), None)
