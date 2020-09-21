from pathlib import Path
from typing import List, Dict, Tuple

from .serializer import load

_configs: List[Tuple[Tuple[str], Dict]] = []


def add_config(key_path: str, config: Dict) -> Dict:
    _configs.append((tuple(key_path.split(".")), config))
    return config


def load_config(path: Path):
    data = load(dict, path)

    for key_path, config in _configs:
        node = data
        for key in key_path:
            if key not in node:
                break

            node = node[key]
        else:
            config.update(node)


__all__ = ["add_config", "load_config"]
