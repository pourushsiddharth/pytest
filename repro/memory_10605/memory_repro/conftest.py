import gc
import os
import tracemalloc

import psutil


_process = psutil.Process(os.getpid())
_before = None


def pytest_sessionstart(session):
    global _before
    tracemalloc.start()
    gc.collect()
    _before = _process.memory_info().rss


def pytest_sessionfinish(session, exitstatus):
    gc.collect()
    after = _process.memory_info().rss
    current, peak = tracemalloc.get_traced_memory()
    top_stats = tracemalloc.take_snapshot().statistics("lineno")[:12]
    print(
        "\nMEMORY_REPRO "
        f"rss_before={_before} "
        f"rss_after={after} "
        f"rss_delta={after - _before} "
        f"traced_current={current} "
        f"traced_peak={peak}"
    )
    print("MEMORY_TOP_ALLOCATIONS")
    for stat in top_stats:
        print(f"{stat.traceback[0]} size={stat.size} count={stat.count}")
    tracemalloc.stop()
