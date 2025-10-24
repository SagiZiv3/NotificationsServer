from enum import StrEnum
from typing import Any, Awaitable, NamedTuple, Callable

type EndpointFunctionType = Callable[..., Any | Awaitable[Any]]


class Method(StrEnum):
    Get = "GET"
    Post = "POST"
    Put = "PUT"
    Delete = "DELETE"
    Patch = "PATCH"
    Head = "HEAD"
    Options = "OPTIONS"
    Trace = "TRACE"


class Endpoint(NamedTuple):
    route: str
    method: Method
    function: EndpointFunctionType
