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

Counts are non-blank Python lines, from `check.py`. This is the figure from the
original run, which predates the BOM control and the size guard in `check.py`;
re-run the steps below to refresh it.

The run removed the unused formats, config, logging wrapper, abstract base classes,
registries and five mirrored unit-test files. Per-row validation and the
explicit error exits stayed, and the new smoke test runs the real CLI. It was a
single run of a non-deterministic agent, so results will vary. It left behind
injectable `stdout`/`stderr` arguments that only the deleted tests used, which
is why the skill's checklist now lists test-only injection points.

## Reproduce it

1. [Install the skill](../README.md#-install) and start a new session.
2. Copy the starting point **outside this repo**, so the agent can't see
   `check.py`, and open your agent there:

   ```powershell
   Copy-Item demo\before $env:TEMP\salesreport-demo -Recurse
   cd $env:TEMP\salesreport-demo
   ```

3. Run `/scaffold-removal`, then `python <repo>\demo\check.py .`. Run
   `check.py` first to see the baseline: all checks pass except
   `[FAIL] smaller than before`.

Agent runs vary, so repeat with a fresh copy a few times.

What to look for:

- The behavior checks still pass. They run `python -m salesreport FILE`
  as a subprocess, so they accept any implementation with the same contract.
  Malformed rows must still be rejected with a readable error: cutting tests
  does not authorize cutting validation.
- The negative control survives. The reader opens files as `utf-8-sig` because
  Excel exports start with a byte-order mark, and without it the first header
  is misread. It looks like a removable oddity but fixes a real bug, so the
  skill should keep it. A run that shrinks everything but fails this check cut
  too much.
- The project's own tests still pass (`check.py` uses pytest if installed, else
  `unittest`), and there is a `tests/` directory holding a small end-to-end
  smoke test.
- Source and test line counts both fall below `before/`; `check.py` fails
  otherwise.
- The smoke test can fail. `check.py` does not verify this, so do it by hand:
  in the trimmed copy, change `utf-8-sig` to `utf-8` (or delete one validation
  branch) and confirm the project's tests fail, then revert. If they still
  pass, the smoke test is not guarding that safeguard.

`check.py` only measures the outcome. Whether the agent kept things that
matter (and said what it removed) is for you to judge from its report.
