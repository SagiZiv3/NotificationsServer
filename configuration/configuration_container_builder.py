from typing import Self

from dependency_injection import DependencyContainerBuilder
from .configuration_section import ConfigurationSection
from .constants import ROOT_PATH
from .data_holder import DataHolder
from .data_providers import DataProvider
from .interfaces import IConfigurationSection


class ConfigurationContainerBuilder:
    def __init__(self, di_builder: DependencyContainerBuilder):
        self._di_builder = di_builder
        self._data_providers: list[DataProvider] = []
        data_holder = DataHolder(self._data_providers)
        self._root_section = ConfigurationSection(data_holder, ROOT_PATH)

    def add_provider(self, data_provider: DataProvider) -> Self:
        self._data_providers.append(data_provider)
        return self

    def get[T](self, t: type[T]) -> T | None:
        return self._root_section.get(t)

    def get_section(self, path: str) -> IConfigurationSection:
        return self._root_section.get_section(path)

    def get_required_section(self, path: str) -> IConfigurationSection:
        return self._root_section.get_required_section(path)

    def configure[T](self, path: IConfigurationSection, t: type[T]) -> Self:
        self._di_builder.add_singleton(t, instantiation_method=lambda _: path.get(t))
        return self
