import contextlib
from typing import Protocol, Callable, Generator, Self, Sequence

from .models import RegisteredService

type InstantiationMethodType = Callable[[IServiceProvider], object]


class IServiceRegistrationHandler(Protocol):
    def is_service_registered[T](self, t: type[T]) -> bool:
        pass

    def get_registered_service_data[T](self, t: type[T]) -> RegisteredService | None:
        ...

    def get_required_registered_service_data[T](self, t: type[T]) -> RegisteredService:
        ...

    def get_registered_services_data[T](self, t: type[T]) -> Sequence[RegisteredService]:
        ...

    def get_instantiation_method[T](self, t: type[T], implementation_type: type) -> InstantiationMethodType | None:
        ...


class IServiceProvider(Protocol):
    def get_service[T](self, t: type[T]) -> T | None:
        ...

    def get_required_service[T](self, t: type[T]) -> T:
        ...

    def get_services[T](self, t: type[T]) -> Sequence[T]:
        ...


class IServiceScope(Protocol):
    @property
    def service_provider(self) -> IServiceProvider:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


class IServiceScopeFactory(Protocol):
    @contextlib.contextmanager
    def create_scope(self) -> Generator[IServiceScope, None, None]:
        ...


class IServiceConstructor(Protocol):
    def construct_type[T](self, service_provider: IServiceProvider, service: RegisteredService) -> T:
        ...


class IDependencyContainer(IServiceScopeFactory, IServiceRegistrationHandler, Protocol):
    def dispose(self) -> None:
        ...
