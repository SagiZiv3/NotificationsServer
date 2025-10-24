from configuration import ConfigurationContainerBuilder
from dependency_injection import DependencyContainerBuilder
from .web_application import WebApplication


class WebApplicationBuilder:
    def __init__(self):
        self._di_container_builder = DependencyContainerBuilder()
        self._config_container_builder = ConfigurationContainerBuilder(self._di_container_builder)

    @property
    def services(self) -> DependencyContainerBuilder:
        return self._di_container_builder

    @property
    def configuration(self) -> ConfigurationContainerBuilder:
        return self._config_container_builder

    def build(self) -> WebApplication:
        return WebApplication(self._di_container_builder.build())
