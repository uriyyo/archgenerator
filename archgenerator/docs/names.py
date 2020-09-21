from collections import Counter
from string import punctuation

PATH_CHARACTERS_TO_REPLACE = {*punctuation, " "} - {"-"}

_NAMES_CACHE = Counter()


def valid_name(name: str, unique: bool = False) -> str:
    for p in PATH_CHARACTERS_TO_REPLACE:
        name = name.replace(p, "-")

    name = (
        name.replace(" ", "-")
        .encode(encoding="ascii", errors="ignore")
        .decode(encoding="ascii")
        .strip("-")
    )

    while "--" in name:
        name = name.replace("--", "-")

    key = name.lower()
    if unique and key in _NAMES_CACHE:
        name = name + f"_{_NAMES_CACHE[key]}"

    _NAMES_CACHE[key] += 1
    return name


def reset_names():
    _NAMES_CACHE.clear()


__all__ = ["valid_name", "reset_names"]
