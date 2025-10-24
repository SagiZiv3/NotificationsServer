from .constants import PATH_DELIMITER
from .data_holder import DataHolder
from .empty_section import EmptySection
from .exceptions import ConfigurationSectionNotFoundError
from .interfaces import IConfigurationSection


class ConfigurationSection:
    def __init__(self, sub_data: DataHolder, path: str):
        self._data = sub_data
        self._path = path

    def get[T](self, t: type[T]) -> T | None:
        return self._data.get_value(self._path, t)

    def get_section(self, path: str) -> IConfigurationSection:
        sub_path = f'{self._path}{PATH_DELIMITER}{path}' if self._path else path
        if not self._data.is_valid_path(sub_path):
            return EmptySection(sub_path)

        return ConfigurationSection(self._data, sub_path)

    def get_required_section(self, path: str) -> IConfigurationSection:
        section = self.get_section(path)
        if isinstance(section, EmptySection):
            raise ConfigurationSectionNotFoundError(f'{self._path}{PATH_DELIMITER}{path}')
        return section
