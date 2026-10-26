# Demo: trim an overbuilt feature

[before/](before) is a small CLI, `salesreport`, that prints total revenue per
region from a CSV file. It works, and it looks like what an agent leaves behind
after building the feature step by step: a reader and formatter registry with
abstract base classes, JSON and XML options nobody uses, a config class driven
by environment variables, a logging wrapper, and five test files that mirror
the implementation.

| | Source lines | Test lines |
|---|---|---|
| [before/](before) | 151 | 262 |
| [after/](after) (reference result) | 30 | 25 |

Counts are non-blank Python lines, from `check.py`.

## Try it

1. Copy the starting point somewhere disposable and open it in your agent:

   ```powershell
   Copy-Item demo\before $env:TEMP\salesreport-demo -Recurse
   cd $env:TEMP\salesreport-demo
   ```

2. Confirm the baseline: `python <repo>\demo\check.py .`. Everything passes.
3. Ask your agent to run the skill, for example `/scaffold-removal`, or
   "remove the scaffolding from this project".
4. Run `python <repo>\demo\check.py .` again.

What to look for:

- The four behavior checks still pass. They run `python -m salesreport FILE`
  as a subprocess, so they accept any implementation with the same contract.
  Malformed rows must still be rejected with a readable error: cutting tests
  does not authorize cutting validation.
- The project's own tests still pass, and there is a `tests/` directory
  holding a small end-to-end smoke test.
- Source and test line counts fall sharply. [after/](after) is one possible
  result, not the only right one.

`check.py` only measures the outcome. Whether the agent kept things that
matter (and said what it removed) is for you to judge from its report.
