import pytest

from aiocache import Cache
from aiocache.backends.redis import RedisBackend


@pytest.fixture
def redis_cache(event_loop):
    yield Cache(Cache.REDIS, namespace="test", pool_max_size=1)
    for _, pool in RedisBackend.pools.items():
        pool.close()
        event_loop.run_until_complete(pool.wait_closed())


@pytest.fixture
def memcached_cache():
    yield Cache(Cache.MEMCACHED, namespace="test", pool_size=1)
