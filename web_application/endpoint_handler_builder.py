import contextvars
import dataclasses
from types import NoneType, UnionType
from typing import Callable, Generator, Mapping, Self, Annotated, get_type_hints, final, Union
from typing import get_origin, get_args, Sequence

import typing_extensions
from fastapi import Depends

from dependency_injection import IServiceScopeFactory, IServiceScope, IServiceRegistrationHandler
from .models import Endpoint


@dataclasses.dataclass(eq=False, slots=True)
class _RequestState:
    di_scope: IServiceScope | None
    counter: int = 0


@final
class _RequestsHandler:
    _request_state: contextvars.ContextVar[_RequestState] = contextvars.ContextVar('_request_state',
                                                                                   default=_RequestState(None))

    def __init__(self, scope_factory: IServiceScopeFactory):
        self._scope_factory = scope_factory

    def get_scope(self) -> IServiceScope:
        request_state = self._get_request_state()
        scope = request_state.di_scope

        return scope

    def on_request_started(self):
        request_state = self._get_request_state()
        request_state.counter += 1
        _RequestsHandler._request_state.set(request_state)

    def on_request_completed(self):
        request_state = self._get_request_state()
        request_state.counter -= 1

        if request_state.counter == 0:
            self._dispose_scope(request_state)

        _RequestsHandler._request_state.set(request_state)

    def _dispose_scope(self, request_state: _RequestState):
        request_state.di_scope.__exit__(None, None, None)
        request_state.di_scope = None

    def _get_request_state(self) -> _RequestState:
        request_state = _RequestsHandler._request_state.get()
        if request_state.di_scope is None:
            scope = self._scope_factory.create_scope().__enter__()
            request_state.di_scope = scope
            _RequestsHandler._request_state.set(request_state)

        return request_state


def _inject(t: type, request_handler: _RequestsHandler) -> Callable[[], Generator[object, None, None]]:
    origin = get_origin(t)
    args = get_args(t)

    def dependency() -> Generator[object | Sequence[object], None, None]:
        scope = request_handler.get_scope()
        try:
            request_handler.on_request_started()
            if origin is None:
                yield scope.service_provider.get_required_service(t)
            elif issubclass(origin, Sequence):
                elem_type = args[0]
                services = scope.service_provider.get_services(elem_type)
                yield origin(services) if origin in (tuple, list) else services
            elif origin in (Union, UnionType):
                non_none_type = args[0] if args[1] is NoneType else args[0]
                yield scope.service_provider.get_service(non_none_type)
        finally:
            request_handler.on_request_completed()

    return dependency


class EndpointHandlerBuilder:
    def __init__(self, endpoint: Endpoint, scope_factory: IServiceScopeFactory,
                 di_registration_handler: IServiceRegistrationHandler,
                 add_endpoint_callback: Callable[[Endpoint], None]):
        self._endpoint = endpoint
        self._request_handler = _RequestsHandler(scope_factory)
        self._di_registration_handler = di_registration_handler
        self._add_endpoint_callback = add_endpoint_callback

    def with_dependencies(self, types_override: Mapping[str, type] = None) -> Self:
        function_annotations = get_type_hints(self._endpoint.function, include_extras=True)
        updated_annotations: dict[str, type] = {name: ann for name, ann in function_annotations.items()
                                                if self._is_di_injectable(ann)}

        if types_override is not None:
            updated_annotations.update({name: t for name, t in types_override.items()
                                        if name in function_annotations.keys()})

        for param_name, t in updated_annotations.items():
            function_annotations[param_name] = Annotated[
                t,
                Depends(_inject(t, self._request_handler), use_cache=False)
            ]

        self._endpoint.function.__annotations__ = function_annotations
        return self

    def apply(self):
        self._add_endpoint_callback(self._endpoint)

    def _is_di_injectable(self, annotation: type) -> bool:
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is None:
            return self._is_registered(annotation)

        match args:
            case (*_, ) if origin in (Annotated, typing_extensions.Annotated):
                return False
            case (arg1, arg2) if origin in (UnionType, Union) and NoneType in args:
                non_none_arg = arg1 if arg2 is NoneType else arg2
                return self._is_di_injectable(non_none_arg)
            case (arg, ) if isinstance(origin, type) and issubclass(origin, Sequence):
                return self._is_registered(arg)

        return False

    def _is_registered(self, t: type) -> bool:
        return isinstance(t, type) and self._di_registration_handler.is_service_registered(t)
