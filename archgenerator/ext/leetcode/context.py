from contextvars import ContextVar

LEETCODE_EMAIL: ContextVar[str] = ContextVar("LEETCODE_EMAIL")
LEETCODE_PASSWORD: ContextVar[str] = ContextVar("LEETCODE_PASSWORD")

__all__ = ["LEETCODE_EMAIL", "LEETCODE_PASSWORD"]
