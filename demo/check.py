"""Check a salesreport project directory and report its size.

    python demo/check.py demo/before
    python demo/check.py path/to/your/trimmed/copy

Behaviour checks run the real CLI (`python -m salesreport FILE`) in a
subprocess, so they pass for any implementation that keeps the same
contract. The project's own tests are then run and the code size is counted.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GOOD = "region,amount\nwest,100.50\neast,40\nwest,20.25\nnorth,5\neast,10.75\n"
EXPECTED = {"east": 50.75, "north": 5.0, "west": 120.75}


def run_cli(project, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("SALESREPORT_")}
    return subprocess.run(
        [sys.executable, "-m", "salesreport", *args],
        cwd=project, env=env, capture_output=True, text=True,
    )


def behaviour(project, tmp):
    good = tmp / "good.csv"
    good.write_text(GOOD)
    bad = tmp / "bad.csv"
    bad.write_text("region,amount\nwest,100\neast,oops\n")
    empty_region = tmp / "empty_region.csv"
    empty_region.write_text("region,amount\n,5\n")

    results = []

    result = run_cli(project, str(good))
    try:
        ok = result.returncode == 0 and json.loads(result.stdout) == EXPECTED
    except ValueError:
        ok = False
    results.append(("totals per region as JSON", ok))

    result = run_cli(project, str(bad))
    results.append(("bad amount: exit 1, no output, names line 3",
                    result.returncode != 0 and not result.stdout.strip()
                    and "3" in result.stderr))

    result = run_cli(project, str(empty_region))
    results.append(("missing region rejected", result.returncode != 0 and not result.stdout.strip()))

    result = run_cli(project, str(tmp / "nope.csv"))
    results.append(("missing file: exit 1, readable error",
                    result.returncode != 0 and bool(result.stderr.strip())
                    and "Traceback" not in result.stderr))
    return results


def own_tests(project):
    if not (project / "tests").is_dir():
        return None
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-t", ".", "-s", "tests"],
        cwd=project, capture_output=True, text=True,
    )
    return result.returncode == 0


def count_lines(project):
    source = tests = 0
    for path in project.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        lines = sum(1 for line in path.read_text().splitlines() if line.strip())
        if "tests" in path.relative_to(project).parts:
            tests += lines
        else:
            source += lines
    return source, tests


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    project = Path(sys.argv[1]).resolve()
    if not (project / "salesreport").is_dir():
        print(f"no salesreport package in {project}")
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        results = behaviour(project, Path(tmp))
    tests_ok = own_tests(project)
    source, tests = count_lines(project)

    for name, ok in results:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    if tests_ok is None:
        print("[FAIL] no tests/ directory: keep one end-to-end smoke test")
    else:
        print(f"[{'ok' if tests_ok else 'FAIL'}] project's own tests pass")
    print(f"non-blank lines: {source} source, {tests} tests")

    return 0 if all(ok for _, ok in results) and tests_ok else 1


if __name__ == "__main__":
    sys.exit(main())
