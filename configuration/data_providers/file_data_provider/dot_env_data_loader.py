from typing import IO, Any

from dotenv import dotenv_values

from configuration.type_utils import DataType


def _insert_element(key: str, value: str, d: dict[str, DataType]):
    segments = key.split('__')
    current = d
    for key in segments[:-1]:
        current = current.setdefault(key, {})
    current[segments[-1]] = value


def load_dot_env_file(fp: IO[str | bytes | Any]) -> dict[str, DataType]:
    env = dotenv_values(stream=fp)
    result: dict[str, DataType] = {}

    for key, value in env.items():
        _insert_element(key, value, result)

    return result
