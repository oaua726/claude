---
name: test-writer
description: Write tests that match the project's existing test framework and conventions instead of inventing new ones. Use when the user asks to write tests, add test coverage, test a function/module/PR, or add a regression test for a bug that was just fixed.
---

# Test writer

Before writing a single test, figure out what already exists — don't introduce a second
test framework or a new file-naming/assertion style into a project that already has one.

1. **Detect the existing convention.** Look for existing test files near the code under
   test, plus config that names the framework (`package.json` devDependencies,
   `pytest.ini`/`pyproject.toml`, `go.mod`, `Cargo.toml`, CI config). Match: framework
   (jest/vitest/pytest/go test/...), file naming (`*.test.ts` vs `*_test.py` vs
   `test_*.py`), directory layout (colocated vs `tests/`), assertion style, and how
   mocks/fixtures are set up. If truly nothing exists yet, pick the ecosystem-standard
   default and say so rather than silently deciding.

2. **Cover, in order of priority:**
   - The happy path the code is meant to handle.
   - Edge cases: empty/null/zero inputs, boundary values, error paths the code
     explicitly handles.
   - A regression test for any specific bug just fixed — one that fails on the old code
     and passes on the new code, named so the bug it guards against is obvious later.

3. **Don't test implementation details.** Assert on observable behavior (return values,
   thrown errors, side effects like calls to a mock) rather than internal state, so
   tests survive refactors that don't change behavior.

4. **Keep tests independent and deterministic.** No shared mutable state between tests,
   no reliance on execution order, no real network/filesystem/clock unless that's
   specifically what's under test (use fakes/mocks for those).

5. **Run the new tests** (and the surrounding suite) before calling it done — a test
   that hasn't been run may not even compile, and a test that passes without the fix
   present isn't testing anything.
