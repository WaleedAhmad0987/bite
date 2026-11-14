# Evidence

Every figure here was measured, and each section names the command to run it again.

```sh
uv sync --group dev
uv run pytest -q                                # Bite's own tests
uv run python experiment/measure.py oracle      # tests from buggy code
uv run python experiment/measure.py blind       # tests from the spec alone
uv run python bite.py experiment/strength/functions/refunds.py \
  --tests experiment/strength/tests/test_refunds.py   # strength, one function
```

## 1. The experiment

Five functions, one fixed prompt per run, a fresh AI run per function, in an empty folder with every tool turned off.
Every AI-written test is kept unedited in [`experiment/`](experiment) (only the import line was changed when the folders moved).

### Tests written from the correct code: strength

| Function | Tests | Coverage | Breaks caught |
|---|---|---|---|
| discount | 26 | 100% | 10 of 10 |
| pagination | 25 | 100% | 12 of 13 |
| password | 27 | 100% | 7 of 7 |
| refunds | 21 | 100% | 13 of 13 |
| shipping | 41 | 100% | 13 of 13 |

The one break not caught, `start >= total` to `start > total` in pagination, changes nothing: at `start == total` both versions return `(total, total)`.

### Tests written from buggy code, then run on the correct code

| Function | Tests | Catch the bug | Assert the bug |
|---|---|---|---|
| discount | 31 | 0 | 1 |
| pagination | 25 | 0 | 2 |
| password | 23 | 0 | 1 |
| refunds | 23 | 0 | 1 |
| shipping | 30 | 0 | 1 |

### Tests written from the spec alone, on the same buggy code

| Function | Tests | Catch the bug | Assert the bug | Fail on both versions |
|---|---|---|---|---|
| discount | 33 | 6 | 0 | 1 |
| pagination | 19 | 4 | 0 | 0 |
| password | 25 | 3 | 0 | 0 |
| refunds | 30 | 0 | 0 | 9 |
| shipping | 31 | 1 | 0 | 0 |

The 10 tests that fail on both versions trace to two gaps in [`experiment/spec.md`](experiment/spec.md): it never says what `refund()` returns, or which check comes first for an unknown code on a small order.
In refunds, that gap hid the bug. [`demo/spec.md`](demo/spec.md) closes it, and the spec tests then catch the same bug (section 2, first row).

## 2. Day 4: Challenge

Each scenario was run against Bite. The test names are in [`tests/test_bite.py`](tests/test_bite.py).

| Scenario | What Bite did | Evidence |
|---|---|---|
| A real bug: day 30 refused, one character changed | `DISAGREES demo/test_refunds_spec.py::test_exactly_30_days_allowed`, exit 1 | `test_fails_on_a_bug_and_names_the_spec_test_it_breaks` |
| AI tests that pass but check nothing (`assert True`) | `0/13 breaks caught`, exit 1 | `test_fails_tests_that_pass_but_check_nothing` |
| The AI replies "Sorry, I cannot help with that." | the reply is not code, so pytest fails: `DISAGREES`, exit 1 | `test_fails_closed_when_the_ai_replies_with_no_code` |
| A prompt planted in a docstring: module, class or function | hidden from the AI | `test_outline_hides_a_prompt_planted_in_a_docstring` |
| A gap in the spec | the refunds bug was hidden by 9 tests failing on both versions | section 1, last table |
| A break that changes nothing | reported as `UNTESTED`: a false alarm | pagination, section 1 |
| Correct code with strong spec tests | `13/13 breaks caught`, exit 0 | `test_passes_when_spec_tests_agree_and_catch_every_break` |

### What Day 4 found and fixed

The first outline hid docstrings at the top of the module and in functions, but not in classes.
A docstring in a class reached the AI word for word.
It is fixed, and the test now plants a prompt in all three places.

## 3. Security

| Risk | What Bite does | What is left |
|---|---|---|
| AI-written tests are code, and they run | The experiment's AI runs had every tool turned off and an empty working folder. Tests run in a temporary copy, never in the repo. CI runs them on a fresh GitHub runner with a read-only token and no secrets. | Bite does not sandbox the run itself. Run the gate in a container with no network (`docker run --network none`). |
| Prompt injection from the code | Bodies, constants and docstrings never reach the AI. | Names and type hints still do. |
| The code leaking to the AI provider | Only the spec and the signatures are sent. | The spec is sent. |
| The AI command | Split with `shlex` and run with no shell. | The command is trusted: it comes from whoever runs Bite. |
| A break that hangs (an endless loop) | Each test run stops after 60 s, which counts as caught. | Not tested. |

## 4. Bite's own checks

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs on every push: ruff, ruff format, `mypy --strict`, Bite's 11 tests, and Bite as a gate on the demo.

Next: [`directive.md`](directive.md).
