from abc import ABC, abstractmethod

from configuration.type_utils import DataType


class DataProvider(ABC):
    def __init__(self):
        self._data: dict[str, DataType] = {}

    def load(self, reload: bool = False) -> dict[str, DataType]:
        if not reload and self._data:
            return self._data

        self._data = self._load_data()
        return self._data

    def reload_required(self) -> bool:
        return self._reload_required()

    @abstractmethod
    def _load_data(self) -> dict[str, DataType]:
        pass

    @abstractmethod
    def _reload_required(self) -> bool:
        pass
