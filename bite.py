"""Bite: break each line one at a time, run the tests, and report every break no test catches."""

import argparse
import ast
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

SWAPS: dict[type, type] = {
    **{ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt},
    **{ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.And: ast.Or, ast.Or: ast.And},
    **{ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult},
}
FIX = """Spec:\n{spec}\nCode:\n{source}\nWrite one pytest test, from the spec, that passes on this
code but fails if line {line} changes `{old}` to `{new}`. Reply with only the test file's code."""
Mutant = tuple[int, str, str, str]  # line, old code, new code, broken source


def break_node(node: ast.AST) -> bool:
    """Break this node in place, or return False when Bite has no break for it."""
    if isinstance(node, ast.Compare) and type(node.ops[0]) in SWAPS:
        node.ops[0] = SWAPS[type(node.ops[0])]()
    elif isinstance(node, ast.BinOp | ast.BoolOp) and type(node.op) in SWAPS:
        node.op = SWAPS[type(node.op)]()
    elif isinstance(node, ast.Constant) and isinstance(node.value, bool | int):
        node.value = not node.value if isinstance(node.value, bool) else node.value + 1
    elif isinstance(node, ast.If):
        node.test = ast.Constant(False)
    else:
        return False
    return True


def mutants(source: str) -> Iterator[Mutant]:
    """Every break of the source, each made on a fresh copy of its tree."""
    for i, node in enumerate(ast.walk(ast.parse(source))):
        tree = ast.parse(source)
        target = next(n for j, n in enumerate(ast.walk(tree)) if j == i)
        if break_node(target):
            old, new = (ast.unparse(getattr(n, "test", n)) for n in (node, target))
            yield getattr(node, "lineno", 0), old, new, ast.unparse(tree)


def passes(root: Path, tests: str, module: str, code: str) -> bool:
    """Put this code in the module and run the tests, with no stale bytecode and a time limit."""
    (root / module).write_text(code)
    cmd = [sys.executable, "-B", "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", tests]
    try:
        return subprocess.run(cmd, cwd=root, capture_output=True, timeout=60).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def fix(root: Path, args: argparse.Namespace, source: str, mutant: Mutant) -> None:
    """Ask the AI for a test that catches this break, and keep it only if it provably does."""
    line, old, new, broken = mutant
    ai, spec = shlex.split(args.fix[0]), Path(args.fix[1]).read_text()
    prompt = FIX.format(spec=spec, source=source, line=line, old=old, new=new)
    reply = subprocess.run(ai, input=prompt, capture_output=True, text=True).stdout
    test = Path(args.tests) / f"test_bite_line_{line}.py"
    (root / test).write_text(re.sub(r"^```(?:python)?\n|```\s*$", "", reply.strip(), flags=re.M))
    proof = (passes(root, str(test), args.module, code) for code in (source, broken))
    caught = next(proof) and not next(proof)
    if caught:
        shutil.copy(root / test, test)
    print(f"{'KEPT' if caught else 'DROPPED'} {test}: {'catches' if caught else 'misses'} {new}")


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("module", help="the Python file to break, from the project root")
    cli.add_argument("--tests", default="tests", help="the tests to run against each break")
    cli.add_argument("--fix", nargs=2, metavar=("AI", "SPEC"), help="AI command, spec file")
    args = cli.parse_args()
    source = Path(args.module).read_text()
    rules = {source[: m.start()].count("\n") + 1: m[1] for m in re.finditer(r"#\s*(R\d+)", source)}
    found = list(mutants(source))
    with tempfile.TemporaryDirectory() as tmp:
        skip = shutil.ignore_patterns(".git", ".venv", "__pycache__")
        root = Path(shutil.copytree(".", tmp, dirs_exist_ok=True, ignore=skip))
        if not passes(root, args.tests, args.module, source):
            sys.exit("bite: the tests fail before any break, so there is nothing to measure")
        survivors = [m for m in found if passes(root, args.tests, args.module, m[3])]
        for line, old, new, _ in survivors:
            note = rules.get(line, "no spec rule: a missing requirement?" if rules else "")
            print(f"SURVIVED {args.module}:{line}  {old}  ->  {new}  {note}".rstrip())
        print(f"bite: {len(found) - len(survivors)}/{len(found)} breaks caught")
        for mutant in survivors if args.fix else []:
            fix(root, args, source, mutant)
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
