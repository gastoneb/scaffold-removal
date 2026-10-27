---
name: scaffold-removal
description: 'Use before opening a pull request, or when asked to remove proof-of-concept scaffolding: shrink code and tests to what a reviewer needs, replace excessive tests with an end-to-end smoke test, and keep product-specific docs out of the main README. Triggers: "remove the scaffolding", "pare this down for review", "this is too big to review", "clean up before the PR".'
---

# Scaffold removal

YAGNI, applied after the proof of concept: **you won't need to keep it.** Code,
tests and docs written while figuring things out were scaffolding. Once the
integration works, assume most of that scaffolding can go. Keep the working
integration, not the history of its development. Optimize for less code to
maintain and review, not shorter lines or moving complexity into new helpers.

Run this once the feature works and before the change goes to review. Other
skills limit what gets written; this one removes what was needed to get there.

## Workflow

1. **Scope.** Work on what this change added or touched (`git diff` against the
   base branch, plus untracked files). Ask for the base if it is unclear. Leave
   unrelated code alone. Record the starting size of source and tests
   separately, e.g. `git diff --stat <base> -- . ':!tests'` and
   `git diff --stat <base> -- tests`.
   Make every cut revertible with a checkpoint that keeps the change in the
   working tree, so the diff stays visible: a temporary commit or branch, or
   `git stash push -u -m scaffold-removal-checkpoint` immediately followed by
   `git stash apply`. Never leave the target changes only in the stash.
2. **Pin the outcome.** Read the affected implementation, callers, tests and
   documentation. State the end-to-end behavior that must keep working and run
   its existing checks first. If nothing exercises it, write that one test
   before cutting anything.
3. **Cut code.** Delete what does not earn its place (see the checklist below).
   Reuse the project's existing path. Do not introduce a framework, base class or
   helper to make the cleanup look organized. Keep code readable: no dense
   one-liners or elaborate fixture factories to claim a smaller diff, and no
   storage-layout changes or dependency swaps just to save lines. Removing a
   dependency this change added and nothing now uses is fine.
4. **Ask before changing behavior.** Decide by provenance. Behavior introduced
   in this change and never released or documented is free to cut. Behavior
   already on the base branch, released or documented needs the user's
   approval first. "Nobody sets it" needs evidence: grep docs, scripts, CI and
   callers before deleting a flag or environment variable that is already on the
   base branch. Reject unsupported formats explicitly; never silently
   reinterpret them or delete user data.
5. **Cut tests.** Keep a test only if it would still pass after a correct
   rewrite of the internals. Delete tests that assert on mocks, call order,
   private helpers or removed code, and overlapping per-branch tests. Cover the
   remaining behavior with one compact end-to-end smoke test. Keep focused
   input-to-output tests for logic with real edge cases (parsing, money, dates).
   Keep tests small enough to review at a glance; this is a scope goal, not a
   reason to minify code or hide test setup elsewhere.
6. **Make the smoke test real.** Exercise the public entry point, processing and
   persistent output. Mock external services and transfers, not the
   implementation being tested. Assert meaningful results, not merely that the
   command exits successfully. Reuse shared tests rather than repeating them
   for each integration. Keep one case for each safeguard that remains
   (for example, a rejected malformed input). Confirm the test can fail by
   temporarily breaking one safeguard.
7. **Trim docs.** Keep the main README focused on setup, common usage and a
   short feature summary. Put necessary product-specific details in one linked
   guide. Delete notes that only narrate how the code was developed.
8. **Verify.** Run the smoke test, focused shared regressions and existing
   lint/type checks. Confirm nothing outside the change broke.

## Cut checklist

Usually scaffolding:

- Abstract base classes, registries, factories and plugin points with one
  implementation.
- Alternative formats, backends or code paths from abandoned experiments.
- Config options, flags and environment variables nobody sets; their parsing
  and their tests.
- Parameters, injection points and hooks that exist only so the removed unit
  tests could reach internals (injected streams, clocks, factories).
- Wrappers that only forward a call; logging, tracing and debug dumps added to
  find the bug; commented-out code; stale TODOs.
- Defensive code for states that cannot happen inside the same trust boundary.
- Unit tests that mirror the implementation, one-per-branch tests that the smoke
  test already covers, and tests of removed code.
- Helper scripts, sample data, notebooks and notes left from exploration,
  unless the smoke test uses them.
- Dependencies this change added that nothing uses any more.

Keep, even if it looks like clutter:

- Input validation at trust boundaries, explicit errors, credential handling,
  locking, migrations and publication safeguards.
- Behavior that other code, users or documented interfaces depend on.
- A regression test for a bug that actually happened.
- Anything the reviewer could not recreate from the remaining code.

When unsure whether something is scaffolding, check who calls it. Public
exports, entry points, config keys, documented interfaces and string-keyed
lookups (registries, reflection) count as callers, so search for those too. If
nothing real calls it, remove it; if it guards against failure, keep it and say
so. Code that looks odd but fixes a real bug (an encoding flag, a retry) is a
safeguard: keep it.

## Boundaries

- Cutting tests does not authorize cutting runtime validation or safeguards (see
  Keep above). Preserve supported output formats and data semantics unless the
  user agrees.
- Do not delete unrelated tests or rewrite shared infrastructure.
- Do not commit changes unless asked.

## Report

Finish briefly, for the reviewer:

- **Size:** before and after (lines or files, source and tests separately).
- **Removed:** the main groups, one line each.
- **Still runs end to end:** what the remaining smoke test verifies.
- **Kept on purpose:** safeguards that look removable but were not.
- **Not checked:** the reduced edge-case coverage and any mocked external
  boundaries, stated explicitly.
