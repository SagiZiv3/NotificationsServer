from .constants import PATH_DELIMITER
from .exceptions import ConfigurationSectionNotFoundError
from .interfaces import IConfigurationSection


class EmptySection:
    def __init__(self, path: str):
        self._path = path

    def get[T](self, _: type[T]) -> T | None:
        return None

    def get_section(self, path: str) -> IConfigurationSection:
        return EmptySection(f"{self._path}{PATH_DELIMITER}{path}")

    def get_required_section(self, path: str) -> IConfigurationSection:
        raise ConfigurationSectionNotFoundError(f"{self._path}{PATH_DELIMITER}{path}")
