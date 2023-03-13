from django.core.cache import caches

babble_cache = caches["second"]


def update_babble_cache(id: int, field: str, count: int) -> None:
    babble_cache_data = babble_cache.get(id)
    if babble_cache_data:
        babble_cache_data[field] += count
        babble_cache.set(id, babble_cache_data)
