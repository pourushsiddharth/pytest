# Pytest memory-growth reproduction for issue #10605

This reproduction compares baseline, parametrized, and xunit-style tests while recording RSS and `tracemalloc` statistics.

From this directory, run for example:

```console
python run_memory_repro.py --case param --items 5000
python run_memory_repro.py --case param --items 5000 --collect-only
python run_memory_repro.py --case param --items 5000 --no-terminal
```

Dependencies: `pytest` and `psutil`.
