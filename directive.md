# Directive

## Final assessment

**AI-written tests are strong, but they test the wrong thing.**
Written from the code, they cover 100% of it and catch 55 of 56 breaks, yet they caught 0 of 5 real bugs, and wrote 6 of those bugs down as correct.
Coverage, mutation score and a green build all stay green, so the bug ships with every signal saying it is safe.

**The fix is to change where the tests get their truth from, not to add more tests.**
Written from the spec alone, the same kind of AI tests caught 4 of 5 bugs and asserted none of them.
The fifth was hidden by a gap in the spec, and caught once the gap was closed.

Bite turns that into a merge gate in under 100 lines, with no dependency.
It writes the tests from the spec, requires them to agree with the code, and requires them to catch every break.

## The quest's questions

| Question | Answer from this work |
|---|---|
| How can we guarantee that code follows its spec? | Test it with tests that only know the spec. Tests written from the code cannot tell you this. |
| How can missing requirements be found early? | A spec test that fails on the code is a bug or a spec gap. Day 1 found two gaps that way. |
| Can verification become autonomous? | Writing tests, checking they bite and blocking the merge all run with no person. |
| Can strict rules stop invalid changes? | Bite exits 1, so it is a required check, and any error fails closed. |
| How can manual review cost less? | A person decides only on a `DISAGREES`, and Bite names the spec test it is about. |
| What if validation itself misses a problem? | Bite checks the tests too: tests that check nothing get 0/13 and fail. |

## Limitations

- **Small sample.** Five functions, one model, one run each. The direction is clear; the rates are not proven.
- **The gate is only as good as the spec.** A gap hides a bug, as refunds showed. Bite surfaces it but cannot fill it.
- **A shared misreading passes.** If the spec tests and the code read the spec the same wrong way, the two agree and Bite stays green.
- **False alarms.** A break that changes nothing (1 of 56 here) still fails the gate, and a person has to mark it.
- **Cost.** Every break re-runs the test file, so the time is breaks times suite time, over the whole module.
- **Scope.** Python and pytest, functions with inputs and outputs. No sandbox of its own.

## Next steps

1. **Break only the lines a pull request changed**, and run the breaks in parallel. This keeps the gate to minutes on a large codebase, inside the one-hour goal.
2. **Two independent test writers.** Where two fresh AI runs disagree on what the spec means, the spec is ambiguous. That points at the gap before any code is written.
3. **Turn a spec gap into a question.** On `DISAGREES`, draft the exact question for the spec's owner, with the two readings side by side.
4. **Run the gate in a container with no network**, as part of the tool.
5. **Map each test to a spec rule**, so a rule with no test is reported like a break no test catches.
