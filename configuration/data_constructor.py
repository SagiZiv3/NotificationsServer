from typing import get_args, Mapping

from .type_utils import DataType, PrimitiveType
from .type_utils import unwrap_optional, get_base_class, get_constructor_annotated_parameters

_sentinel = object()


def construct_object[T](data: DataType, t: type[T]) -> T | None:
    base = unwrap_optional(t)

    if base is not t and data is None:
        return None

    t = base

    if isinstance(data, dict):
        if issubclass(get_base_class(t), dict):
            return _construct_dict(data, t)
        return _construct_data(data, t)
    elif isinstance(data, list):
        return _construct_list(data, t)
    elif isinstance(data, (str, int, float, bool)):
        return _construct_primitive(data, t)
    else:
        raise TypeError(f'Unknown data-type {type(data).__name__}')


def _construct_data[T](data: Mapping[str, DataType], t: type[T]) -> T:
    params = get_constructor_annotated_parameters(t)
    kwargs: dict[str, DataType] = {}

    for param in params:
        value = data.get(param.name, _sentinel)
        if value is _sentinel:
            if param.default is not param.empty:
                continue
            raise TypeError(f"Missing required field: {param.name} for {t.__name__}")

        annotation = param.annotation
        kwargs[param.name] = construct_object(value, annotation)

    return t(**kwargs)


def _construct_dict[T](data: Mapping[str, DataType], t: type[T]) -> Mapping[str, T]:
    args = get_args(t)
    item_type = args[1] if args else object

    return {key: construct_object(item, item_type) for key, item in data.items()}


def _construct_list[T](data: list[DataType], t: type[T]) -> list[T]:
    args = get_args(t)
    item_type = args[0] if args else object

    return [construct_object(item, item_type) for item in data]


def _construct_primitive[T](data: PrimitiveType, t: type[T]) -> T:
    if t is bool and isinstance(data, str):
        return data.lower() in ('true', '1', 'yes')

    return t(data)
