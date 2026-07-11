---
name: dependency-upgrade
description: Safely audit and upgrade outdated project dependencies in small verified batches instead of one large bump. Use when the user asks to upgrade/update dependencies, bump package versions, check for outdated packages, or address dependency vulnerabilities.
---

# Dependency upgrade

Treat this as a risk-managed operation, not a one-shot bump — a bad batch upgrade is
hard to untangle later.

1. **Baseline first.** Confirm the build/test suite passes *before* touching any
   dependency, so any failure after upgrading is attributable to the upgrade, not
   pre-existing breakage.

2. **List what's outdated** with the ecosystem's own tool (`npm outdated` /
   `pnpm outdated`, `pip list --outdated`, `go list -u -m all`, `cargo outdated`, etc.)
   rather than guessing versions. Note which bumps are patch/minor (usually safe) vs
   major (likely to have breaking changes).

3. **Upgrade in small batches, not all at once:**
   - Patch/minor bumps for unrelated packages can usually go together.
   - Each major-version bump gets its own batch — check that package's
     changelog/migration guide for breaking changes first, and apply any required code
     changes alongside the bump.
   - Never bundle a framework/runtime major upgrade with unrelated dependency bumps.

4. **After each batch: install, build, run the full test suite.** If something breaks,
   isolate which package in the batch caused it (bisect the batch if needed) before
   deciding whether to fix the calling code or hold that package back.

5. **If a batch can't be made to pass**, stop and report which package and why, rather
   than force-merging a broken upgrade or silently reverting without explanation.

6. **Prioritize security-relevant upgrades** (check `npm audit` / `pip-audit` / GitHub
   Dependabot alerts if present) ahead of purely cosmetic version bumps when time is
   limited.

7. **Summarize what changed and why** at the end: which packages moved, which were
   held back and the reason, and any code changes required by breaking changes.
