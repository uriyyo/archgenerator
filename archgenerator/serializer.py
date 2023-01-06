from json import loads, dumps
from pathlib import Path
from typing import Any, TypeVar

from pydantic.json import pydantic_encoder

T = TypeVar("T")


def dump(obj: Any, path: Path) -> None:
    path.write_text(dumps(obj, indent=4, default=pydantic_encoder))


def load(cls: type[T], path: Path) -> T:
    return cls(**loads(path.read_text(encoding="utf-8")))


__all__ = [
    "dump",
    "load",
]
