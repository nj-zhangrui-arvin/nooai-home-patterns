---
name: codex-phase-release
description: "Run a bounded, evidence-based delivery phase from scope through tests, staged verification, commit, and handoff. Use when a user asks Codex to complete work in stages, avoid losing the main thread, report progress clearly, or prepare a reviewable phase release."
---

# Codex Phase Release

Keep one explicit phase goal active and make completion evidence visible.

## Workflow

1. State the single current phase outcome in the first line.
2. Identify the source of truth, write scope, privacy boundary, and destructive-action boundary.
3. Lock existing behavior with the smallest relevant tests before cleanup or refactor.
4. Execute one bounded change set. Suppress unrelated improvements unless they block the phase.
5. After an incident, close the incident with evidence and return to the original phase.
6. Run local gates, then staged/runtime read-only verification when applicable.
7. Review requirement compliance first, then code and documentation quality. Do not let a clean implementation hide a missed requirement.
8. Match every success claim to an observable outcome. A generic healthy response does not prove the intended provider, route, state, or deployment changed.
9. Separate verified facts, inferred conclusions, known gaps, and manual intervention points.
10. Create one independently revertible commit and a compact handoff.

For multi-step work, number at most five current steps and repeat the active step in each progress update. Give estimates only when grounded; prefer an observable next checkpoint over invented precision.

## Output contract

Use this order:

1. phase result or active step;
2. evidence;
3. risk or blocker;
4. one next action;
5. manual intervention points, only when present.

Do not add generic preambles, repeat completed analysis, or end with an empty offer to continue.

## Exceptions

Pause when the next action is destructive, irreversible, legally meaningful, changes external authority, or depends on a real user preference. Escalate after three consecutive failures with the same root blocker.

Read `references/evidence-matrix.md` when a phase includes production deployment or public release.
Read `references/prior-art.md` when adapting this workflow to another agent harness.
