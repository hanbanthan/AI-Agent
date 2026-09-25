from agent_engineer.optimization.cache import (
    Cache,
)


def test_cache_hit_and_miss() -> None:

    cache = Cache[str, str]()

    assert cache.get("a") is None
    assert cache.stats.misses == 1

    cache.set(
        "a",
        "response",
    )

    assert cache.get("a") == "response"
    assert cache.stats.hits == 1