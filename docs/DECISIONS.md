# QVS Decisions Register

Numbered, never renumbered, never deleted. A superseded decision is marked
`SUPERSEDED BY D-nnn` and left in place, because the report's *Critical evaluation*
section is worth more when it can show a position that changed and why.

Format is four lines: **Context**, **Decision**, **Rejected**, **Consequence**.
Four lines is a complete entry - this is a six-week project, not a documentation
exercise.

This file is the source for the *Design decisions* section of the technical report
(25% of the module marks). Every entry here is a paragraph you will not have to write
from memory in Sprint D.

---

## D-001 - Django 5.2 as the web framework

- **Context:** Short deadline; the developer has production Django experience.
- **Decision:** Build on Django 5.2 with server-rendered templates.
- **Rejected:** FastAPI and Flask. Both would have meant writing auth, forms, CSRF
  protection and an admin surface by hand.
- **Consequence:** Auth, ORM, admin, forms, CSRF and a test client arrive built in.
  Each is a requirement not implemented.

## D-002 - SQLite as the database

- **Context:** The system holds a demonstration dataset, not production volume.
- **Decision:** SQLite, with `DATABASES` read from an environment variable.
- **Rejected:** PostgreSQL and MySQL - either adds a service to run in CI and in
  Docker, for no assessed benefit.
- **Consequence:** No database service anywhere. Migration to PostgreSQL is a
  configuration change, and describing that in the report is worth more than doing it.

## D-003 - HMAC-SHA256 signatures for authenticity

- **Context:** REQ-F-002 and REQ-F-006 require tamper-evident credentials.
- **Decision:** Sign a canonical ordering of each record's fields with HMAC-SHA256,
  keyed from `QVS_SIGNING_KEY` held in the environment.
- **Rejected:** Blockchain-based verification. Disproportionate to the problem and
  unfinishable in the time available.
- **Consequence:** Real tamper detection in roughly thirty lines, no external
  dependency, and an argued rejection of blockchain that scores better in the
  critical evaluation than a half-built chain would.

## D-004 - pytest with pytest-django

- **Context:** The assignment assesses unit tests and integration tests separately.
- **Decision:** pytest, pytest-django and pytest-cov, with `unit` / `integration`
  markers and a `req` marker naming the requirement each test verifies.
- **Rejected:** Django's built-in test runner - no marker system, so the
  unit/integration split and the traceability matrix would both be manual.
- **Consequence:** One command produces the test result, the coverage report and the
  data for the requirements traceability matrix.

## D-005 - Ruff for lint and formatting

- **Context:** *Static code analysis* and *coding standards compliance* are both
  assessed.
- **Decision:** Ruff, configured in `pyproject.toml`.
- **Rejected:** flake8 plus isort plus black - three tools, three configs, three CI
  steps.
- **Consequence:** Two assessed criteria satisfied by one CI job.

## D-006 - Bandit for security static analysis

- **Context:** A security-specific analyser is a distinct quality gate the pipeline
  can point at.
- **Decision:** Bandit over the application packages, at medium severity and above.
- **Rejected:** Relying on Ruff's security rules alone - a weaker story in the report.
- **Consequence:** A separate, nameable security gate. Findings are either fixed or
  carry a `# nosec` with a written reason.

## D-007 - GitHub Actions for CI/CD

- **Context:** The assignment names GitHub Actions first among the acceptable tools.
- **Decision:** GitHub Actions, configuration committed at `.github/workflows/ci.yml`.
- **Rejected:** Jenkins (needs hosting), GitLab CI (needs a second platform).
- **Consequence:** The pipeline definition lives in the repository, so it is itself
  part of the assessed Git deliverable.

## D-008 - Docker as the deployment target

- **Context:** Deployment must be to Docker or a cloud platform.
- **Decision:** Docker, with `docker compose up` as the single start command.
- **Rejected:** AWS, Azure and GCP - account setup, billing and a network dependency
  for no additional marks.
- **Consequence:** REQ-N-003 is satisfiable and demonstrable on camera. A live public
  URL becomes an optional stretch rather than a commitment.

## D-009 - Pull-request workflow even when working alone

- **Context:** The Git deliverable is 20% and assesses branches, pull requests, code
  review and issue tracking.
- **Decision:** Every change goes through an issue, a branch and a PR into `develop`,
  with a self-review comment, regardless of team size.
- **Rejected:** Committing directly to a branch and reconstructing the history later -
  which cannot be done convincingly.
- **Consequence:** One extra command per unit of work, using `gh`. The 20% accrues as
  work happens rather than being chased at the end.

## D-010 - Python 3.12 everywhere

- **Context:** Local development, CI and the Docker image are three environments that
  can drift apart.
- **Decision:** Python 3.12 in all three. Confirmed 3.12.10 locally, and it is the
  only interpreter the Windows launcher has registered.
- **Rejected:** 3.13 locally with 3.11 in the container, mirroring the TaCRAS server.
  That server is irrelevant to this project.
