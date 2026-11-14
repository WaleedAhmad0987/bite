"""Day 1: run each AI test file on the buggy code it was written for, then on the correct code.

Usage: python experiment/measure.py <oracle|blind>
A test that fails on the buggy code alone caught the bug. A test that fails on the correct code
alone is wrong: written from the code, it asserts the bug; written from the spec, it shows a gap
in the spec. A test that fails on both checks something neither version does.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def failed(root: Path, tests: str) -> tuple[set[str], int]:
    """The names of the tests that failed, and how many ran."""
    cmd = [sys.executable, "-B", "-m", "pytest", "-q", "-rf", "-p", "no:cacheprovider", tests]
    out = subprocess.run(cmd, cwd=root, capture_output=True, text=True).stdout
    ran = sum(int(n) for n in re.findall(r"(\d+) (?:passed|failed)", out))
    return set(re.findall(r"^FAILED (\S+)", out, re.M)), ran


def main() -> None:
    run = sys.argv[1]
    print("| Function | Tests | Catch the bug | Wrong on correct code | Fail on both |")
    print("|---|---|---|---|---|")
    for module in sorted((HERE / run / "functions").glob("[!_]*.py")):
        tests = f"experiment/{run}/tests/test_{module.stem}.py"
        with tempfile.TemporaryDirectory() as tmp:
            skip = shutil.ignore_patterns(".git", ".venv", "__pycache__")
            root = Path(shutil.copytree(HERE.parent, tmp, dirs_exist_ok=True, ignore=skip))
            on_bug, ran = failed(root, tests)
            correct = HERE / "strength" / "functions" / module.name
            shutil.copy(correct, root / "experiment" / run / "functions" / module.name)
            on_correct, _ = failed(root, tests)
        bug, right, both = on_bug - on_correct, on_correct - on_bug, on_bug & on_correct
        print(f"| {module.stem} | {ran} | {len(bug)} | {len(right)} | {len(both)} |")


if __name__ == "__main__":
    main()
