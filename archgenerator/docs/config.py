from ..configurator import add_config

CONFIG = {
    "title": "Coding Challenges ⭐",
}

LANG_TO_PRETTY_LANG = {
    "javascript": "JavaScript",
    "coffeescript": "CoffeeScript",
}

LANG_TO_EMOJI = {
    "bash": "🔩",
    "python": "🐍",
    "javascript": "🙈",
    "java": "️️☕️",
    "coffeescript": "🙉",
    "c++": "🛠",
    "cpp": "🛠",
    "c": "🔧",
    "kotlin": "🌱",
    "haskell": "🔗",
}

add_config("docs.config", CONFIG)
add_config("docs.lang_to_emoji", LANG_TO_EMOJI)
add_config("docs.lang_to_pretty_lang", LANG_TO_PRETTY_LANG)

__all__ = ["CONFIG", "LANG_TO_EMOJI", "LANG_TO_PRETTY_LANG"]
