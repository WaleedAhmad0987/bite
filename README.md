# Bite

**AI-written tests caught 0 of 5 real bugs, at 100% coverage.**
Written from the code, they turned each bug into the expected result: `test_code_is_case_sensitive`, `test_exactly_12_chars_is_too_short`.
Written from the spec alone, they caught them.

Bite is a merge gate for AI-written code, in [`bite.py`](bite.py): under 100 lines, Python's standard library only.

1. **Write**: an AI writes the tests from the spec and the function signatures, never the code.
2. **Agree**: the tests must pass on the code. A failure is a bug in the code or a gap in the spec.
3. **Bite**: each line is broken, one at a time, and the tests must catch every break.

```console
$ python bite.py demo/refunds.py --tests demo/test_refunds_spec.py
bite: tests agree with the code; 13/13 breaks caught

$ # the same code with one bug: a refund on day 30 is refused
DISAGREES demo/test_refunds_spec.py::test_exactly_30_days_allowed: a code bug or a spec gap
```

## Read in this order

| File | What it holds |
|---|---|
| [`intent.md`](intent.md) | The problem, measured: how I found it, its root cause, the direction |
| [`approach.md`](approach.md) | Architecture, design decisions, lead time |
| [`evidence.md`](evidence.md) | Experiment results, Day 4 failure cases, security |
| [`directive.md`](directive.md) | Final assessment, limitations, next steps |
| [`experiment/`](experiment) | The Day 1 experiment: functions, planted bugs, prompts, every AI-written test, unedited |
| [`demo/`](demo) | A refund service, its spec and its spec tests |

## Run it

```sh
uv sync --group dev
uv run python demo.py                                             # the demo: 3 steps, press Enter for each
uv run pytest -q                                                  # Bite's own tests
uv run python bite.py demo/refunds.py --tests demo/test_refunds_spec.py

# Write new spec tests with any AI command that reads a prompt on stdin
uv run python bite.py demo/refunds.py --tests demo/test_new.py --write demo/spec.md "<AI command>"
```

CI runs ruff, `mypy --strict`, Bite's tests and the gate on every push.
