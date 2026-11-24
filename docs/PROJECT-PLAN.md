# Backup Restore Verifier

## Product requirements

**Problem.** A person maintaining a small project can produce a backup without knowing whether it still contains all the files they need. An archive opening successfully does not establish that its contents match a known version. The proposed audience is a freelancer or small project team running a recovery rehearsal with generated documents and media fixtures. This audience is a planning assumption.

**Outcome.** Select a saved reference manifest and a prepared backup, restore actual file bytes into a fresh rehearsal directory, and read a report showing which paths matched, changed, were missing, or appeared unexpectedly. Reopen the same result after restarting the app and download a machine-readable report locally. The original fixture directories remain untouched.

| ID | User need | Observable success |
| --- | --- | --- |
| R1 | Save a fixed reference for a known-good build or delivery | A reference preserves relative path, byte count and SHA-256 for every regular file and has a reproducible identity. |
| R2 | Rehearse recovery without replacing current work | The verifier reads a staged folder or supported ZIP and writes actual files only inside a new attempt directory. |
| R3 | Understand precisely what was recovered | Every distinct path has a category and a reason. Counts and byte totals reconcile against both inventories. |
| R4 | Understand failures and rerun deliberately | Interruption, cancellation, corrupted input and capacity errors stay visible. A retry creates its own attempt and links the previous one. |
| R5 | Inspect evidence after session restart | The saved outcome and JSON report agree with the data visible in the browser, and each verified result links to the reference and staged input used. |

**First usable slice.** On a fresh generated workspace, use the known-good sample and one folder copy. Save the reference, verify the actual restored files, read the result, and reopen it after restart. The rest of the epic adds supported ZIP rehearsal, mixed results, cancellation and restart recovery, and an export with independently checked totals.

**Release boundaries.** Offline single-user verification of prepared synthetic input, content and relative paths only. Leave backup creation, scheduling, external volumes and live recovery, password-protected archives, cloud services, links and file-permission replay for future work. A match measures the rehearsal's bytes against its selected reference. It provides no claim about the origin of that reference or about files edited after the reference was captured.

## Technical design

### Runtime and local inputs

Python 3.11 with `sqlite3`, `zipfile`, `zlib`, `hashlib` and standard-library HTTP support on Linux, with bundled HTML, CSS and JavaScript in Chrome. Bind the HTTP server to loopback. Preflight the interpreter, those imports, Chrome, local writable storage, and the Linux file-opening options used by the backend. No cloud dependency, build step or network package download is needed for the intended stack. Verify that the target workspace supplies these prerequisites before implementation.

The proposed entry points are `python3 -m restore_verifier --workspace .restore-verifier init-demo` and `python3 -m restore_verifier --workspace .restore-verifier serve`. Initialization seeds named reference and backup fixtures under an app-owned workspace with a marker. It refuses a populated or conflicting directory. The UI selects staged input IDs only. Fixture metadata and dashboard responses use display labels and logical paths. The server accepts neither a destination path nor a host filesystem path in a browser request. An optional later staging command can copy separately generated inputs into the same controlled area without changing the rehearsal contract.

### Inventory and manifest

- Each file row has a canonical relative path, nonnegative byte count and lowercase 64-character SHA-256. Hash raw bytes using incremental reads. Path ordering is ascending ASCII byte order.
- The baseline path profile admits ASCII letters, digits, underscores, hyphens, space and dot inside named segments. Every segment starts with a letter or digit, ends without a dot or space, and is at most 64 bytes. Use only forward slashes between segments, up to eight levels and 240 bytes overall. Reject empty or ambiguous names, repeated member names and file-directory collisions. Reject different spellings of the same case-insensitive path at every component, including shared directories. ZIP directory entries may represent parent folders, with one trailing slash used solely as a directory marker. Directory paths never become report rows.
- A version-one manifest contains the profile, hash algorithm and sorted file rows. Canonical UTF-8 JSON uses fixed keys, compact separators, no BOM and a single final LF. Hash only the manifest bytes for the manifest ID, excluding input label and clock time. Preserve immutable manifest content and an optional label in history. A zero-byte regular file has a normal hash and counts as a file.
- Admit regular files and directories under the controlled reference or backup root. Reject links, unsupported file types and roots outside the initialized workspace. Walk and open source components relative to an open root descriptor with Linux no-follow operations, checking final file types on opened descriptors. Detect changes in source inventory or file fingerprints during the rehearsal and record an input-change error instead of issuing a completed comparison. The fixture directory is used as a read-only staged dataset during a run.

