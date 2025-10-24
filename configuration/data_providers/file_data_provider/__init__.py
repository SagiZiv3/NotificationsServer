import json

from dotenv import find_dotenv

from .dot_env_data_loader import load_dot_env_file
from .file_data_provider import DataProvider, FileDataProvider, FileType


def dot_env_file() -> DataProvider:
    return FileDataProvider(find_dotenv(), load_dot_env_file)


def json_file(json_path: str) -> DataProvider:
    return FileDataProvider(json_path, json.load)


__all__ = ('FileDataProvider', 'FileType', 'json_file', 'dot_env_file')
