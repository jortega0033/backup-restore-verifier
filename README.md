# Backup Restore Verifier

A local test restore workbench that checks recovered files against a known manifest.

This repository contains the plan for the first implementation epic and a scaffold (module stubs, smoke tests, CI). No product behaviour is implemented yet.

- [Product requirements](docs/PROJECT-PLAN.md#product-requirements)
- [Technical design](docs/PROJECT-PLAN.md#technical-design)
- [Epic and implementation tickets](https://github.com/jortega0033/backup-restore-verifier/issues)

The first plan of phase 1 said 12–19 engineering hours. Its open tickets, with tests and review, add up to 48 to 78 hours; the whole program is larger and is described below. All figures are estimates.

Licensed under the [MIT License](LICENSE).

## Program goal

Turn the verifier into a recovery engine: own archive and compression decoders, own deduplicating snapshot store, repair of damaged backups, reading of file systems from raw image files, and checks inside the recovered databases and repositories, with no archive, compression, file-system or database library in the engine.

The program is planned ([#35](https://github.com/jortega0033/backup-restore-verifier/issues/35)). Phase 1 is the current epic [#1](https://github.com/jortega0033/backup-restore-verifier/issues/1) and the only phase with tickets.

**Score.** Share of a corpus of valid and damaged archives and disk images whose recovered bytes equal those of two independent tools, and the share of injected damage that is found and, up to the stated limit, repaired.

| Phase | Content | Hours (rough) | Issue |
|---|---|---|---|
| 1 | The current epic and its tickets | 48 to 78 | [#1](https://github.com/jortega0033/backup-restore-verifier/issues/1) |
| 2 | Archives and compression | 150 to 260 | [#36](https://github.com/jortega0033/backup-restore-verifier/issues/36) |
| 3 | Snapshot store | 120 to 210 | [#37](https://github.com/jortega0033/backup-restore-verifier/issues/37) |
| 4 | Damage and repair | 110 to 190 | [#38](https://github.com/jortega0033/backup-restore-verifier/issues/38) |
| 5 | File systems from images | 160 to 280 | [#39](https://github.com/jortega0033/backup-restore-verifier/issues/39) |
| 6 | Inside the recovered data | 140 to 240 | [#40](https://github.com/jortega0033/backup-restore-verifier/issues/40) |

About 730 to 1260 engineer hours in total: rough estimates, not measurements. The numbers in the score and the finish lines are targets until a run shows them. Only phase 1 has tickets to work; the sub-issues of a later phase are written when it starts. No single session is expected to reach the end.