[Python SHA-256 API](https://docs.python.org/3.11/library/hashlib.html#hashlib.sha256)

### Actual restore and comparison

1. Preflight the selected manifest, staged backup type, relative paths, file count and capacity. The initial workload limits are 1,000 files, 2,000 entries including directories, 32 MiB per file, 256 MiB total uncompressed bytes and 128 MiB per ZIP. Apply byte and entry limits to manifests and probes as well. Create no output tree for a rejected preflight.
2. Allocate a fresh attempt directory under app-managed storage. Write only regular files into its private staging tree. Open ZIP members explicitly and stream them with the same byte checks as folder inputs. Support stored and deflated unencrypted ZIP members and reject unsupported entry metadata before copying. Enforce the actual byte limits during reads, verify that streamed length equals the accepted entry declaration, and surface member-read or integrity errors. Stream into fresh temporary files within the private tree and publish each file after its copy completes. Reproduce the source bytes, leaving archive permissions and timestamps unapplied.
3. Close copy handles and compare the sealed destination independently. Enumerate and rehash the actual restored bytes, and join the sorted output inventory with the saved manifest on path. One path has one result. With two present rows, size and hash both equal means `matched`, otherwise `changed`. Expected only means `missing`, and restored only means `unexpected`. Read errors are attempt failures and do not masquerade as missing files. Record independently computed restored hashes and sizes.
4. Commit counts, ordered rows and completed outcome together in SQLite. With E expected files and O observed files, E equals matched plus changed plus missing, and O equals matched plus changed plus unexpected. The total report rows equal E plus unexpected. Sum expected and observed bytes separately. An outcome is `verified` only when it completed with all expected paths matched and zero changed, missing or unexpected files. A completed comparison with any difference is `differences_found`. An empty baseline can complete verified only when the restored inventory is also empty and the browser labels that result as an empty restore.

An attempt-level quota and a one-active-attempt rule keep the service bounded. Apply a default workspace cap of 1 GiB of retained attempt files and partial files, reserving available headroom before copying. If there is too little space, give a capacity error with the attempt history available. Version one retains attempts and provides no automatic cleanup or overwriting. A user can initialize a different clean rehearsal workspace explicitly.

[Python ZIP member API and supported methods](https://docs.python.org/3.11/library/zipfile.html)

### Persistence, recovery and the browser

| Record | Essential fields |
| --- | --- |
| Manifest | ID, canonical bytes, label and creation time |
| Staged input | ID, display label, kind, fixture revision and controlled location key |
| Attempt | ID, manifest ID, staged input ID and revision, retry parent, phase, terminal reason, compare result, progress and timestamps |
| Result row | Attempt ID, canonical path, state, expected size and hash or absent, restored size and hash or absent |

Use one local service instance per initialized workspace and one worker per service. A transaction starts at most one active attempt. The same request ID with the same inputs returns the original attempt, including after a completed response is lost. With different inputs it returns a conflict. A distinct request while busy receives the active attempt link. Save short progress updates separately from the final transaction and never hold a database write lock while copying files. A crash before final commit leaves no completed outcome even if files exist. After restart under the workspace lock, mark unfinished attempts interrupted and keep their partial output isolated. Cancellation is cooperative between bounded chunk reads and file steps. An already finalized result returns its terminal state. A retry explicitly starts from zero under a new attempt ID and does not alter the original attempt.

The browser offers a start screen, progress view, result table with category filters, and a run history. Confirm the selected manifest and staged backup labels before a start. Show the current phase and copied totals while the job runs. Announce major transitions in a live region, use semantic tables with headers and visible focus, and show text labels alongside status colors. Failed or interrupted attempts show their last phase, reason and retry action. Keep completed reports accessible on reload. Provide a local JSON export with manifest identity, source label and revision, outcome, summary counts and sorted rows. The canonical comparison portion is byte-identical on repeat runs with the same inputs. Job IDs and telemetry are separate history or envelope fields.

The proposed API exposes `GET /api/fixtures`, `POST /api/manifests`, `POST /api/attempts`, `GET /api/attempts`, `GET /api/attempts/{id}`, `POST /api/attempts/{id}/cancel` and `GET /api/attempts/{id}/report`. Use same-origin requests with capped JSON bodies and no CORS. Reject writes lacking the expected loopback origin. Validate identifiers against the local records before working with storage, and escape fixture labels and returned path strings in the browser.

## Original verification fixtures

These are specifications for generated fixtures. Hashes were computed independently with .NET SHA-256 on the listed bytes. Actual application and browser runs remain planned acceptance work. Text bytes are ASCII with LF and no final BOM.

| Reference path | Bytes | Size | SHA-256 |
| --- | --- | ---: | --- |
| `docs/empty.txt` | Empty | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `docs/readme.txt` | `first draft\n` | 12 | `a07219764af338a96455bf5ce10c5080e6ca79286196bfa9d60301adc19f9157` |
| `images/pixel.bin` | Hex `00 FF 10 80` | 4 | `a33bb2aed757bc839807d7a9deab0688c3cf06d36e53cb428f2e539c8dc76c5b` |
| `notes/checklist.txt` | `one\ntwo\n` | 8 | `c3f9c8c283a2b1f2f1896f27a01cbe3cddc0c9d93f752e4639035a0f5b36f6e8` |

| Fixture | Prepared input | Independent expected result |
| --- | --- | --- |
| F1 Good recovery | Same four files in a folder and in stored and deflated ZIPs, with differing enumeration orders | Four matched, zero other categories. Both inventories have 4 files and 24 bytes. Read the restored binary and empty file directly to prove real output. Manifests and canonical comparisons agree across repeated runs. |
| F2 Mixed recovery | Match both `docs/` reference files, change checklist to `one\nTWO\n` at the same length, omit the pixel file, add `docs/extra.txt` with `spare\n` | Two matched, one changed, one missing, one unexpected. Expected 4 files and 24 bytes. Observed 4 files and 26 bytes. The table has 5 rows and the outcome is `differences_found`. |
| F3 Unsupported input | Controlled fixture marked unsupported and a truncated copy of the known ZIP. Exercise an over-limit count through test-configured small limits. | Specific unsupported, read or capacity reason. No completed report and no side effects on any staged input. |
| F4 Interrupted copy | Test hook pauses after the first completed file. Exercise cancellation and abrupt process stop in separate attempts. | Cancellation stays cancelled. On restart the abrupt attempt becomes interrupted, with its files isolated. A clean retry creates a distinct verified attempt. |
| F5 Competing starts and stale UI | Submit a repeated request ID, a second distinct start during a held run and a replay with altered inputs. Refresh the browser while the held run continues. | One active attempt. Same request and inputs return it. Competing or altered requests have explicit conflicts. Refresh restores the live attempt view. |

For F2 the checklist digest is `ff4bebae5b918eeae9ad25e99951e0690c77d3a8764edf8f805c31f32d904753` and the new file digest is `b57324e8dac8839489c4f3ceebdf6fbce21bb0bc1f8b388f627d6b9fde4b6f10`. The planned integration oracle reads the restored directory directly and compares it with independently recorded fixture bytes and expectations. It does not derive its expected rows from the app report.

## Epic · Verify a synthetic backup through an actual isolated restore

Deliver a local rehearsal that restores folders and supported ZIPs, checks their bytes against a saved reference, and preserves a repeatable report and meaningful recovery history. It is complete when the fixture checks, clean offline Chrome run and restart behavior pass with recorded observations. The six tickets total **12–19 hours of hands-on implementation and verification**, with four integration milestones described below.

| Milestone | Tickets | Integration gate |
| --- | --- | --- |
| Define contracts and accept fixtures | BR-01 | Controlled workspace, staged IDs, start screen and typed source and report contracts. |
| Run the first usable rehearsal | BR-02, BR-03, BR-04 | Manifest and restore adapters can be developed in parallel after the contract. The first folder backup restores and compares end to end, and then ZIP and mixed fixtures use the same compare flow. |
| Verify recovery behavior | BR-05 | Check explicit cancellation, restart, conflict and rerun against preserved attempts. |
| Record the offline release walkthrough | BR-06 | Clean launch, recorded Chrome and test results, and report consistency. |

| Requirement | Primary acceptance evidence |
| --- | --- |
| R1 | BR-02-A, BR-02-B and BR-02-C |
| R2 | BR-01-B, BR-03-A, BR-03-B and BR-03-C |
| R3 | BR-04-A and BR-06-B |
| R4 | BR-05-A, BR-05-B and BR-05-C |
| R5 | BR-04-B, BR-04-C and BR-06-C |

### BR-01 · Set up the local rehearsal and fixture contracts

**Story** As a maintainer, I can select a prepared reference and backup in a local workspace without sharing real backups.

**Estimate** 2–3 hours. **Dependencies** None.

- BR-01-A. A fresh init creates the controlled workspace and the generated fixtures F1–F3 using the byte contract. A second init on the same path reports a conflict and changes no fixture hash.
- BR-01-B. The keyboard can select two prepared IDs and display the option summary in Chrome from a loopback server. Arbitrary browser-supplied paths fail validation.
- BR-01-C. Freeze the manifest, staged input, attempt state and comparison row contracts in a documented fixture. Capture actual preflight commands and observed versions.

### BR-02 · Capture a deterministic reference manifest

**Story** As a maintainer, I can save a reference and compare later backups against the exact same file inventory.

**Estimate** 2–3 hours. **Dependencies** BR-01.

- BR-02-A. F1 manifests contain exactly the four expected rows, all fixture sizes and all independently computed hashes in canonical path order.
- BR-02-B. Two scans of identical inputs preserve manifest bytes and ID despite enumeration order. Editing a same-length byte changes the manifest ID. Zero-byte files remain explicit.
- BR-02-C. Unsupported paths and file types produce specific errors, with no manifest saved. Use a separately computed digest or direct file read for corroboration.

### BR-03 · Restore folders and ZIPs with bounded output

**Story** As a maintainer, I can rehearse a backup in fresh storage without replacing the source.

**Estimate** 3–4 hours. **Dependencies** BR-01.

- BR-03-A. A folder restore writes the F1 bytes into a fresh private directory. Stored and deflated ZIP adapters achieve the same result. A second run uses a different attempt directory.
- BR-03-B. Verify the restored bytes by reading output files directly. Verify that reference and backup trees retain their original content and that the adapter writes only to its attempt directory.
- BR-03-C. F3 rejects unsupported inputs and limit violations with distinct errors. An incomplete copy is marked partial and cannot serve as completed verification.

### BR-04 · Reconcile recovered bytes and show a saved report

**Story** As a maintainer, I can read precisely what matched the reference and investigate each difference.

**Estimate** 2–3 hours. **Dependencies** BR-02 and BR-03.

- BR-04-A. The comparison re-reads the isolated output. F1 has four matches and `verified`. F2 contains the five expected rows with counts, byte totals and `differences_found` from the fixture table.
- BR-04-B. The keyboard can inspect a filtered result and recorded reason. The user can reopen a completed attempt and locally download JSON that matches the comparison screen.
- BR-04-C. Compare exports for repeat F1 runs after removing attempt metadata. Match their canonical payloads exactly.

### BR-05 · Handle cancel, restart, retry and competing requests

**Story** As a maintainer, I can recover from interrupted work and know which attempts are safe to interpret.

**Estimate** 2–4 hours. **Dependencies** BR-04.

- BR-05-A. F4 cancellation and restart preserve the expected terminal states, with partial files distinguishable and no completed reports. The clean retry verifies and links its predecessor.
- BR-05-B. F5 demonstrates one active attempt, stable same-input retry behavior, conflict for mismatched or competing launches, and continued progress after reload.
- BR-05-C. Simulate output capacity exhaustion with a small test quota. History remains available, prior reports remain intact, and the current run has an explicit capacity reason.

### BR-06 · Prove the workflow from a clean offline workspace

**Story** As a maintainer, I can run and verify the rehearsal from the documented steps.

**Estimate** 1–2 hours. **Dependencies** BR-05.

- BR-06-A. In a fresh Linux workspace, run the fixtures and one complete Chrome flow with no external connectivity. The UI loads its assets and API calls through loopback, and both expected outcomes are inspectable.
- BR-06-B. Run the independent expected-row, byte and digest checks, including equal-length change detection and byte totals. Record commands, environment, and observed pass or fail results.
- BR-06-C. Verify keyboard navigation, progress announcements and completed report reopening after restart. Document accepted formats and limits and preserve the distinction between output evidence and a production recovery guarantee.
