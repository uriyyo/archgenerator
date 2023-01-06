from ...configurator import add_config
from ...platform import PlatformConfig

SECTION_EMOJI = {
    "beta": "🌝",
    "retired": "😶",
    "1 kyu": "🏆",
    "2 kyu": "👑",
    "3 kyu": "💎",
    "4 kyu": "💍",
    "5 kyu": "🎯",
    "6 kyu": "🎩",
    "7 kyu": "🎁",
    "8 kyu": "🎒",
}

CONFIG: PlatformConfig = {
    "title": "CodeWars ✨",
    "sections_emoji": SECTION_EMOJI,
}

add_config("codewars.config", CONFIG)
add_config("codewars.section_emoji", SECTION_EMOJI)

__all__ = [
    "CONFIG",
    "SECTION_EMOJI",
]
