---
name: spec-writing
description: Guidance and templates for writing requirement, spec, plan and review documents in the specforge workflow. Use when drafting or reviewing .spec/ files or acceptance criteria.
---

# Spec writing

Use the templates in `${CLAUDE_SKILL_DIR}/templates/` for every document in a specforge project. Copy a template into the project's `.spec/` folder (or the repo root for CLAUDE.md files) and fill in every section. Do not drop sections.

| Document | Template | Written to |
|----------|----------|------------|
| Requirement | `requirement.md` | `.spec/requirement.md` |
| Spec | `spec.md` | `.spec/spec.md` |
| Plan | `plan.md` | `.spec/plan.md` |
| Review | `review.md` | `.spec/review.md` |
| Root project rules | `root-CLAUDE.md` | `CLAUDE.md` |
| Folder rules | `folder-CLAUDE.md` | `<folder>/CLAUDE.md` (max 10 lines) |

## Acceptance criteria

Number every criterion with a stable ID: `AC-1`, `AC-2`, and so on. Never renumber or reuse an ID. Each one is a single, observable, testable statement, written as Given / When / Then.

Good: `AC-3: Given an empty todo list, when the client requests GET /todos, then the response is 200 with an empty array.`

Bad: `The API should be fast and handle errors well.` (not observable, not testable)

## Rules

- Ask clarifying questions before writing the spec; at most 5.
- Scope says what is in. Out of Scope says what is deliberately left out. Both are required.
- Edge cases cover empty input, invalid input, duplicates, limits and failures.
- Plan tasks reference the AC-IDs they satisfy. Every AC maps to at least one task and one test.
- Review lists every AC with its code location, its test and a pass/fail status.
