from enum import IntEnum
from typing import NamedTuple, Self


class LifeScope(IntEnum):
    Transient = 0
    Scoped = 1
    Singleton = 2


class RegisteredService(NamedTuple):
    life_scope: LifeScope
    service_type: type
    implementation_type: type


class ServiceIdentifier(NamedTuple):
    Type: type
    Key: object = None

    @classmethod
    def from_type[T](cls, t: type[T]) -> Self:
        return cls(t)
