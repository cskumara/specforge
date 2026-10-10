# specforge

A Claude Code plugin for spec-driven development with human approval gates.

You describe a feature. Claude writes a spec with numbered acceptance criteria, you approve it, Claude plans and writes failing tests, you approve that, and only then does Claude write code. Hooks enforce the gates, so Claude cannot skip them.

## Install

Requirements: Claude Code 2.1.295 or later, `python3` and `git` on your PATH, and `gh` if you want `/specforge:review` to open pull requests.

From inside Claude Code, add this repository as a marketplace and install the plugin:

```
/plugin marketplace add ./specforge
/plugin install specforge@specforge-marketplace
```

Use the path to your clone in place of `./specforge`. From a shell, the equivalents are:

```
claude plugin marketplace add ./specforge
claude plugin install specforge@specforge-marketplace
```

Run `/reload-plugins` or restart the session after installing. Then open the project you want to build in and run `/specforge:spec`.

## Workflow

```
 /specforge:spec <description>
        |  questions -> requirement.md, spec.md (AC-1, AC-2, ...), CLAUDE.md
        |  spec-reviewer checks it
        v
   [ YOU: /specforge:approve spec ]          spec_approved = true
        v
 /specforge:plan
        |  plan.md (tasks -> AC-IDs), folders + short CLAUDE.md files,
        |  test-writer creates FAILING tests from the acceptance criteria
        v
   [ YOU: /specforge:approve plan ]          plan_approved = true
        v
 /specforge:build [--mode strict|checkpoint|auto]
        |  feature branch; per task: RED (test:) -> GREEN (feat:) -> REFACTOR (refactor:)
        |  pauses by mode; stops after 3 failures of the same test
        v
 /specforge:review
        |  fresh code-reviewer, review.md (every AC -> code -> test),
        |  full test results, then a pull request (never merged)
        v
      done            /specforge:status shows where you are at any time
```

If `.spec/spec.md` changes after approval, the spec version goes up and both approvals reset. You approve again before work continues.

## Commands

| Command | What it does |
|---|---|
| `/specforge:spec <description>` | Asks up to 5 clarifying questions, writes `requirement.md`, `spec.md` and `CLAUDE.md`, runs `spec-reviewer`, then stops. |
| `/specforge:plan` | Refuses unless the spec is approved. Writes `plan.md`, folders with short `CLAUDE.md` files, and failing tests. Stops. |
| `/specforge:build [--mode strict\|checkpoint\|auto]` | Refuses unless spec and plan are approved. Builds on a feature branch with red, green, refactor per task. |
| `/specforge:review` | Fresh `code-reviewer`, writes `review.md`, opens a PR. Never merges. |
| `/specforge:status` | Read-only: phase, approvals, spec version, build mode, pending items. |
| `/specforge:approve spec\|plan` | Records your approval. Only you can run it: the model is not allowed to invoke it. |

Build modes: `strict` pauses after every task, `checkpoint` (default) after each milestone, `auto` only before risky actions such as deleting files, changing dependencies, migrations, external calls or force pushes.

## Gates

State lives in `.spec/state.json` in your project:

```json
{ "phase": "spec", "spec_approved": false, "plan_approved": false,
  "spec_version": 1, "build_mode": "checkpoint" }
```

Hooks read it and block with a clear reason on stderr:

| Gate | Rule |
|---|---|
| Edits to source folders (`src`, `app`, `lib`, at any depth) | Blocked until `spec_approved` and `plan_approved` are both true. |
| Edits to test folders (`tests`, at any depth) | Blocked until `spec_approved` is true. This lets the plan phase write failing tests. |
| `CLAUDE.md` files inside those folders | Treated like tests: allowed once the spec is approved. |
| Edits to `.spec/state.json` | Always blocked. Approvals go through `/specforge:approve`. Shell commands that write to it are blocked too, on a best-effort basis. |
| `git commit` | Once both approvals are in, blocked while the test suite fails. Commits whose message starts with `test:` are let through, so failing tests (RED) can be committed. |
| Spec changes | Editing `.spec/spec.md` after approval bumps `spec_version` and resets both approvals. |

