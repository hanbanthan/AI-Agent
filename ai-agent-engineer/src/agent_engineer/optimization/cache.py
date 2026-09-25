import time

from dataclasses import dataclass
from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

@dataclass
class CacheEntry(Generic[V]):
    value: V
    expires_at: float | None

@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0

class Cache(Generic[K, V]):

    def __init__(
        self,
        ttl_seconds: float | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:

        self.ttl_seconds = ttl_seconds
        self.clock = clock

        self._items: dict[K, CacheEntry[V]] = {}

        self.stats = CacheStats()

    def set(
        self,
        key: K,
        value: V,
    ) -> None:

        expires_at = None

        if self.ttl_seconds is not None:
            expires_at = self.clock() + self.ttl_seconds

        self._items[key] = CacheEntry(
            value=value,
            expires_at=expires_at,
        )

    def get(
        self,
        key: K,
    ) -> V | None:

        entry = self._items.get(key)

        if entry is None:
            self.stats.misses += 1
            return None

        if entry.expires_at is not None and self.clock() >= entry.expires_at:
            del self._items[key]
            self.stats.misses += 1
            return None

        self.stats.hits += 1
        return entry.value