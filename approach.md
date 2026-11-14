# Approach

## Architecture

```
  spec.md ──────────────────────────┐
                                    ▼
  code.py ──► outline ──────► AI test writer ──► spec tests (committed)
              signatures only       any command,           │
              no bodies             prompt in, reply out   │
              no constants                                 ▼
              no docstrings              ┌──── 1. Agree: run the spec tests on the code
                                         │        fail ──► DISAGREES: a code bug or a spec gap
                                         │                 a person decides which (exit 1)
                                         ▼
                                     2. Bite: break each line, one at a time, run the tests
                                         a break no test catches ──► UNTESTED (exit 1)
                                         ▼
                                     every break caught ──► merge (exit 0)
```

## How to use it

```sh
# Write the tests from the spec, then run the gate
python bite.py demo/refunds.py --tests demo/test_refunds_spec.py \
  --write demo/spec.md "<AI command: prompt on stdin, test file on stdout>"

# The gate alone, as CI runs it on every push
python bite.py demo/refunds.py --tests demo/test_refunds_spec.py
```

## Design decisions

| Decision | Why |
|---|---|
| The test writer sees the spec and the signatures, never the code | Day 1: tests from code caught 0 of 5 bugs; tests from the spec caught 4 of 5, and 5 of 5 once the spec was complete. |
| The outline hides constants as well as bodies | `MAX_PER_PAGE = 50` *is* the pagination bug. Showing it hands the bug to the tester. |
| The outline hides docstrings | A docstring is text from the code that reaches the AI, so it is a channel for prompt injection. Day 4 found one, in class docstrings, and closed it. |
| Agree comes before Bite | A test that fails on the code is either a bug or a spec gap, and a person must look. Breaking the code first would only add noise. |
| Mutation with Python's own `ast` | Six operator swaps (`<`/`<=`, `>`/`>=`, `==`/`!=`, `and`/`or`, `+`/`-`, `*`/`/`), constants changed, and each `if` made false. Small, deterministic and with no dependency. |
| Each break runs in a temporary copy | The repo is never changed, so a crash or timeout leaves nothing behind. |
| It fails closed | A pytest error, a 60 s timeout or an AI reply that is not code all fail the gate. |
| The AI is any command | Model-agnostic, with no SDK and no key in the tool: swap the model by changing one string. |
| The spec tests are committed files | The AI is called once, when the spec changes. CI re-runs the tests with no AI call: deterministic, free, with no secret in CI. |
| Exit code 0 or 1 | Any CI system can use it as a required check. |

## Specification

[`demo/spec.md`](demo/spec.md) is the spec for the demo.
It is written so each rule can be checked: the order of the checks, the error each one raises, and what the function returns.
The Day 1 experiment showed why that matters: the one sentence my first spec left out hid a bug.

## Lead time

Measured on the demo, on a laptop:

| Step | Time |
|---|---|
| AI writes the spec tests, then the gate runs | 16 s |
| Gate: Agree, then 13 breaks | 2.9 s |
| Full CI run on GitHub (install, lint, types, Bite's tests, gate) | 19 s |

The time grows with the number of breaks times the test suite's run time.
[`directive.md`](directive.md) covers how to keep it inside an hour on a large codebase.

## Where a person stays in the loop

Only on `DISAGREES`.
Deciding whether the code or the spec is wrong is a product decision, and Bite says which spec test is affected so the decision is fast.
Everything else (writing tests, checking they are strong, blocking the merge) runs with no person.

Next: [`evidence.md`](evidence.md).
