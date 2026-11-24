# Implementer map

Status: **scaffold only: the modules exist as empty stubs and no product behaviour is implemented.** This page maps the boundaries that [PROJECT-PLAN.md](PROJECT-PLAN.md) requires onto a module layout so that parallel tickets do not collide. It adds no requirement; the plan wins where they differ. The names are the orchestrator's proposal, fixed by the scaffold; a ticket that changes one corrects this page in the same pull request.

## Planned module map

| Boundary | Module | Owns | Parent ticket |
|---|---|---|---|
| Path profile | `restore_verifier/paths.py` | Canonical relative paths, collisions, limits | #2 (contract), #3 |
| Workspace | `restore_verifier/workspace.py` | Marker, init, controlled locations, fixture seeding, workspace lock | #2 |
| Contracts | `restore_verifier/contracts.py` | Manifest, staged input, attempt and row shapes, states, limits | #2 |
| Sources | `restore_verifier/sources.py` | Descriptor-relative folder walk, ZIP member intake | #3 (folder inventory), #4 |
| Manifest | `restore_verifier/manifest.py` | Hashing, canonical bytes, identity | #3 |
| Restore | `restore_verifier/restore.py` | Bounded streaming into a private tree, capacity checks | #4 |
| Compare | `restore_verifier/compare.py` | Second read of the output, join, counts, outcome | #5 |
| Storage | `restore_verifier/store.py` | SQLite records, request IDs, final commit, reports | #5, #6 |
| Jobs | `restore_verifier/jobs.py` | One worker, progress, cancellation, interruption, retry | #5 (one run), #6 |
| HTTP | `restore_verifier/server.py` | Loopback bind, request guards, routes, static assets | #2, #5, #6 |
| Browser assets | `restore_verifier/static/` | Start, progress, result table, history | #2, #5, #6 |
| Test oracle | `tests/oracle.py` | Direct reads of restored bytes against recorded expectations | #4, #5 |

Dependency direction: `server` depends on `jobs` and `store`; `jobs` on `restore`, `compare` and `store`; `restore` and `manifest` on `sources`; `sources` on `paths`; all on `contracts`, which imports nothing from the package. `tests/oracle.py` imports nothing from the package.

## Freeze points

Parallel tickets rely on these shapes. A ticket that changes a frozen shape updates this page and every dependent ticket in the same pull request.

- **Manifest, staged input, attempt state and comparison row shapes**, in a documented fixture: ticket #2, before #3 and #4 start in parallel.
- **Restored inventory interface** read by the comparison: #4 provides it.
- **Canonical report payload** without job IDs and times: #5 documents it before #6 and #7 rely on it.

## What is verified where

Portable tests run locally and in CI on Linux and Windows. Tests that need directory descriptors, no-follow opening or process signals run on Linux CI and are skipped on Windows with a printed reason. Browser checks are manual in Chrome unless a ticket states a headless run.
