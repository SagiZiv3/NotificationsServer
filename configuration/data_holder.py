from __future__ import annotations

from typing import Sequence, Mapping

from .data_constructor import construct_object
from .data_providers import DataProvider
from .data_validator import validate_data
from .type_utils import DataType
from .constants import ROOT_PATH, PATH_DELIMITER

_sentinel = object()


class DataHolder:
    def __init__(self, data_providers: Sequence[DataProvider]):
        self._data_providers = data_providers
        self._data: dict[str, DataType] = {}

    def get_value[T](self, path: str, t: type[T]) -> T | None:
        self._refresh_data()
        sub_data = self._get_sub_data(path)

        if sub_data is _sentinel:
            return None

        validate_data(sub_data, t)
        return construct_object(sub_data, t)

    def is_valid_path(self, path: str):
        self._refresh_data()

        sub_data = self._get_sub_data(path)
        return sub_data is not _sentinel

    def _get_sub_data(self, path: str) -> DataType | type(_sentinel):
        sub_data = self._data

        if path is ROOT_PATH:
            return sub_data

        path_sections = path.split(PATH_DELIMITER)

        for section in path_sections:
            if not isinstance(sub_data, Mapping):
                return _sentinel
            sub_data = sub_data.get(section, _sentinel)
            if sub_data is _sentinel:
                return _sentinel

        return sub_data

    def _refresh_data(self):
        if not any(provider.reload_required() for provider in self._data_providers):
            return

        self._data.clear()
        for provider in self._data_providers:
            _deep_update(self._data, provider.load(provider.reload_required()))

def _deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.setdefault(k, {}), dict):
            _deep_update(d[k], v)
        else:
            d[k] = v
    return d
