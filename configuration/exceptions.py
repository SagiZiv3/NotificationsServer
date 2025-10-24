from constants import PATH_DELIMITER

class ConfigurationException(Exception):
    def __init__(self, error_message: str):
        super().__init__(error_message)


class ConfigurationSectionNotFoundError(ConfigurationException):
    def __init__(self, path: str):
        self.path = path.replace(PATH_DELIMITER, '.')
        super().__init__(f"Configuration section not found: '{self.path}'")


class MissingConstructorParametersError(ConfigurationException):
    def __init__(self, t: type, missing_parameters: set[str]):
        super().__init__(f"Config is missing required parameter(s) for {t.__name__}: {', '.join(sorted(missing_parameters))}")
        self.missing_parameters = missing_parameters
        self.type = t

class UnexpectedConstructorParametersError(ConfigurationException):
    def __init__(self, t: type, extra_parameters: set[str]):
        super().__init__(f"Config has unexpected parameter(s) for {t.__name__}: {', '.join(sorted(extra_parameters))}")
        self.missing_parameters = extra_parameters
        self.type = t
