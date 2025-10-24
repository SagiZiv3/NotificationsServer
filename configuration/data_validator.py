import inspect
import re
from collections.abc import Callable
from typing import NoReturn, get_args, Mapping

from .exceptions import UnexpectedConstructorParametersError, MissingConstructorParametersError, ConfigurationException
from .type_utils import DataType, PrimitiveType
from .type_utils import unwrap_optional, get_base_class, get_constructor_annotated_parameters, \
    get_constructor_type_hints, is_primitive_type, PRIMITIVE_TYPES


def validate_data(data: DataType, t: type) -> None | NoReturn:
    base = unwrap_optional(t)

    if base is not t and data is None:
        return

    t = base
    _validate_type_match(data, t)
    if isinstance(data, dict):
        if issubclass(get_base_class(t), dict):
            _validate_dict(data, t)
        else:
            _validate_object(data, t)
    elif isinstance(data, list):
        _validate_list(data, t)
    elif is_primitive_type(data):
        _validate_primitive(data, t)


def _validate_type_match(data: DataType, t: type) -> None | NoReturn:
    base = get_base_class(t)
    expected_types: tuple[type, ...] = ()
    if issubclass(base, list):
        expected_types = (list,)
    elif is_primitive_type(t):
        expected_types = PRIMITIVE_TYPES
    elif inspect.isclass(t) or issubclass(base, dict):
        expected_types = (dict,)

    if expected_types and not isinstance(data, expected_types):
        raise TypeError(f"Expected {', '.join(x.__name__ for x in expected_types)}, got '{type(data).__name__}'")


def _validate_object(data: dict[str, DataType], t: type) -> None | NoReturn:
    params = get_constructor_annotated_parameters(t)
    _detect_positional_only_parameters(params, t)
    optional_params, required_params = _get_optional_and_required_params(params)
    data_params = set(data.keys())
    missing_parameters = required_params - data_params

    if missing_parameters:
        raise MissingConstructorParametersError(t, missing_parameters)

    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)
    if has_kwargs:
        _validate_object_constructor(data, t)
        return

    valid_params = required_params | optional_params
    extra_parameters = data_params - valid_params
    if extra_parameters:
        raise UnexpectedConstructorParametersError(t, extra_parameters)

    _validate_object_constructor(data, t)


def _get_optional_and_required_params(params: list[inspect.Parameter]) -> tuple[set[str], set[str]]:
    required_params: set[str] = {
        p.name
        for p in params
        if p.default is p.empty and p.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY
        )
    }
    optional_params: set[str] = {
        p.name
        for p in params
        if p.default is not p.empty
    }

    return optional_params, required_params


def _detect_positional_only_parameters(params: list[inspect.Parameter], t: type):
    pos_only = any(p.name for p in params if p.kind == inspect.Parameter.POSITIONAL_ONLY)
    if pos_only:
        raise TypeError(
            f"{t.__name__}.__init__ has positional-only parameters, "
            f"which cannot be passed via keyword arguments (**data)."
        )


def _validate_object_constructor(data: dict[str, DataType], t: type):
    hints = get_constructor_type_hints(t)

    for key, value in data.items():
        if key not in hints:
            continue

        field_type = hints[key]
        try:
            validate_data(value, field_type)
        except (TypeError, ConfigurationException) as e:
            raise TypeError(
                f"In field '{key}' of {t.__name__}: {e}"
            ) from e


def _validate_dict(data: dict[str, DataType], t: type) -> None | NoReturn:
    args = get_args(t)
    item_type = args[1] if args else object
    for key, item in data.items():
        try:
            validate_data(item, item_type)
        except (TypeError, ConfigurationException) as e:
            raise TypeError(
                f"In key {key} of {t.__name__}: {e}"
            ) from e


def _validate_list(data: list[DataType], t: type) -> None | NoReturn:
    args = get_args(t)
    item_type = args[0] if args else object

    for i, item in enumerate(data):
        try:
            validate_data(item, item_type)
        except (TypeError, ConfigurationException) as e:
            raise TypeError(
                f"At index '{i}' of {t.__name__}: {e}"
            ) from e


def _validate_primitive(data: PrimitiveType, t: type) -> None | NoReturn:
    if isinstance(data, t) or issubclass(t, str):
        return

    validation: Mapping[type, Callable[[str], bool]] = {
        int: lambda s: s.isdigit() or s[1:].isdigit(),
        float: lambda s: re.match(r'^[+-]?\d+(\.\d+)?$', s) is not None,
        bool: lambda s: s.lower() in ('true', 'false', '1', '0', 'yes', 'no')
    }

    validator = validation.get(t, None)
    if not validator:
        raise TypeError(f"Can't parse '{data}' to type {t.__name__}, unknown parser")

    if len(data.strip()) == 0 or not validator(data.strip()):
        raise TypeError(f"Can't parse '{data}' to type {t.__name__}, invalid input")
