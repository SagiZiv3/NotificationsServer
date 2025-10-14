import functools
import inspect

from .exceptions import UnannotatedParameterException, IncompatibleScopesError
from .interfaces import IServiceProvider, IServiceRegistrationHandler
from .models import RegisteredService


@functools.lru_cache
def _get_constructor[T](t: type[T]):
    return inspect.signature(t.__init__)


class ServiceConstructor:
    def __init__(self, service_reg_handler: IServiceRegistrationHandler):
        self.service_reg_handler = service_reg_handler

    def construct_type[T](self, service_provider: IServiceProvider, t: type[T]) -> T:
        registered_service: RegisteredService = self.service_reg_handler.get_required_registered_service_data(t)
        current_scope = registered_service.life_scope
        init = _get_constructor(t)
        kwargs = {}
        for name, param in init.parameters.items():
            if name == "self":
                continue

            ann = param.annotation
            if ann is inspect._empty:
                raise UnannotatedParameterException(name, t)

            # If the dependency is registered, resolve it according to its life scope
            dependency_registered_service = self.service_reg_handler.get_required_registered_service_data(ann)
            if dependency_registered_service.life_scope < current_scope:
                raise IncompatibleScopesError(dependency_registered_service, registered_service)

            dep_instance: T = service_provider.get_required_service(ann)

            kwargs[name] = dep_instance

        return t(**kwargs)
