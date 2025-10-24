import pathlib
from enum import StrEnum

from configuration.data_providers.data_provider import DataProvider
from configuration.type_utils import DataType
from .interfaces import DataLoader


class FileType(StrEnum):
    Text = 'rt',
    Binary = 'rb'


class FileDataProvider(DataProvider):
    def __init__(self, file_path: str, data_loader: DataLoader, file_type: FileType = FileType.Text):
        super().__init__()

        if file_path == '':
            self._file = None
        else:
            self._file = pathlib.Path(file_path)

        self._file_type = file_type
        self._data_loader = data_loader
        self._last_modified_time: float | None = None

    def _load_data(self) -> dict[str, DataType]:
        if self._file is None or not self._file.exists():
            return {}

        self._last_modified_time = self._file.stat().st_mtime
        with open(self._file, self._file_type) as fp:
            return self._data_loader(fp)

    def _reload_required(self) -> bool:
        if self._file is None:
            return False
        return self._last_modified_time is None or self._last_modified_time < self._file.stat().st_mtime