- **Consequence:** A failure reproduces identically in all three places. Version drift
  is removed as a possible cause of any bug.

## D-011 - Virtual environment, addressed by explicit interpreter path

- **Context:** TaCRAS runs on system Python via `py manage.py`, which made "which
  interpreter am I on" a live question. This machine additionally carries the
  Microsoft Store `python.exe` alias stub, which prints an advertisement instead of
  running Python.
- **Decision:** `.venv` at the repository root, gitignored. Every Python invocation
  uses the explicit path `.\.venv\Scripts\python.exe`. `py` is used exactly once, to
  create the environment.
- **Rejected:** Shell activation - it depends on execution policy and on the shell
  remembering state, and it fails silently when forgotten.
- **Consequence:** The interpreter is unambiguous in every command, in every script
  and in every Claude Code prompt. The Store stub is unreachable by accident.

## D-012 - LF line endings everywhere, no exception

- **Context:** TaCRAS carries substantial CRLF normalisation debt from tooling that
  rewrites line endings inconsistently.
- **Decision:** `.gitattributes` sets `* text=auto eol=lf` with no PowerShell
  carve-out. `core.autocrlf` is set to `false` explicitly so the two mechanisms
  cannot disagree.
- **Rejected:** CRLF for `*.ps1`. PowerShell 5.1 reads LF scripts without complaint,
  so the exception buys nothing and creates a second rule to keep in sync.
- **Consequence:** The whole class of line-ending problems is absent rather than
  managed.

## D-013 - Repository folder keeps its spaced name

- **Context:** The repository sits at a path containing spaces
  (`...\Qualification Verification System`), and the Filesystem connector is already
  scoped to it.
- **Decision:** Keep it. All tooling derives the repository root from
  `$PSScriptRoot`, so the absolute path appears nowhere inside any script;
  `docker-compose.yml` will pin `name: qvs` so container naming stays clean.
- **Rejected:** Renaming to `qvs`. It would have required reconfiguring the connector
  and restarting Claude Desktop mid-build, for friction the tooling design already
  removes.
- **Consequence:** The path is typed once per terminal session and nowhere else.

## D-014 - Governance limited to three documents

- **Context:** The TaCRAS governance apparatus - decisions register, findings
  register, task register, workstream claims file, prediction scorecard, formal
  handover tokens - manages a large, long-lived, multi-account codebase.
- **Decision:** `CLAUDE.md`, `docs/HANDOVER.md` and `docs/SESSION_LOG.md`, plus this
  register and `docs/REQUIREMENTS.md` as content. No findings register, no claims
  file, no prediction scorecard.
- **Rejected:** Porting the TaCRAS model. On a six-week solo project the process
  would cost more than it protects.
- **Consequence:** Reasoning recorded in `docs/HANDOVER.md` Section 2, so a later session
  finds an argued absence rather than an apparent oversight.

## D-015 - Document staleness is checked by command, not by discipline

- **Context:** On TaCRAS, governance documents fell behind the repository and
  recovering a current position from a stale one proved expensive.
- **Decision:** `tools\Check-Docs.ps1` verifies tool versions and paths asserted in
  `CLAUDE.md` against the machine, verifies the document map both ways, and fails
  when commits exist that are newer than the newest `SESSION_LOG` block. It runs
  before every commit.
- **Rejected:** A periodic manual review pass. That is what failed before.
- **Consequence:** Staleness is caught within one commit of occurring, when it costs
  minutes, rather than at a review, when it costs a session.

## D-016 - Dependency ranges, not a lockfile

- **Context:** Reproducible builds across the local `.venv`, CI and the Docker image.
- **Decision:** `requirements.txt` and `requirements-dev.txt` use compatible-release
  ranges (`Django>=5.2,<5.3`). `gunicorn` carries a `sys_platform != "win32"` marker
  so one file serves Windows development and Linux containers alike.
- **Rejected:** pip-tools or uv with a committed lockfile. Correct for a long-lived
  service; on a six-week deliverable it adds a dependency-update workflow nobody has
  time to run.
- **Consequence:** Security patches flow in without intervention, at the cost of
  builds not being byte-identical across time. Acceptable here, and named in the
  report's critical evaluation rather than left implicit.

## D-017 - Claude writes the next session's opening prompt at close

- **Context:** A session ends holding context that exists nowhere else - what was
  half-finished and how far it got, which claim is unverified, what the single next
  action is. Sir Ton cannot reconstruct that from outside the session, and should not
  have to.
- **Decision:** Every session close produces the opening prompt for the next session,
  written by Claude, placed **both** in the `Opening prompt` field of the session log
  block (the durable, git-tracked copy) **and** directly in chat as a copy-pasteable
  block. Protocol in `docs/HANDOVER.md` Section 1.5.
- **Rejected:** Sir Ton writing the prompt himself, and a separate
  `NEXT_SESSION.md` file. The first discards context Claude holds and he does not;
  the second adds a document to the map for something the log already carries, and
  would be overwritten rather than accumulated - losing the record of how each
  session was handed on.
