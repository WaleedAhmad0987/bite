"""The demo in one command: python demo.py. It works on copies, so no file in the repo changes."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
TESTS = "demo/test_refunds_spec.py"
STEPS = [
    ("The refund code is correct, and the AI's tests were written from the spec alone.", "", ""),
    (
        "Now one character is wrong: a refund on day 30 is refused, but the spec allows it.",
        "placed_at > WINDOW",
        "placed_at >= WINDOW",
    ),
    ("Now the tests pass but check nothing: every test is just `assert True`.", "nothing", ""),
]


def main() -> None:
    for number, (story, old, new) in enumerate(STEPS, 1):
        input(f"\nStep {number} of {len(STEPS)}: {story}\nPress Enter to run Bite...")
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT / "demo", Path(tmp) / "demo")
            shutil.copy(ROOT / "bite.py", tmp)
            tests = Path(tmp) / TESTS
            if old == "nothing":
                tests.write_text("def test_refund() -> None:\n    assert True\n")
            elif old:
                code = Path(tmp) / "demo" / "refunds.py"
                code.write_text(code.read_text().replace(old, new))
            cmd = [sys.executable, "-B", "bite.py", "demo/refunds.py", "--tests", TESTS]
            run = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
        print(
            "\n".join(line for line in run.stdout.splitlines() if not line.startswith("UNTESTED"))
        )
        passed = run.returncode == 0
        print("PASS: safe to merge" if passed else "BLOCKED: this change cannot merge")


if __name__ == "__main__":
    main()
