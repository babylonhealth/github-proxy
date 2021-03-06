from typing import Optional

from cachetools import TTLCache

from github_proxy.cache.backend import CacheBackend
from github_proxy.cache.backend import CacheBackendConfig
from github_proxy.cache.backend import Value


class InMemoryCache(CacheBackend, scheme="inmemory"):
    """Useful for testing purposes"""

    def __init__(self, config: CacheBackendConfig):
        super().__init__(config)
        self._store: TTLCache[str, Value] = TTLCache(
            maxsize=1024, ttl=self.config.cache_ttl
        )

    def _make_key(
        self, resource: str, filter_: Optional[str], representation: str
    ) -> str:
        return f"{resource}/{filter_}/{representation}"

    def _get(self, key: str) -> Optional[Value]:
        return self._store.get(key)

    def _set(self, key: str, value: Value) -> None:
        self._store[key] = value
