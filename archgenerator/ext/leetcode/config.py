from ...configurator import add_config
from ...platform import PlatformConfig

LANG_TO_NORMALIZE_LANG = {"python3": "python"}
DIFFICULTY_LEVEL = (None, "easy", "medium", "hard")

SECTION_EMOJI = {
    "easy": "👌",
    "medium": "👊",
    "hard": "💪",
}

CONFIG: PlatformConfig = {
    "title": "LeetCode 💫",
    "sections_emoji": SECTION_EMOJI,
}

add_config("leetcode.config", CONFIG)
add_config("leetcode.section_emoji", SECTION_EMOJI)
add_config("leetcode.lang_to_normalize_lang", LANG_TO_NORMALIZE_LANG)

__all__ = [
    "CONFIG",
    "LANG_TO_NORMALIZE_LANG",
    "SECTION_EMOJI",
    "DIFFICULTY_LEVEL",
]
