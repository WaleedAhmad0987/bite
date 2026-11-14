"""Day 1: ask a fresh AI run to write tests for each function, from one fixed prompt, unedited.

Usage: python experiment/generate.py <strength|oracle|blind> "<AI command: prompt in, reply out>"
The blind run sees the spec and the signatures alone, never the code.
Each run starts in an empty folder, so the AI sees only the prompt and the function.
"""

import ast
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def outline(source: str) -> str:
    """The module's imports, classes and signatures, with no constants and no function bodies."""
    tree = ast.parse(source)
    tree.body = [n for n in tree.body if not isinstance(n, ast.Assign | ast.AnnAssign)]
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node.body = [ast.Expr(ast.Constant(...))]
    return ast.unparse(tree)


def main() -> None:
    run_dir, ai = HERE / sys.argv[1], shlex.split(sys.argv[2])
    blind = sys.argv[1] == "blind"
    prompt = (HERE / ("prompt-blind.md" if blind else "prompt.md")).read_text()
    package, specs = f"experiment.{sys.argv[1]}.functions", (HERE / "spec.md").read_text()
    for module in sorted((run_dir / "functions").glob("[!_]*.py")):
        source = outline(module.read_text()) if blind else module.read_text()
        spec = next(line for line in specs.splitlines() if f"**{module.stem}**" in line)
        text = prompt.format(package=package, name=module.stem, source=source, spec=spec)
        with tempfile.TemporaryDirectory() as empty:
            run = subprocess.run(
                ai, input=text, capture_output=True, text=True, cwd=empty, check=True
            )
        code = re.sub(r"^```(?:python)?\n|```\s*$", "", run.stdout.strip(), flags=re.M)
        (run_dir / "tests" / f"test_{module.stem}.py").write_text(code.strip() + "\n")
        print(f"wrote tests for {module.stem}")


if __name__ == "__main__":
    main()
