from pathlib import Path
from typing import Any, TypeAlias, Mapping, cast

from .serializer import load

Config: TypeAlias = Mapping[Any, Any]

_configs: list[tuple[tuple[str, ...], Config]] = []


def add_config(key_path: str, config: Config) -> Config:
    _configs.append((tuple(key_path.split(".")), config))
    return config


def load_config(path: Path) -> None:
    data = load(dict, path)

    for key_path, config in _configs:
        node = data
        for key in key_path:
            if key not in node:
                break

            node = node[key]
        else:
            cast(dict[Any, Any], config).update(node)


__all__ = [
    "add_config",
    "load_config",
]
