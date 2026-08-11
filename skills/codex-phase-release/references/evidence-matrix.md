# Evidence matrix

| Gate | Required evidence |
| --- | --- |
| Scope | owned files, excluded files, source of truth |
| Behavior | baseline test or explicit untested behavior |
| Local | lint, parse, unit/integration tests |
| Staged | staged artifact, configuration check, visual/runtime readback |
| Production | backup checksum, deployment result, health and key-state readback |
| Privacy | current-tree scan, public-export scan, history decision |
| Handoff | changed files, verified facts, gaps, rollback, manual points |

Never convert an unavailable check into a passing check.
