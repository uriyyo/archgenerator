from contextvars import ContextVar

LEETCODE_EMAIL: ContextVar[str] = ContextVar("LEETCODE_EMAIL")
LEETCODE_PASSWORD: ContextVar[str] = ContextVar("LEETCODE_PASSWORD")
LEETCODE_SESSION: ContextVar[str] = ContextVar("LEETCODE_SESSION")


__all__ = ["LEETCODE_EMAIL", "LEETCODE_PASSWORD", "LEETCODE_SESSION"]
