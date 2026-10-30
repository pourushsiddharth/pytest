"""Compare pytest memory behavior across small, isolated reproductions."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEST_FILE = ROOT / "memory_repro" / "test_memory.py"
CONFTST_FILE = ROOT / "memory_repro" / "conftest.py"


def run_case(
    case: str, items: int, collect_only: bool, no_terminal: bool, no_capture: bool
) -> None:
    source = TEST_FILE.read_text(encoding="utf-8")
    source = source.replace("range(100)", f"range({items})")
    if case == "empty":
        source = re.sub(
            r'\n\n@pytest\.mark\.parametrize\("value", range\(\d+\)\)\n'
            r"def test_parametrized\(value\):\n"
            r"    assert value >= 0\n",
            "",
            source,
        )
        source = source.replace(
            "\n\nclass TestXunitStyle:\n"
            "    def setup_method(self):\n"
            "        self.obj = RetainedObject()\n\n"
            "    def test_instance_object(self):\n"
            "        assert self.obj is not None\n",
            "",
        )
    elif case == "param":
        source = source.split("\n\nclass TestXunitStyle:", 1)[0] + "\n"
    elif case == "xunit":
        source = re.sub(
            r'\n\n@pytest\.mark\.parametrize\("value", range\(\d+\)\)\n'
            r"def test_parametrized\(value\):\n"
            r"    assert value >= 0\n",
            "",
            source,
        )
        source = source.replace(
            "    def test_instance_object(self):\n",
            f'    @pytest.mark.parametrize("value", range({items}))\n'
            "    def test_instance_object(self, value):\n",
        )

    generated = TEST_FILE.with_name(f"test_generated_{os.getpid()}_{case}.py")
    generated.write_text(source, encoding="utf-8")
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        command = [sys.executable, "-m", "pytest", str(generated)]
        if not no_terminal:
            command.insert(3, "-q")
        if collect_only:
            command.append("--collect-only")
        if no_terminal:
            command.extend(["-p", "no:terminal"])
        if no_capture:
            command.append("-s")
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            check=False,
            text=True,
            capture_output=True,
        )
        output = completed.stdout + completed.stderr
        match = re.search(
            r"MEMORY_REPRO rss_before=(\d+) rss_after=(\d+) "
            r"rss_delta=(-?\d+) traced_current=(\d+) traced_peak=(\d+)",
            output,
        )
        print(f"\nCASE {case}")
        print(output.strip())
        if match:
            print(
                "RESULT "
                f"rss_delta={int(match.group(3)) / 1024 / 1024:.2f} MiB "
                f"traced_current={int(match.group(4)) / 1024 / 1024:.2f} MiB "
                f"traced_peak={int(match.group(5)) / 1024 / 1024:.2f} MiB"
            )
        if completed.returncode:
            raise SystemExit(completed.returncode)
    finally:
        generated.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("empty", "param", "xunit"), default="empty")
    parser.add_argument("--items", type=int, default=100)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--no-terminal", action="store_true")
    parser.add_argument("--no-capture", action="store_true")
    args = parser.parse_args()
    run_case(args.case, args.items, args.collect_only, args.no_terminal, args.no_capture)


if __name__ == "__main__":
    main()
