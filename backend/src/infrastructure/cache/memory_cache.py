"""In-memory cache with TTL support.

Simple cache implementation for brand theme data and other frequently accessed data.
For production, consider using Redis or similar distributed cache.
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""

    value: Any
    expires_at: float


@dataclass
class MemoryCache:
    """Simple in-memory cache with TTL support.

    Thread-safe for async operations using asyncio.Lock.

    Attributes:
        default_ttl: Default time-to-live in seconds (default: 300 = 5 minutes)
        max_size: Maximum number of entries (default: 1000)
    """

    default_ttl: float = 300.0
    max_size: int = 1000
    _cache: dict[str, CacheEntry] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if time.time() > entry.expires_at:
                # Entry expired, remove it
                del self._cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        async with self._lock:
            # Evict oldest entries if at max size
            if len(self._cache) >= self.max_size:
                await self._evict_oldest()

            expires_at = time.time() + (ttl or self.default_ttl)
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all cache entries matching pattern.

        Args:
            pattern: Prefix pattern to match (e.g., 'brand:')

        Returns:
            Number of entries deleted
        """
        async with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    async def _evict_oldest(self) -> None:
        """Evict oldest entries when cache is full.

        Removes entries that are expired first, then oldest by expiration time.
        """
        current_time = time.time()

        # First, remove expired entries
        expired_keys = [
            k for k, v in self._cache.items() if v.expires_at < current_time
        ]
        for key in expired_keys:
            del self._cache[key]

        # If still at max size, remove oldest 10%
        if len(self._cache) >= self.max_size:
            sorted_entries = sorted(
                self._cache.items(), key=lambda x: x[1].expires_at
            )
            entries_to_remove = max(1, len(sorted_entries) // 10)
            for key, _ in sorted_entries[:entries_to_remove]:
                del self._cache[key]

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


# Global cache instance
_cache: MemoryCache | None = None


def get_cache() -> MemoryCache:
    """Get global cache instance.

    Returns:
        Global MemoryCache instance
    """
    global _cache
    if _cache is None:
        _cache = MemoryCache()
    return _cache


# Cache key builders
def brand_theme_key(slug: str) -> str:
    """Build cache key for brand theme."""
    return f"brand:theme:{slug}"


def brand_menu_key(brand_id: str) -> str:
    """Build cache key for brand menu."""
    return f"brand:menu:{brand_id}"
