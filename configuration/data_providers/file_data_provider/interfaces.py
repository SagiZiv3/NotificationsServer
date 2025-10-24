from typing import Protocol, Any, IO

from configuration.type_utils import DataType


class DataLoader(Protocol):
    def __call__(self, stream: IO[str | bytes | Any]) -> dict[str, DataType]:
        ...