- **Consequence:** A session starts with one paste and is oriented before its first
  read. The prompts also accumulate in the log as evidence of the working method, which
  is material for both the DevOps workflow section of the report and the individual
  contribution report.

## D-018 - Repository text is ASCII only

- **Context:** PowerShell 5.1 decodes a UTF-8 file carrying no byte order mark as
  ANSI. Every non-ASCII character in a document or script therefore arrived corrupted
  in the first session-open census, and `tools\Check-Docs.ps1` reads five files
  without `-Encoding UTF8`, getting away with it only because everything it happens
  to pattern-match is ASCII. That is luck, not design.
- **Decision:** Repository text files contain ASCII only. "Section 3", not a section
  sign; a hyphen, not an em dash; straight quotes, not curly ones.
  `tools\Check-Ascii.ps1` enforces it read-only and treats a byte order mark as a
  failure. `tools\Fix-Encoding.ps1` performed the one-time conversion - 131
  characters across 6 files - with a dry-run mode and backups to
  `dev_reports\encoding_backup\`.
- **Rejected:** Adding `-Encoding UTF8` to every read. That handles the problem
  correctly in the places somebody remembered, which is precisely the failure mode
  D-015 exists to prevent. The ASCII rule removes the class instead: once the content
  is ASCII the bytes decode identically under either encoding. Same shape as D-012 on
  line endings - absent rather than managed.
- **Consequence:** Artefacts are legible, string comparisons cannot fail for
  invisible reasons, and the rule is checked by command rather than remembered. The
  cost is one guard in the local gate and in CI, where "coding standards compliance"
  is an assessed criterion anyway.

## D-019 - Claude Desktop is the default writer; Claude Code is for bulk and `gh`

- **Context:** `CLAUDE.md` Section 7 said Claude Code writes files into the repo. In
  session 002 Claude Desktop wrote three `tools\` scripts directly through the
  Filesystem connector because each needed line-by-line reasoning, and one of them
  carried a self-matching infinite loop that was caught precisely because the writing
  agent was the reasoning agent. Document and practice had diverged.
- **Decision:** Claude Desktop writes files directly through the connector by default.
  Claude Code is used for bulk or repetitive edits across many files, long command
  sequences, and `gh` operations. Whoever writes, Desktop reads the file back through
  the connector before the file counts as done.
- **Rejected:** Reverting to routing every file through Claude Code. The rule that
  Claude Code's report is not evidence is really an argument against the round trip;
  at the file counts this project works in, the round trip buys a translation step and
  a report to distrust, and nothing else.
- **Consequence:** Fewer agent hops per file and one less place for a file's content
  to change in transit. The cost is Desktop context spent on file bodies, which is
  affordable at this project's size and would not be on a large codebase - so this
  decision is scoped to QVS, not generalised.

## D-020 - Commit messages are written to a file, used with `-F`, then deleted

- **Context:** A Conventional Commit subject plus a body citing requirements is a
  multi-line message. PowerShell 5.1 has no `&&`, mangles embedded quotes and newlines
  in `-m`, and repeating `-m` per paragraph produces a message nobody can review
  before it is written to history. Commit messages are also assessed - the Git
  deliverable is 20% and names commit history explicitly.
- **Decision:** Claude writes the message to `dev_reports\commit_message.txt` through
  the Filesystem connector. The commit is made with
  `git commit -F dev_reports\commit_message.txt`. The file is then removed by an
  explicit `Remove-Item` command in the same sequence, every time.
- **Rejected:** `git commit -m` with escaped newlines, and an editor-based commit.
  The first is unreadable before it is used and unreviewable after; the second stops
  the sequence dead in a terminal editor and cannot be handed over as a command block.
- **Consequence:** The message is a file Sir Ton can read before it becomes history,
  and it lives under `dev_reports\`, which is gitignored - so a message file that
  survives a failed sequence still cannot be committed by accident. Deleting it
  removes the other failure mode: a stale message reused for the wrong commit.

## D-021 - The root commit lands directly on `main`, before branch protection

- **Context:** D-009 requires every change to travel through an issue, a branch and a
  pull request into `develop`. None of that machinery can exist yet: `main` is unborn,
  `develop` cannot be branched from a commit that does not exist, and GitHub cannot
  protect a branch with no ref.
- **Decision:** The Sprint A foundation lands as a single root commit on `main`.
  Immediately afterwards `develop` is branched from it and `main` is protected. Every
  change after this one follows D-009 without exception.
- **Rejected:** Leaving the deviation unrecorded. A history whose first commit
  visibly bypasses a registered decision, with nothing explaining why, reads as a
  process that was declared and then ignored - which is worse for the assessed Git
  deliverable than the deviation itself.
- **Consequence:** Exactly one commit in the repository's history sits outside the
  pull-request workflow, and it is the one that made the workflow possible. That
  sentence is the report's answer if anybody asks.
