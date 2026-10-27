# Demo: trim an overbuilt feature

[before/](before) is a small CLI, `salesreport`, that prints total revenue per
region from a CSV file. It works, and it looks like what an agent leaves behind
after building the feature step by step: a reader and formatter registry with
abstract base classes, JSON and XML options nobody uses, a config class driven
by environment variables, a logging wrapper, and five test files that mirror
the implementation.

## Result of one real run

The skill was run on a copy of `before/`, with no reference solution available:

| | Source lines | Test lines | Files |
|---|---|---|---|
| Before | 151 | 262 | 8 source, 5 test |
| After | 38 | 39 | 3 source, 1 test |

Counts are non-blank Python lines, from `check.py`, and come from a single run
that predates the BOM control and the size guard; reproduce it below to refresh
them. The run removed the unused formats, config, logging wrapper, abstract
base classes, registries and five mirrored unit-test files. Per-row validation
and the explicit error exits stayed, and the new smoke test runs the real CLI.

## Reproduce it

1. [Install the skill](../README.md#-install) and start a new session.
2. Copy the starting point **outside this repo**, so the agent can't see
   `check.py`, and open your agent there:

   ```powershell
   Copy-Item demo\before $env:TEMP\salesreport-demo -Recurse
   cd $env:TEMP\salesreport-demo
   ```

3. Run `python <repo>\demo\check.py .` for the baseline: everything passes
   except `[FAIL] smaller than before`. Then run `/scaffold-removal` and
   `check.py` again.

Agent runs vary, so repeat with a fresh copy a few times.

What to look for:

- The behavior checks pass. They run `python -m salesreport FILE` as a
  subprocess, so any implementation with the same contract passes. Malformed
  rows must still be rejected: cutting tests does not authorize cutting
  validation.
- The BOM control survives. The reader opens files as `utf-8-sig` because Excel
  exports start with a byte-order mark. It looks removable but fixes a real bug,
  so a run that fails this check cut too much.
- The project's own tests pass (pytest if installed, else `unittest`) and
  `tests/` holds a small end-to-end smoke test.
- Source and test line counts are both below `before/`.
- The smoke test can fail. `check.py` does not verify this, so do it by hand:
  change `utf-8-sig` to `utf-8` in the trimmed copy and confirm the tests fail,
  then revert.

`check.py` only measures the outcome. Whether the agent kept what matters and
reported what it removed is for you to judge from its report.
