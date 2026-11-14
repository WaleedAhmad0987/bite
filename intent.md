# Intent

## The question

AI now writes the code and the tests. If the tests pass, can the change ship with no person reviewing it?

To answer that, I measured what AI-written tests actually check, before I built anything.

## Day 1: Discover

I wrote five small functions of the kind every product has: a discount code, a password rule, a shipping price, pagination and a refund.
A fresh AI run wrote the tests for each one, from one fixed prompt ([`experiment/prompt.md`](experiment/prompt.md)), and I kept every test exactly as written.

**My first assumption was that AI tests are weak. The data said no.**

| What I measured | Result |
|---|---|
| Tests written | 140 |
| Line and branch coverage | 100% |
| Breaks caught (each line broken, one at a time) | 55 of 56; the one miss changes nothing |

So I changed the question.
In real work the code may already be wrong when the AI writes its tests.
I planted one real bug in each function, the kind a review misses (an off-by-one, a lost `.upper()`, a wrong limit), and asked fresh runs for tests again.

| Function | Planted bug | The AI's own test name |
|---|---|---|
| discount | codes match only in upper case | `test_code_is_case_sensitive` |
| password | 12 characters is rejected | `test_exactly_12_chars_is_too_short` |
| refunds | day 30 is outside the window | `test_window_boundary_exactly_30_days_is_closed` |
| shipping | exactly 0.5 kg is not free | `test_at_threshold_is_not_free` |
| pagination | the page cap is 50, not 100 | `test_max_per_page_value` |

**The 132 tests caught 0 of 5 bugs, and 6 of them wrote a bug down as the correct behaviour.**
Coverage stayed at 100%, and every test passed.

## Day 2: Define

### Root cause

A test is only as good as its **oracle**: the source of truth for what is correct.
A test written from the code has one source of truth, the code. It turns whatever the code does into the expected result, bugs included.

This is not a model quality problem. A better model reads the code more carefully, and so writes the bug down more accurately.
It is an information-flow problem: the tester and the code share one source.
Coverage and mutation score cannot see it either, since both measure the tests against the same code.

### Ranked problems

1. **Tests from code confirm the code** (measured: 0 of 5 bugs). Silent, and it grows as AI writes more of both.
2. **Gaps in the spec hide bugs** (measured below: one missing sentence hid the refunds bug).
3. **Weak tests** (measured: 55 of 56 breaks caught). Real, but the smallest of the three.

### The fix, tested before I built it

I cut the flow: a fresh AI run saw only the spec and the function signatures, never the code ([`experiment/prompt-blind.md`](experiment/prompt-blind.md)).

| Tests written from | Bugs caught | Tests that assert a bug |
|---|---|---|
| The code | 0 of 5 | 6 |
| The spec alone | 4 of 5 | 0 |

The fifth bug, in refunds, was hidden: 9 tests failed on the buggy code **and** on the correct code, because my spec never said what `refund()` returns.
Once the spec said it ([`demo/spec.md`](demo/spec.md)), the spec-only tests caught that bug too.
So a disagreement between spec tests and code is a signal either way: a bug in the code, or a gap in the spec.

## Assumptions

- A change starts from a written spec, as in the quest's "implementation-ready specification".
- The code is Python, tested with pytest, with functions that take inputs and return outputs.
- Five functions, one model and one run each is a small sample: the numbers show a direction, not a rate.

## Engineering direction

**Bite**, a merge gate for AI-written code, in [`bite.py`](bite.py) (under 100 lines, standard library only):

1. **Write** the tests from the spec and the signatures alone, never the code.
2. **Agree**: the spec tests must pass on the code. A failure is a bug or a spec gap, never "fix the test".
3. **Bite**: each line of the code is broken, one at a time. The tests must catch every break.

A person is needed at one point only: when the spec tests and the code disagree, someone decides which one is wrong. That is a product decision, and it should be a person's.

Next: [`approach.md`](approach.md).
