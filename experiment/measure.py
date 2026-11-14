"""Day 1: run each AI test file on the buggy code it was written for, then on the correct code.

Usage: python experiment/measure.py <oracle|blind>
A test that fails on the buggy code caught the bug. A test that fails on the correct code
asserts something the spec does not say: for tests written from the code, that is the bug
written down as correct.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def failed(root: Path, tests: str) -> tuple[int, int]:
    """How many tests failed, and how many ran."""
    cmd = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", tests]
    out = subprocess.run(cmd, cwd=root, capture_output=True, text=True).stdout
    found = {word: int(n) for n, word in re.findall(r"(\d+) (passed|failed)", out)}
    return found.get("failed", 0), found.get("passed", 0) + found.get("failed", 0)


def main() -> None:
    run = sys.argv[1]
    print("| Function | Fails on buggy code (bug caught) | Fails on correct code (wrong test) |")
    print("|---|---|---|")
    for module in sorted((HERE / run / "functions").glob("[!_]*.py")):
        tests = f"experiment/{run}/tests/test_{module.stem}.py"
        with tempfile.TemporaryDirectory() as tmp:
            skip = shutil.ignore_patterns(".git", ".venv", "__pycache__")
            root = Path(shutil.copytree(HERE.parent, tmp, dirs_exist_ok=True, ignore=skip))
            on_bug, ran = failed(root, tests)
            correct = HERE / "strength" / "functions" / module.name
            shutil.copy(correct, root / "experiment" / run / "functions" / module.name)
            on_correct, _ = failed(root, tests)
        print(f"| {module.stem} | {on_bug} of {ran} | {on_correct} of {ran} |")


if __name__ == "__main__":
    main()
