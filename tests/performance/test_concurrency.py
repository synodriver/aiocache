import re
import time
import pytest
import subprocess

from multiprocessing import Process

from server import run_server


@pytest.fixture
def redis_server():
    p = Process(target=run_server, args=["redis"])
    p.start()
    yield
    p.terminate()
    time.sleep(2)


@pytest.fixture
def memcached_server():
    p = Process(target=run_server, args=["memcached"])
    p.start()
    yield
    p.terminate()
    time.sleep(2)


@pytest.fixture
def memory_server():
    p = Process(target=run_server, args=["memory"])
    p.start()
    yield
    p.terminate()
    time.sleep(2)


@pytest.fixture(params=["memcached_server", "memory_server", "redis_server"])
def server(request):
    return request.getfuncargvalue(request.param)


def test_concurrency_error_rates(server):
    total_requests = 1500
    result = subprocess.run(
        ["ab", "-n", str(total_requests), "-c", "500", "http://127.0.0.1:8080/"],
        stdout=subprocess.PIPE,
    )

    failed_requests = total_requests
    if m := re.search(r"Failed requests:\s+([0-9]+)", str(result.stdout)):
        failed_requests = int(m[1])

    non_200 = 0
    if m := re.search(r"Non-2xx responses:\s+([0-9]+)", str(result.stdout)):
        non_200 = int(m[1])

    print(f"Failed requests: {failed_requests / total_requests * 100}%")
    print(f"Non 200 requests: {non_200 / total_requests * 100}%")
    assert (
        failed_requests / total_requests < 0.75
    )  # aioredis is the problem here, need to improve it
    assert non_200 / total_requests < 0.75
