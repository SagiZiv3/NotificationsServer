from __future__ import annotations

from typing import Protocol


class IConfigurationSection(Protocol):
    def get[T](self, t: type[T]) -> T | None:
        ...

    def get_section(self, path: str) -> IConfigurationSection:
        ...

    def get_required_section(self, path: str) -> IConfigurationSection:
        ...
