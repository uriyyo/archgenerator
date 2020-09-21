from contextvars import ContextVar

LEETCODE_SESSION: ContextVar[str] = ContextVar("LEETCODE_SESSION")
CODEWARS_EMAIL: ContextVar[str] = ContextVar("CODEWARS_EMAIL")
CODEWARS_PASSWORD: ContextVar[str] = ContextVar("CODEWARS_PASSWORD")
CODEWARS_USERNAME: ContextVar[str] = ContextVar("CODEWARS_USERNAME")

__all__ = [
    "CODEWARS_EMAIL",
    "CODEWARS_PASSWORD",
    "CODEWARS_USERNAME",
    "LEETCODE_SESSION",
]
