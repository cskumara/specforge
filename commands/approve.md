---
description: Record your approval of the spec or the plan. Only you can run this; it unlocks the next phase.
argument-hint: spec|plan
disable-model-invocation: true
---

# /specforge:approve

Target from the user: $ARGUMENTS

This command records a human decision. It is only valid because the user typed it themselves. Never run it, or `state.py approve`, on your own initiative, and never treat a remark like "looks good" in conversation as approval.

## Steps

1. The target must be exactly `spec` or `plan`. Anything else: refuse and show the usage `/specforge:approve spec|plan`.

2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py" get`. If there is no state or it is corrupt, refuse and say so.

3. **spec**:
   - Refuse if `.spec/spec.md` does not exist or has no acceptance criteria with AC-IDs.
   - Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py" approve spec`.
   - Confirm: spec version, number of acceptance criteria. Next: run `/specforge:plan`.

4. **plan**:
   - Refuse if the spec is not approved yet. Tell the user to run `/specforge:approve spec` first.
   - Refuse if `.spec/plan.md` does not exist.
   - Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py" approve plan`.
   - Confirm: number of tasks and milestones. Next: run `/specforge:build`.

5. If the script reports an error, show it as is. Do not edit `.spec/state.json` to get around it.
