from typing import Iterable

from .models import RegisteredService


class DependencyInjectionException(Exception):
    def __init__(self, error_message: str):
        super().__init__(error_message)


class UnregisteredTypeException(DependencyInjectionException):
    def __init__(self, t: type):
        super().__init__(f"Type '{t.__name__}' was not registered")
        self.type = t


class IncompatibleScopesError(DependencyInjectionException):
    def __init__(self, dependency_service: RegisteredService, dependent_service: RegisteredService):
        super().__init__(f"Can't inject service '{dependency_service.service_type.__name__}' with scope "
                         f"{dependency_service.life_scope.name} into service '{dependent_service.service_type.__name__}' "
                         f"with scope {dependent_service.life_scope.name}")
        self.dependency_service = dependency_service
        self.dependent_service = dependent_service


class UnannotatedParameterException(DependencyInjectionException):
    def __init__(self, parameter_name: str, t: type):
        super().__init__(
            f"Cannot resolve parameter '{parameter_name}' for {t.__name__}.__init__: missing type annotation")
        self.parameter_name = parameter_name
        self.type = t


class CircularDependencyException(DependencyInjectionException):
    def __init__(self, visited: Iterable[type], t: type):
        super().__init__(f"Circular dependency detected: {' → '.join(v.__name__ for v in visited)} → {t.__name__}")
