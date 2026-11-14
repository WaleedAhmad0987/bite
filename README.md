# Bite

Coverage tells you a line ran. It does not tell you a test would notice if that line broke.
AI assistants write tests fast, and many of them pass, reach high coverage, and still check very little.

Bite is a merge gate for that: it breaks each line a pull request changed, one at a time, and runs the tests.
A test that fails on the broken code **bites**. A change whose tests pass on broken code does not merge.

## Status

Work in progress, built over five days.

| Deliverable | File | State |
|---|---|---|
| Problem definition | `intent.md` | Day 2 |
| Technical approach | `approach.md` | Day 3 |
| Prototype | `bite.py` | Day 3 |
| Verification evidence | `evidence.md`, `tests/` | Day 4 |
| Final assessment | `directive.md` | Day 5 |

## Development

```sh
uv sync --group dev
uv run ruff check . && uv run mypy bite.py && uv run pytest -q
```
