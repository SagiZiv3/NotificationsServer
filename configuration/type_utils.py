import functools
import inspect
from types import UnionType, NoneType
from typing import Mapping, ForwardRef
from typing import get_origin, Union, get_args, get_type_hints

type PrimitiveType = str | int | float | bool | None
type DataType = Mapping[str, DataType] | list[DataType] | PrimitiveType
_UNION_TYPES = (Union, UnionType)

PRIMITIVE_TYPES = (str, int, float, bool)


def is_optional_type(t: type) -> bool:
    return get_base_class(t) in _UNION_TYPES and NoneType in get_args(t)


def unwrap_optional(t: type) -> type:
    base = get_base_class(t)
    args = get_args(t)
    if base in _UNION_TYPES and NoneType in args:
        return next(arg for arg in args if arg is not NoneType)

    return t


def is_primitive_type(t: type | object) -> bool:
    if inspect.isclass(t):
        return t in PRIMITIVE_TYPES

    return type(t) in PRIMITIVE_TYPES


@functools.lru_cache
def get_base_class(t: type):
    origin = get_origin(t)
    return t if origin is None else origin


@functools.lru_cache
def get_constructor_annotated_parameters(t: type) -> list[inspect.Parameter]:
    global_ns = getattr(inspect.getmodule(t), "__dict__", {})

    return [_resolve_parameter(global_ns, param) for param in inspect.signature(t).parameters.values()
            if param.annotation is not param.empty and param.name.lower() != "self"]


@functools.lru_cache
def get_constructor_type_hints(t: type) -> Mapping[str, type]:
    hints = get_type_hints(t.__init__, include_extras=True)

    if not hints:
        hints = get_type_hints(t)

    return hints


def _resolve_parameter(global_ns: dict, parameter: inspect.Parameter) -> inspect.Parameter:
    ann = parameter.annotation
    if isinstance(ann, ForwardRef):
        ann = ann._evaluate(global_ns, None, recursive_guard=frozenset())  # resolve the ForwardRef
    return parameter.replace(annotation=ann)
