# Prior art and absorbed boundaries

This Skill is deliberately narrower than a full development methodology.

- [i-have-adhd](https://github.com/ayghri/i-have-adhd) informed action-first output, bounded lists, explicit state, and suppression of tangents.
- [Superpowers](https://github.com/obra/superpowers) informed two-stage review: requirement compliance before code quality, fresh verification before completion claims, and isolated/revertible execution where the repository supports it.

Absorb the principles, not upstream wording or implementation. Keep this Skill explicit-only, preserve the host agent's authorization model, and do not require a worktree when the user has intentionally chosen the current worktree or the repository cannot support one safely.

For outcome verification, first name the observable that must change. Examples include the selected provider in a response, a new deployed artifact checksum, or a runtime state transition. A generic HTTP success or an agent report is not sufficient evidence by itself.
