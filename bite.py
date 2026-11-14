"""Bite: tests written from the spec alone, that must pass on the code and must catch its bugs."""

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

PAIRS: list[tuple[type, type]] = [(ast.Lt, ast.LtE), (ast.Gt, ast.GtE), (ast.Eq, ast.NotEq)]
PAIRS += [(ast.And, ast.Or), (ast.Add, ast.Sub), (ast.Mult, ast.Div)]
SWAPS: dict[type, type] = {**dict(PAIRS), **{b: a for a, b in PAIRS}}
WRITE = """Write pytest tests for `{pkg}` from its spec alone: you see signatures, not code.
Import it with `from {pkg} import *`. Reply with only the test file's code.
Spec:\n{spec}\nSignatures:\n{sig}"""
HIDDEN = {ast.Module: (ast.Expr, ast.Assign, ast.AnnAssign), ast.ClassDef: (ast.Expr,)}
FENCE = re.compile(r"^```(?:python)?\n|```\s*$", re.M)


def outline(source: str) -> str:
    """Imports, classes and signatures only: no constants, no bodies, no docstrings."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            node.body = [ast.Expr(ast.Constant(...))]
        elif isinstance(node, ast.Module | ast.ClassDef):
            node.body = [n for n in node.body if not isinstance(n, HIDDEN[type(node)])]
    return ast.unparse(tree)


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


def mutants(source: str) -> Iterator[tuple[int, str, str, str]]:
    """Every break as (line, old code, new code, broken source), each on a fresh tree."""
    for i, node in enumerate(ast.walk(ast.parse(source))):
        tree = ast.parse(source)
        target = next(n for j, n in enumerate(ast.walk(tree)) if j == i)
        if break_node(target):
            old, new = (ast.unparse(getattr(n, "test", n)) for n in (node, target))
            yield getattr(node, "lineno", 0), old, new, ast.unparse(tree)


def failures(root: Path, tests: str, module: str, code: str, first: bool = False) -> list[str]:
    """Put this code in the module, run the tests, and name each one that fails."""
    (root / module).write_text(code)
    cmd = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no", tests]
    try:
        out = subprocess.run(cmd + ["-x"] * first, cwd=root, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return ["timed out"]
    named = re.findall(r"^(?:FAILED|ERROR) (\S+)", out.stdout.decode(), re.M)
    return named or ([] if out.returncode == 0 else [f"pytest exited {out.returncode}"])


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("module", help="the Python file under test, from the project root")
    cli.add_argument("--tests", required=True, help="the spec tests to run")
    cli.add_argument("--write", nargs=2, metavar=("SPEC", "AI"), help="first write the tests")
    args = cli.parse_args()
    code = Path(args.module).read_text()
    if args.write:  # the AI sees the spec and the signatures, never the code
        spec, ai = Path(args.write[0]).read_text(), shlex.split(args.write[1])
        prompt = WRITE.format(pkg=args.module[:-3].replace("/", "."), spec=spec, sig=outline(code))
        reply = subprocess.run(ai, input=prompt, capture_output=True, text=True)
        Path(args.tests).write_text(FENCE.sub("", reply.stdout))
    with tempfile.TemporaryDirectory() as tmp:
        skip = shutil.ignore_patterns(".git", ".venv", "__pycache__")
        root = Path(shutil.copytree(".", tmp, dirs_exist_ok=True, ignore=skip))
        if failed := failures(root, args.tests, args.module, code):
            print("\n".join(f"DISAGREES {name}: a code bug or a spec gap" for name in failed))
            return 1
        found = list(mutants(code))
        caught = [m for m in found if failures(root, args.tests, args.module, m[3], first=True)]
        for line, old, new, _ in (m for m in found if m not in caught):
            print(f"UNTESTED {args.module}:{line}  {old} -> {new}: no test catches this")
        print(f"bite: tests agree with the code; {len(caught)}/{len(found)} breaks caught")
    return 0 if len(caught) == len(found) else 1


if __name__ == "__main__":
    raise SystemExit(main())
