# CLAUDE.md

Working instructions for this repository. Read this file first, then the documents it links to. It does not repeat them.

## What this is

A local workbench for a freelancer or small team: save a reference manifest, restore a prepared folder or ZIP backup into a fresh directory, and read which files matched, changed, were missing or appeared unexpectedly. The report is the same after a restart and the fixtures stay untouched. Python 3.11 standard library and SQLite on Linux, `127.0.0.1` only, generated files only.

**Nothing is implemented yet.** The repository holds the plan, the delivery tooling and the backlog in epic #1. Commands marked planned below do not work yet. Do not describe a planned thing as working, and do not claim a passing baseline: there is none.

## Sources of truth

| Topic | Document |
|---|---|
| Product scope, design, fixtures with expected values | [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md) |
| Planned module map, freeze points, planned versus implemented | [docs/architecture.md](docs/architecture.md) |
| Backlog | Epic issue #1 and its child tickets on GitHub. The epic's table is authoritative for order, dependencies and estimates; tickets state their own owner-decision defaults. |
| Loop setup and its limits | [LOOP.md](LOOP.md), [loop-constraints.md](loop-constraints.md) |
| Project subagents, origin and local changes | [.claude/agency-agents/README.md](.claude/agency-agents/README.md) |
| Ticket workflow and the step at which each role runs | [.claude/skills/implement-ticket/SKILL.md](.claude/skills/implement-ticket/SKILL.md), section "Agent roles" below |
| How a ticket goes from the queue to a ready pull request, who may do what | "Delivery workflow" below |
| UI and copy rules, design tokens | [docs/ui-quality.md](docs/ui-quality.md), [docs/design-tokens.md](docs/design-tokens.md) |
| Decisions the owner made, with dates | [docs/owner-decisions.md](docs/owner-decisions.md) |

The plan wins for product design; the epic and tickets win for order and scope. A ticket that changes a contract fixes the plan in the same pull request.

## Stack and constraints

- Python 3.11, **standard library only**, in the application and in the tests. No package download in any launch, fixture or test step.
- Linux is the supported platform (descriptor-relative, no-follow file opening).
- Serves bundled HTML, CSS and JavaScript and a small JSON API on `127.0.0.1`. No build step.
- One service per workspace, one worker, one active attempt.
- Generated fixtures only. Never point the program at real backups, volumes or devices.
- Creating backups, scheduling, live recovery, encrypted archives, links, permissions and cloud storage are outside the first release.
- A runtime version change, a dependency, an external request or a non-loopback listener needs the owner's approval first, not a pull request.

## Commands

Python 3.11 or newer (3.11 and 3.13 in CI). No install step is needed. The last two commands need Linux.

| Purpose | Command | Status |
|---|---|---|
| Tests | `python -m unittest discover -s tests` | planned: real with the scaffold |
| Help and version | `python -m restore_verifier --help` | planned: real with the scaffold |
| Create the demo workspace | `python3 -m restore_verifier --workspace .restore-verifier init-demo` | planned: #2 |
| Run the app | `python3 -m restore_verifier --workspace .restore-verifier serve` | planned: #2 |

## Architecture boundaries

The planned module map is in [docs/architecture.md](docs/architecture.md). Invariants every change must keep (the plan is the source):

