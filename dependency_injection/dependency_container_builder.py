from __future__ import annotations

from typing import Callable

from .dependency_container import DependencyContainer
from .interfaces import IServiceScopeFactory, InstantiationMethodType, IServiceProvider, IDependencyContainer
from .models import RegisteredService, LifeScope, ServiceIdentifier


class DependencyContainerBuilder:
    def __init__(self):
        self._registered_services: dict[ServiceIdentifier, list[RegisteredService]] = {}
        self._custom_instantiation_methods: dict[tuple[ServiceIdentifier, type], InstantiationMethodType] = {}

    def build(self) -> IDependencyContainer:
        instance = DependencyContainer(self._registered_services, self._custom_instantiation_methods)
        self.add_singleton(IServiceScopeFactory, DependencyContainer, lambda _: instance)
        return instance

    def add_singleton[TService, TImplementation: TService](self, service_type: type[TService],
                                                           implementation_type: type[TImplementation] | None = None,
                                                           instantiation_method: Callable[[
                                                               IServiceProvider], TImplementation] = None) -> DependencyContainerBuilder:
        self._add_service(service_type, implementation_type or service_type, LifeScope.Singleton, instantiation_method)
        return self

    def add_scoped[TService, TImplementation: TService](self, service_type: type[TService],
                                                        implementation_type: type[TImplementation] | None = None,
                                                        instantiation_method: InstantiationMethodType = None) -> DependencyContainerBuilder:
        self._add_service(service_type, implementation_type or service_type, LifeScope.Scoped, instantiation_method)
        return self

    def add_transient[TService, TImplementation: TService](self, service_type: type[TService],
                                                           implementation_type: type[TImplementation] | None = None,
                                                           instantiation_method: InstantiationMethodType = None) -> DependencyContainerBuilder:
        self._add_service(service_type, implementation_type or service_type, LifeScope.Transient, instantiation_method)
        return self

    def _add_service[TService, TImplementation:TService](self, service_type: type[TService],
                                                         implementation_type: type[TImplementation],
                                                         life_scope: LifeScope,
                                                         instantiation_method: InstantiationMethodType | None):
        service_identifier = ServiceIdentifier.from_type(service_type)
        registered_services = self._registered_services.get(service_identifier, [])
        registered_services.append(RegisteredService(life_scope, service_type, implementation_type))
        self._registered_services[service_identifier] = registered_services

        if instantiation_method is not None:
            self._custom_instantiation_methods[(service_identifier, implementation_type)] = instantiation_method
