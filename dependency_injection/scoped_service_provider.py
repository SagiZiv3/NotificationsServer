import functools
from typing import Sequence

from .exceptions import UnregisteredTypeException, CircularDependencyException, IncompatibleScopesError
from .interfaces import IServiceConstructor, IServiceRegistrationHandler, IServiceProvider, InstantiationMethodType
from .models import LifeScope, ServiceIdentifier, RegisteredService
from .service_scope import ServiceScope


class ScopedServiceProvider:
    def __init__(self, service_constructor: IServiceConstructor,
                 service_reg_handler: IServiceRegistrationHandler,
                 root_service_provider: IServiceProvider | None = None):
        self._root_service_provider = root_service_provider
        self._service_constructor = service_constructor
        self._service_reg_handler = service_reg_handler
        self._scope = ServiceScope()
        self._visited: list[RegisteredService] = []
        self._disposed = False

    @property
    def service_provider(self) -> IServiceProvider:
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    def dispose(self):
        if self._disposed:
            return

        self._scope.dispose_instances()
        self._disposed = True

    def get_service[T](self, t: type[T]) -> T | None:
        service = self._service_reg_handler.get_registered_service_data(t)
        if service is None:
            return None

        return self._resolve_service(t, service)

    def get_required_service[T](self, t: type[T]) -> T:
        service = self.get_service(t)

        if service is None:
            raise UnregisteredTypeException(t)

        return service

    def get_services[T](self, t: type[T]) -> Sequence[T]:
        registered_services = self._service_reg_handler.get_registered_services_data(t)
        services: list[T] = []

        for registered_service in registered_services:
            services.append(self._resolve_service(t, registered_service))

        return services

    def _resolve_service[T](self, t: type[T], service: RegisteredService) -> T:
        self._check_dependency_constraints(service, t)

        self._visited.append(service)
        instantiation_method = self._get_instantiation_method(service, t)
        try:
            return self._instantiate_service(instantiation_method, service, t)
        finally:
            self._visited.remove(service)

    def _check_dependency_constraints[T](self, service: RegisteredService, t: type[T]):
        if service in self._visited:
            raise CircularDependencyException(map(lambda s: s.implementation_type, self._visited), t)

        last_visited_service = self._visited[-1] if self._visited else None
        if last_visited_service is not None and service.life_scope < last_visited_service.life_scope:
            raise IncompatibleScopesError(service, last_visited_service)

    def _get_instantiation_method[T](self, service: RegisteredService, t: type[T]) -> InstantiationMethodType:
        instantiation_method = self._service_reg_handler.get_instantiation_method(t, service.implementation_type)

        if instantiation_method is None:
            instantiation_method = functools.partial(self._service_constructor.construct_type,
                                                     t=service.implementation_type)
        return instantiation_method

    def _instantiate_service[T](self, instantiation_method: InstantiationMethodType, service: RegisteredService,
                                t: type[T]) -> object:
        if service.life_scope is LifeScope.Transient:
            return instantiation_method(self.service_provider)

        sp = self._root_service_provider if service.life_scope is LifeScope.Singleton else self

        return sp._scope.get_instance(ServiceIdentifier.from_type(t), service.implementation_type,
                                      lambda: instantiation_method(self.service_provider))
