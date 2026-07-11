---
name: debug-systematically
description: Structured root-cause debugging workflow — reproduce, isolate, form a hypothesis, verify the real fix, and check for related occurrences. Use when the user reports a bug, crash, error, unexpected behavior, flaky test, or asks "why is this failing" / "this isn't working" / "help me debug this".
---

# Debug systematically

Don't jump straight to a patch. Work the problem in order:

1. **Reproduce reliably.** Get a minimal, repeatable trigger (a failing command, test,
   input, or set of steps) before touching any code. If it can't be reproduced yet,
   that's the first task — add logging, narrow the input, or ask the user for the exact
   steps/environment rather than guessing.

2. **Isolate the smallest failing case.** Strip away unrelated code/config/data until
   only the minimal reproduction remains. If the bug is a regression, bisect: find the
   last known-good commit/state and the first bad one (`git bisect`, or manually
   checking out candidate commits) rather than reading the whole diff history.

3. **Form a hypothesis before editing.** State in one sentence what you believe is
   wrong and why the symptoms match. If you can't state a specific mechanism ("X is
   null because Y runs before Z"), you don't understand it well enough to fix it yet —
   keep investigating (add a breakpoint/print, read the actual stack trace, check
   assumptions about types/ordering/state) instead of trying random changes.

4. **Fix the cause, not the symptom.** A fix that makes the specific reproduction case
   pass but doesn't address the mechanism from step 3 is a red flag — e.g. adding a
   null check instead of finding why the value is null, or widening a try/catch instead
   of fixing the failing call. Prefer the fix that makes the invariant hold in general.

5. **Verify against the original reproduction**, then re-run the broader test suite —
   a fix that's correct for the minimal case can still break something the minimal
   case didn't exercise.

6. **Check for related occurrences.** If the root cause is a pattern (e.g. a missing
   null check, an off-by-one, a race condition), grep for the same pattern elsewhere in
   the codebase — bugs like this are rarely singletons.

Report what the root cause actually was, not just "fixed it" — the mechanism is the
useful part for the user to sanity-check.