- Inventory, restore, comparison, jobs, storage and rendering stay separate. The comparison reads the restored bytes again and never reuses the copy's own hashes.
- The browser selects staged input IDs only. A request never carries a host path or a destination, and no path is built from an HTTP value.
- Sources are walked and opened relative to an open root descriptor with no-follow flags, and the type of every opened descriptor is checked. Links and special files are rejected. A source that changes during a run gives an input-change error, not a comparison.
- The path profile of the plan (characters, segment and total length, depth, case-insensitive collisions, file and directory collisions) is enforced for folders and ZIP members alike.
- ZIP members are opened one by one and streamed; only stored and deflated, unencrypted members are accepted. Byte limits are enforced while reading, and the streamed length must equal the accepted declaration. `extractall` is never used.
- Output goes only into a new attempt directory. A rejected preflight creates no output tree. Reference, backup and earlier attempts are never written.
- Manifests are canonical UTF-8 JSON with fixed keys, compact separators, no BOM and one final LF; paths sort by ASCII bytes; the manifest ID hashes those bytes only.
- Every path has exactly one of `matched`, `changed`, `missing`, `unexpected`. Expected = matched + changed + missing, observed = matched + changed + unexpected. Read errors fail the attempt and never look like missing files.
- `verified` needs a completed run with every expected path matched and nothing else; any difference is `differences_found`. An empty restore is labelled as such.
- Counts, rows and outcome commit in one transaction; no database lock is held while files are copied. A crash before that commit leaves no completed outcome.
- One active attempt. The same request ID with the same inputs returns the same attempt, with other inputs a conflict. After a restart unfinished attempts are interrupted, and a retry is a new attempt that names the old one.
- Limits: 1,000 files, 2,000 entries, 32 MiB per file, 256 MiB in total, 128 MiB per ZIP and 1 GiB of retained attempts, checked before copying and while copying. Nothing is cleaned up automatically.
- The server binds `127.0.0.1`, caps JSON bodies, sends no CORS headers and rejects writes without the expected loopback origin.
- Labels and paths are rendered as text. Tables have headers, transitions are announced, status is text as well as colour, and everything works by keyboard.
- The product never claims more than it measured: bytes of one rehearsal against one reference, no guarantee about a production recovery.

## Git workflow

