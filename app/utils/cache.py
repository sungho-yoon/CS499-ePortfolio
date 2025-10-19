from functools import lru_cache
from typing import Mapping, Any, Tuple

def _freeze(value: Any) -> Any:
    # Make nested dict/list/hashables into a stable, hashable structure
    if isinstance(value, Mapping):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple, set)):
        return tuple(_freeze(v) for v in value)
    return value

def make_signature(filters: Mapping[str, Any], *extras: Any) -> Tuple[Any, ...]:
    # Normalize filters and any extra args into a cache key 
    return (_freeze(filters),) + tuple(_freeze(x) for x in extras)

# LRU size is modest so we don’t cache stale stuff for too long.
# You can tune these if your dataset/usage grows.
def lru128(func):
    return lru_cache(maxsize=128)(func)