Everything else is allowed, including everything under `.spec/`. A project with no `.spec/` folder is left alone. If the state or config file is unreadable, or a hook script fails, the hook blocks rather than guessing.

## Configuration

Optional `.spec/config.json`:

```json
{
  "code_dirs": ["src", "app", "lib", "backend"],
  "test_dirs": ["tests", "spec_tests"],
  "test_command": "make test"
}
```

- `code_dirs`: folder names (not paths) that count as source code. Default `src`, `app`, `lib`.
- `test_dirs`: folder names that count as tests. Default `tests`. A path inside both, such as `app/tests/x.py`, counts as a test.
- `test_command`: how to run the suite. If unset, specforge looks for `pytest`, then `npm test`, then `flutter test`. If it finds none, or the runner is not installed, commits are blocked with a message telling you to set it.

## Example session

A todo API, illustrative:

```
> /specforge:spec REST API for todos: create, list, complete, delete
Claude: A few questions: 1) Storage: in memory or SQLite? 2) Auth needed? ...
> In memory, no auth.
Claude: Wrote .spec/requirement.md, .spec/spec.md (6 acceptance criteria) and CLAUDE.md.
        spec-reviewer: READY FOR APPROVAL. Review .spec/spec.md, then run /specforge:approve spec.

> /specforge:plan
Claude: The spec is not approved. Review .spec/spec.md, then run /specforge:approve spec.
> /specforge:approve spec
Claude: Spec approved (version 1, 6 acceptance criteria). Next: /specforge:plan.

> /specforge:plan
Claude: Wrote .spec/plan.md: 2 milestones, 8 tasks. Created src/ and tests/ with CLAUDE.md files.
        test-writer created 9 failing tests (test_ac1_..., test_ac2_..., ...).
> /specforge:approve plan
Claude: Plan approved. Next: /specforge:build.

> /specforge:build --mode checkpoint
Claude: Branch feature/todo-api. T1 RED: test fails as expected. test: commit.
        T1 GREEN: full suite passes. feat: commit. ...
        Milestone 1 complete. Approve to continue?
> yes
Claude: ... all 8 tasks done, 9 tests passing. Run /specforge:review.

> /specforge:status
Phase: build. Spec approved: yes. Plan approved: yes. Spec version: 1.
Pending: no tasks left. Next: /specforge:review.

> /specforge:review
Claude: review.md written: AC-1..AC-6 all pass, no gaps.
        PR opened: https://github.com/you/todo-api/pull/1 (not merged).
```

## Limitations

- **TDD order is mostly instructions.** `/specforge:build` and the `test-writer` agent tell Claude to go red, green, refactor, and hooks block commits while tests fail. Nothing stops Claude from writing code and its test in one go. `/specforge:review` checks the git history and reports any task whose `test:` commit does not come before its `feat:` commit, but it reports, it does not block.
- **A `test:` commit can contain anything.** The prefix only skips the test run. The review step is where misuse shows up.
- **The Bash guard for `state.json` is best effort.** Hooks cannot reliably parse every shell command. Someone determined could write to the file by a route the pattern does not recognize, or run `state.py approve` through Bash. `/specforge:approve` cannot be invoked by the model, but the underlying script is a normal Python file.
- **The commit gate starts after both approvals.** Before that, no source code can be written, and committing planning documents with failing tests would deadlock the plan phase.
- **Hooks need Claude Code 2.1.295 or later** for `onFailure: block`. On older versions a crashing hook script does not block.
- `python3` must be on the PATH, and the test runner must be installed in the environment Claude runs commands in.

## Development

The plugin is built test first. Scripts have behavior tests, and prompts (commands, agents, skill, templates) have structure tests.

```
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/pytest -q
claude plugin validate .
```

Layout:

```
.claude-plugin/   plugin.json, marketplace.json
commands/         spec, plan, build, review, status, approve
agents/           spec-reviewer, test-writer, code-reviewer
skills/           spec-writing (SKILL.md and templates)
hooks/hooks.json  gate wiring
scripts/          state.py, config.py, gate_check.py, test_gate.py
tests/            structure/ and scripts/
```