- `main` is the default branch. Work on one branch per ticket: `<issue-number>-<short-slug>`. Never commit to `main`.
- Small commits with imperative subjects and a type prefix (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Order for every ticket: local evidence, Code Reviewer, Reality Checker, then a draft pull request that says `Part of epic #1` and `Closes #<ticket>`, then CI on that draft, then `gh pr ready` only when CI is green.
- Do not push or open a pull request unless the owner asked in the current session; starting `/next-ticket` is that request for one ticket. Only the owner merges and releases. Do not push to `main`, force-push, or merge your own pull request.
- Never commit a rehearsal workspace (`.restore-verifier/`), `.env*`, or build output.
- Do not change `.claude/agents/`, `LOOP.md`, `loop-constraints.md` or `loop-budget.md` as part of a feature ticket.
- Open owner decisions on a ticket are settled with the ticket's stated default. Where a ticket states none, take the conservative option and say so in the pull request.

## Evidence before a ticket is called done

Paste real output into the pull request; never summarise a run you did not make.

1. For each acceptance criterion of the issue: the name of the test that proves it, or the exact step and what was observed.
2. The full output of `python -m unittest discover -s tests` locally with the number of skipped tests, and the link to the green CI run on the draft pull request (Linux with no skips, Windows with the listed skips).
3. For a restore or comparison change: the fixture (F1 to F5), the direct read of the restored bytes and the digest computed without the application.
4. For a job change: the fault point, the state after restart and the state of earlier attempts.
5. For a UI change: the Chrome version, the steps and what was observed, and that the page made no external request.
6. `git status` shows no stray files, and no dependency, external URL or non-loopback listener was added.
7. Anything not verified, said plainly.

## Agent roles

Project subagents are in `.claude/agents/`: nine Agency Agents roles and `loop-verifier`, which belongs to the Loop setup. Each Agency Agents role file starts with a section "In this repository", written for this project. That section and this file override the generic text below it. Sources, licence, local changes and the name collision with a user-level install are in [.claude/agency-agents/README.md](.claude/agency-agents/README.md).

When asked to implement, continue or finish a GitHub issue, follow the playbook [`.claude/skills/implement-ticket/SKILL.md`](.claude/skills/implement-ticket/SKILL.md). Claude Code loads it on its own for ticket work; `/implement-ticket <issue number>` starts it by hand. Delegate to the roles without waiting to be asked: each role's `description` ends with a "Use proactively ..." sentence, which is what makes Claude Code delegate. The playbook gives the exact trigger of each role.

| When | Roles | Access |
|---|---|---|
| Before coding | Software Architect | `Read, Grep, Glob` |
| While coding | Backend Architect, Database Reliability Engineer, Frontend Developer | can edit |
| After coding, when the trigger matches | Application Security Engineer, Accessibility Auditor | `Read, Grep, Glob` |
| After coding, when the trigger matches | API Tester | can edit |
| Gate on every ticket | Code Reviewer on the full diff, until no material finding is left | `Read, Grep, Glob` |
| Acceptance gate on every ticket, after Code Reviewer | Reality Checker on each acceptance criterion and the recorded evidence, and that CI is configured to run the checks (no CI result is needed yet) | `Read, Grep, Glob` |

- The two gates run on every ticket, whatever its size. A ticket is not called done before both have passed.
- Roles limited to `Read, Grep, Glob` cannot run commands. Give them the diff, the acceptance criteria and whatever command output exists.
- The session or role that wrote a change does not count as its reviewer.
- If a role is missing or cannot be delegated to, the session does the before-coding, while-coding and specialist steps itself and says so. It cannot pass the two gates on its own change: do not push or open the pull request. Stop, report that the gates could not run, and leave the run for the owner. This overrides the playbook's sentence "do that step yourself" for the two gates.
- In the pull request description, list under "Agent roles run" each role that ran, what it was asked and its verdict, and any step done without a role.

## Delivery workflow

How a ticket reaches the owner. Each piece is described in its own file; this part only links them.

- **Start:** the owner runs `/next-ticket` ([`.claude/skills/next-ticket/SKILL.md`](.claude/skills/next-ticket/SKILL.md)); it picks one leaf ticket (never a `tracking` parent or a ticket with open sub-issues; the last sub-issue's pull request also closes the parent), creates the branch and worktree, and runs the playbook [`.claude/skills/implement-ticket/SKILL.md`](.claude/skills/implement-ticket/SKILL.md). Nothing is scheduled.
- **Gate hook:** [`.claude/hooks/role_gate.py`](.claude/hooks/role_gate.py) blocks `gh pr create` and `gh pr ready` until Code Reviewer and Reality Checker ran after the last code edit. `ROLE_GATE=off` in the environment Claude Code is started from switches it off for that session; only the owner does that.
- **Permissions:** [`.claude/settings.json`](.claude/settings.json). Agent configuration edits ask in the main checkout and in ticket worktrees; CI, `CLAUDE.md`, `AGENTS.md` and Loop-file edits ask only in the main checkout; in a ticket worktree they are limited by the playbook's scope rule and reviewed by the owner at merge (shell-made edits are not covered, so a ticket never changes agent configuration); force pushes, pushes to `main`, `gh pr merge`, releases and reads of `.env` are denied.
- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Every job must be green on the current diff before a pull request is marked ready. The agent does not poll: it ends its turn with "Draft pull request #N is waiting for CI" and reads `gh pr checks` once when woken. Reviewers read the diff and evidence from `.claude/state/review/`. An acceptance step that needs a person is listed under "Owner checks" in the pull request.
- **Pull request:** [`.github/pull_request_template.md`](.github/pull_request_template.md). Tickets use [`.github/ISSUE_TEMPLATE/implementation-ticket.md`](.github/ISSUE_TEMPLATE/implementation-ticket.md).
- **Labels:** `status:ready`, `status:blocked`, `status:in-progress`, `needs-decision`, `tracking` (parent container, never worked; its sub-issues are the work items).
- **Changelog:** every ticket pull request adds one line under Unreleased in [CHANGELOG.md](CHANGELOG.md).
- **UI and copy:** [docs/ui-quality.md](docs/ui-quality.md); the `ui-ux-pro-max` and `unslop` skills are in `.claude/skills/`. Colours come from the shared design tokens in `restore_verifier/static/tokens.css` ([docs/design-tokens.md](docs/design-tokens.md)); new UI adds no colour literals.
- **Decisions:** [docs/owner-decisions.md](docs/owner-decisions.md). Security reports: [SECURITY.md](SECURITY.md).
- **Merge and release:** only the owner merges and releases ([docs/RELEASING.md](docs/RELEASING.md)). An agent stops at a ready pull request.

## Loop

Issue triage runs at L1: report-only, started by hand, no scheduler, no GitHub writes. See [LOOP.md](LOOP.md).
