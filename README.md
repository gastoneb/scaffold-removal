# scaffold-removal

An agent skill that pares a finished feature back to what a reviewer needs to
see. Run it once the code works and before you open the pull request.

## Why

Agents write a lot of code, even with skills that tell them to write less. The
reason is how features get built: code and tests are added as the feature
grows, and a lot of scaffolding goes up to reach a working MVP. Abstractions
for formats nobody ended up using, options nobody sets, debug logging, and unit
tests that mirror the implementation line by line.

Once the MVP works, much of that is cruft. It makes the diff bigger, the review
slower, and the result harder to maintain. Skills that restrain the agent while
it writes (such as [ponytail](https://github.com/DietrichGebert/ponytail)) help,
but they cannot remove what was only needed on the way. This skill is the second
pass: with the feature working, it asks which of the scaffolding is still
needed, and removes the rest.

The idea is simple: **YAGNI, applied after the proof of concept.** Keep the
working integration, not the history of how it was developed.

## What it does

When invoked, the agent:

1. Scopes itself to what your change added or touched.
2. Pins the end-to-end behavior that must keep working, and runs it first.
3. Deletes dead wrappers, speculative options, single-use abstractions,
   abandoned experiments and debug code.
4. Replaces overlapping unit tests with one compact end-to-end smoke test
   (about 100 lines for the feature).
5. Moves product-specific detail out of the main README.
6. Reports before and after sizes, what was removed, what was deliberately
   kept, and what is no longer covered.

It does not remove input validation, error handling, credential protection,
locking or publication safeguards. It asks before changing behavior anyone may
rely on, and it does not commit. Details are in
[SKILL.md](skills/scaffold-removal/SKILL.md).

## Example

The [demo](demo) is a small CSV report CLI built the way an agent would build
it step by step. Trimmed to its essentials, the same behavior needs:

| | Source lines | Test lines |
|---|---|---|
| Before | 151 | 262 |
| After (reference) | 30 | 25 |

The malformed-input check is kept. See [demo/README.md](demo/README.md) to try
it with your own agent.

A real run of the skill on the "before" project, with no access to the
reference result, produced:

| | Source lines | Test lines | Files |
|---|---|---|---|
| Before | 151 | 262 | 8 source, 5 test |
| After one run | 38 | 39 | 3 source, 1 test |

It removed the unused formats, config, logging wrapper, abstract base classes,
registries and five mirrored unit-test files. Per-row validation and the
explicit error exits stayed, and the new smoke test runs the real CLI. It was a
single run of a non-deterministic agent, so results will vary. That run left
behind injectable `stdout`/`stderr` arguments that only the deleted tests used,
which is why the checklist now lists test-only injection points.

## Install

The skill is one file: [skills/scaffold-removal/SKILL.md](skills/scaffold-removal/SKILL.md).
Copy the `scaffold-removal` folder into your agent's skills directory.

**GitHub Copilot** (VS Code and CLI), for one project or for all of them:

```powershell
git clone https://github.com/gastoneb/scaffold-removal
Copy-Item scaffold-removal\skills\scaffold-removal .github\skills\ -Recurse   # this project
Copy-Item scaffold-removal\skills\scaffold-removal ~\.copilot\skills\ -Recurse # all projects
```

**Claude Code:** the same folder goes in `.claude/skills/` (project) or
`~/.claude/skills/` (all projects).

**Skills CLI:** if you use the [`skills`](https://github.com/vercel-labs/skills)
installer, `npx skills add gastoneb/scaffold-removal` picks up the folder
and installs it for the agents you choose.

**Any other agent:** paste the body of `SKILL.md` into your rules file
(`AGENTS.md`, Cursor rules, and so on). The skill is plain instructions, with no
code or dependencies.

Restart the session after installing so the agent notices the new skill.

## Use

- Ask in plain words: "remove the scaffolding", "pare this down for review".
  The description in `SKILL.md` lets the agent load the skill on its own.
- Or invoke it by name where your agent supports it, for example
  `/scaffold-removal` in Copilot and Claude Code, or `$scaffold-removal` in
  Codex. Slash-command support varies by agent and version.

A good habit is to run it as the last step before pushing, then read the
agent's report and the diff. The skill cuts aggressively by design; you decide
what stays.

## Repo layout

```
skills/scaffold-removal/SKILL.md   the skill
demo/before/                       an overbuilt feature
demo/after/                        reference result
demo/check.py                      behavior checks and size report
```

CI runs `demo/check.py` against both versions, which checks the demo itself, not
the skill. Whether the skill trims well is judged by running it, as described in
[demo/README.md](demo/README.md).

## License

[MIT](LICENSE)
