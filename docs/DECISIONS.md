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
- **SUPERSEDED BY D-026.**

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
- **SUPERSEDED BY D-027.**

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
- **REFINED BY D-025.** The log-currency check named here moved out of the pre-commit
  gate and into the session-open census. The other three checks are unchanged.

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
- **REFINED BY D-023.** Session-close log commits are a second, standing exception.
  This entry's claim of "exactly one" was true when written and is no longer.

## D-022 - `git` and `gh` output goes to an artefact, never to the terminal

- **Context:** `CLAUDE.md` Section 4 routed a command through `Invoke-Logged.ps1` only
  when Claude needed the output. Git and gh were therefore run bare, and the first
  commit sequence in session 003 put status listings, push progress and commit
  summaries straight into the terminal - the noisiest output in the project, in the
  one place nobody reads carefully.
- **Decision:** Every `git` and `gh` command is wrapped in `Invoke-Logged.ps1`,
  whether or not Claude needs the output. The console keeps its two-line contract:
  a verdict and an artefact path.
- **Rejected:** Wrapping only the verbose commands and leaving quiet ones such as
  `git switch` bare. That is an exception list, and an exception list is a second rule
  that drifts out of sync with the first - the same argument that removed the
  PowerShell carve-out in D-012 and the per-read encoding flag in D-018.
- **Consequence:** The terminal stays legible, and every git operation leaves a dated
  artefact showing exactly what was run and what it returned. That record is evidence
  for the DevOps workflow section of the report, which the terminal scrollback was
  never going to be.

## D-023 - Session-close log commits go straight to `develop`

- **Context:** D-009 routes every change through an issue, a branch and a pull request
  with a self-review. D-021 named the root commit as the single exception. Applying
  the rule literally to a session close means roughly seven extra commands to land a
  `SESSION_LOG` block, reviewed by the person who wrote it minutes earlier.
- **Decision:** The session-close commit - `docs/SESSION_LOG.md` alone, plus any
  document amended in the same session - commits directly to `develop` with a `docs:`
  subject. Every other change follows D-009 without exception.
- **Rejected:** A pull request per session close. It produces a review artefact with
  no reviewer and no finding, on a project whose scope fence exists to keep process
  from outgrowing the deadline. Also rejected: leaving the exception unwritten and
  simply doing it, which is how a documented process quietly stops matching the
  history.
- **Consequence:** A session closes in three commands rather than ten. The cost is
  that the log block reaches `develop` unreviewed - acceptable, because it is a record
  of what happened rather than a change to how the system behaves, and because the
  next session's Section 0.5 reconciles it against the repository anyway.

## D-024 - `gh` issue and PR bodies use `--body-file`, like commit messages

- **Context:** D-020 routes commit messages through a file because PowerShell 5.1
  mangles embedded quotes and newlines in `-m`. A `gh issue create` or `gh pr create`
  body is the same shape of text with the same quoting problem, and it is read by an
  assessor rather than by a machine.
- **Decision:** Bodies are written to `dev_reports\issue_body.txt` through the
  Filesystem connector, passed with `--body-file`, and deleted afterwards. Same
  mechanism, same gitignored location, same clean-up as D-020.
- **Rejected:** Inline `--body` with escaped newlines, which is unreadable before it
  is used and unreviewable after; and a heredoc, which PowerShell 5.1 handles but
  cannot be handed over as a single-command block.
- **Consequence:** Issue and pull-request text can be read on disk before it reaches
  GitHub, where it becomes part of the assessed Git deliverable. The cost is one
  extra file write and one deletion per issue or PR.

## D-025 - Log currency is checked at session open, not before every commit

- **Context:** D-015 put a log-currency check in `tools\Check-Docs.ps1`, comparing the
  newest date written inside `SESSION_LOG.md` against git's committer date. It failed
  for the first time on 2026-09-08 and it failed twice over. Session 004's block is
  headed 22:35 and the commit carrying it was made at 00:05 - the block's date is
  typed by hand, the commit's is not, and the ninety minutes between them crossed
  midnight, so a log that described the newest commit exactly was reported one day
  stale. Underneath that sat a worse problem: the block describing a session cannot
  be written until that session closes (Section 1.4), so every second commit of every
  session would have tripped the same gate. The rule that a STALE verdict is fixed
  before committing and the rule that the log is written at close cannot both hold.
- **Decision:** The check moves to `tools\Session-Open.ps1` and is measured in
  commits rather than dates. The newest block names the commit its session left
  behind; HEAD should be that commit or the close commit one above it, per
  `docs/HANDOVER.md` Section 1.3. Two or more ahead means work exists that no block
  describes. `Check-Docs.ps1` keeps version drift, the document map and decision
  references as its pre-commit gate.
- **Rejected:** A one-day tolerance on the date comparison. It would have cleared the
  midnight case and left the mid-session case to fire the following day - a snooze
  rather than a fix, and the second false positive would have arrived with the gate's
  credibility already spent. Also rejected: writing a log block mid-session to satisfy
  the gate, which would make the log a record of what was needed to pass a check.
- **Consequence:** The question is asked where it is answerable, against the same
  evidence Section 0.5 already asks a human to check by eye, and the census now
  reports a LOG VERDICT beside its TREE VERDICT. The check no longer runs before
  every commit, so a session that ends without logging is caught at the next session
  open rather than at its own next commit - which is the same moment in practice,
  because the failure it detects can only be created by a session that has already
  ended.

## D-026 - Route B: deploy to a managed container service, not local Docker

- **Context:** The assignment allows Docker or a cloud platform. D-008 chose Docker on
  the reasoning that a cloud account was setup and billing for no additional marks.
  Since then the only machine that could run Docker has been left unbootable twice by
  Docker Desktop itself, and the corporate machine that replaced it must not have
  Docker Desktop, WSL or any hypervisor component installed. Local Docker is therefore
  not a route that exists any more, not merely one that is inconvenient.
- **Decision:** Deploy to a managed container service returning a real HTTPS URL.
  Cloud Run is the provisional pick on cost and speed; Azure is worth weighing if MSU
  credit exists. The image defined by commit 4d1b1cb becomes the build artefact rather
  than the deployment itself, so that work carries forward instead of being discarded.
- **Rejected:** Staying with D-008. It now depends on a capability this project no
  longer has, and acquiring it means putting Docker Desktop on a corporate machine that
  also carries TaCRAS - risking a second dead machine to satisfy a wording choice.
- **Consequence:** A live public URL moves from optional stretch to commitment, which
  is stronger evidence for the deployment deliverable than a local run recorded on
  camera. REQ-N-003's wording still describes a single `docker compose up` and needs
  revisiting, since the assessed start command is no longer the local one.

## D-027 - The repository folder is renamed to `qvs`

- **Context:** D-013 kept the spaced folder name on the reasoning that renaming would
  cost a connector reconfiguration and a Claude Desktop restart mid-build, for friction
  the tooling design already removed. The laptop holding that checkout is gone. Session
  008 cloned fresh onto the corporate machine and had to configure the connector from
  nothing regardless, so the cost D-013 was avoiding had already been paid.
- **Decision:** The repository root is `C:\Users\tmachimbira\Projects\Development\qvs`,
  a sibling of the `tacras` checkout, with no spaces in the path.
- **Rejected:** Recreating the spaced name on the new machine for continuity. It would
  have preserved a path that only ever existed to avoid a rename that has now happened
  anyway, and it keeps spaces in a path that reaches PowerShell arguments, build
  contexts and coverage output.
- **Consequence:** No script changed. Every tool derives the repository root from
  `$PSScriptRoot` and `config/settings.py` derives `BASE_DIR` from its own location,
  which is exactly the property D-013 was written to protect - so the rename cost
  nothing beyond the connector entry. `config/settings.py` still cites D-013 for that
  reasoning and the citation stays valid; a superseded decision is not a wrong one.

## D-028 - The Docker branch merges on CI evidence, not on a local container run

- **Context:** Session 006 deliberately held the pull request for
  `feature/REQ-N-003-docker-deployment` because no container had ever been built and a
  PR body would have had to describe a deployment nobody had run. Under D-026 no
  container will ever run on this machine either, so holding the PR for a local run is
  waiting for something that cannot now happen.
- **Decision:** The merge gate becomes CI evidence: a workflow job that builds the
  image and starts the container on the runner, with the run log cited in the PR body
  and copied into `docs/evidence/`.
- **Rejected:** Merging 4d1b1cb on nothing, on the grounds that the gate has become
  impossible. The gate's purpose was never the locality of the run; it was that the
  claim in the PR body be true.
- **Consequence:** Commit 4d1b1cb is five files written from reasoning and executed
  nowhere, on any machine, and it is the largest untested assumption in the repository.
  The first CI build may well fail. That is the point of the gate, and a green suite on
  `develop` is not evidence about it.

## D-029 - `issued_at` is inside the signed payload

- **Context:** REQ-F-002 signs a record's canonical fields at issue. `issued_at` is the
  timestamp of issue itself, and the obvious Django idiom for it, `auto_now_add`,
  assigns its value as the row is written - after any code in `save()` has run. A value
  that does not exist yet cannot be signed.
- **Decision:** `issued_at` is set explicitly with `timezone.now()` in
  `Qualification.save()`, immediately before the signature is computed, and it is one of
  the six fields `canonical_fields()` returns.
- **Rejected:** Signing the four substantive fields plus `certificate_id` and leaving
  `issued_at` outside the payload. It is simpler, and it leaves a backdated issue
  timestamp undetectable - in a system whose purpose is establishing that a credential
  is what it claims to be, a hole worth one line of code to close.
- **Consequence:** `save()` must be idempotent over the issued fields, or re-saving an
  altered record would re-sign it under its new contents and tampering would repair
  itself. Each assignment is therefore guarded, and
  `test_re_saving_does_not_re_sign_or_reissue` pins that behaviour.
  `test_backdating_the_issue_time_breaks_verification` is what this decision buys.

  A second consequence, and the one that needs a paragraph in the report: the signature
  covers `issued_at` to microsecond precision through `isoformat()`. That round-trips
  exactly on SQLite and on PostgreSQL, but a backend that truncated sub-second precision
  would silently invalidate every existing record. D-002 claims the SQLite to PostgreSQL
  move is a configuration change; that claim survives, but it is narrower than it looks.
- **Related, taken inline rather than registered:** normalisation lives on the model.
  `canonical_fields()` returns values already converted to strings, both temporal fields
  as ISO 8601, so `canonical_payload()`'s `default=str` is never reached in practice.
  The failure it avoids is a `date` at issue and a string read back from the database
  serialising to different bytes, which would make a valid record report as TAMPERED - a
  false accusation of forgery, and the worst error this system can make. Tightening
  `canonical_payload()` to reject non-strings outright is the stronger fix and remains
  open; it changes a module merged by PR #10 and its tests, so it needs its own branch.

## D-030 - The environment is loaded by an explicit script, not by `python-dotenv`

- **Context:** `.env` exists in the repository root with the three variables in it, and
  nothing reads it. `config/settings.py` reads `os.environ` directly and `python-dotenv`
  is in neither requirements file. The file is documentation shaped like configuration.
  In session 009 this cost two test runs: a new terminal inherited no variables and
  twelve tests failed on `ImproperlyConfigured`.
- **Decision:** A `tools\Set-Env.ps1` loads `.env` into the current PowerShell session.
  One command at the start of any new terminal.
- **Rejected:** Reading `.env` in `config/settings.py` via `python-dotenv`. It would
  remove the need to remember anything, which is its appeal, and it would also mean the
  container and the CI runner carry a dependency whose only job is to read a file that
  exists in neither. It makes the local case invisible rather than explicit, and a
  variable silently supplied from somewhere is harder to reason about than one that is
  missing loudly.
- **Consequence:** The failure mode does not disappear, it moves: a terminal where the
  script has not been run still fails, and still fails loudly, which is the behaviour
  D-003 wanted. `Set-Env.ps1` does not exist yet and is the first action of session 010.

## D-031 - `main` is protected by classic branch protection, with zero required approvals

- **Context:** REQ-N-001 states that no change reaches `main` without passing lint,
  security scan and the test suite. `ci.yml` has been that mechanism since D-007, but
  until this session `main` was unprotected: the pipeline ran, and nothing obliged
  anyone to heed it. The requirement had a pipeline and no gate. `qvs` is public and the
  account holds ADMIN, so classic branch protection and rulesets are both available at
  no cost - there is no plan constraint to document and no workaround to justify.
- **Decision:** Classic branch protection on `main`, applied by API from
  `dev_reports/branch_protection.json` rather than by hand in the web console, so what
  was requested is readable and re-appliable. Required status check
  `Lint, security and tests` bound to the GitHub Actions app id 15368, with `strict` set
  so a stale head must rebuild before merging; pull request required with
  `required_approving_review_count` at 0; `enforce_admins` on; force pushes and branch
  deletion off; conversation resolution required; linear history off.
- **Rejected:** Requiring one approving review, which is what a team of three to five
  would set and what the assignment's collaboration criteria imply. GitHub does not
  permit approving one's own pull request, so on a single-author repository that setting
  makes `main` permanently unmergeable. A gate that cannot be satisfied is not a stricter
  gate, it is a broken one.

  Rulesets were also rejected, and not on merit - they are the newer mechanism and
  arguably the better one. Branch protection renders as a single readable settings page,
  which is stronger evidence in a report and a viva than a ruleset's layered view.

  Linear history was rejected because a release merge from `develop` carries two parents
  and would be refused. The alternative, squashing `develop` into `main`, would collapse
  the branch history the assignment assesses.
- **Consequence:** The review gate on this project is the pipeline, not a person, and the
  report must say so rather than leave a reader to infer that human code review was
  enforced. This is the clearest instance in the repository of the gap between an
  assignment written for a team and a project executed by one author, and it belongs in
  the critical evaluation as exactly that.

  `enforce_admins` means the sole maintainer cannot push to `main` either; changes arrive
  by pull request or not at all. The protection settings themselves remain editable by an
  admin, so the position is strict but recoverable.

  REQ-N-001 does not move on protection alone. Protection is the mechanism; the evidence
  is a pull request from `develop` that merges to `main` through this gate, with the
  check reported against it. Until that merge exists the requirement stays OPEN.

  **Satisfied on 2026-09-11.** PR #14 merged `develop` into `main` through this gate,
  with the required check reported against it, and REQ-N-001 moved to VERIFIED in
  session 010. The paragraph above describes the position before that merge and is left
  standing rather than edited, because a decision that records what it was waiting for
  is more useful to the report than one that quietly reads as though it always held.
  Confirmed in session 012 against `gh pr view 14`, not inferred from commit subjects.

## D-032 - Audit events carry no foreign keys

- **Context:** REQ-F-007 records every verification attempt and REQ-F-008 requires
  those records to be append-only. The obvious model has a ForeignKey to
  `Qualification` and another to the user, which is what an audit table in most systems
  looks like.
- **Decision:** `AuditEvent` has no ForeignKey at all. The certificate ID is stored as
  the string that was submitted, and the actor as a username snapshot. REQ-F-011 will
  join on the string.
- **Rejected:** Nullable foreign keys. A NOT FOUND attempt has no qualification to
  point at, so the column would be null on exactly the events most worth auditing - the
  ones where somebody presented an identifier this system never issued. On the user
  side every `on_delete` option is wrong in a different way: CASCADE destroys audit
  history, SET_NULL rewrites an audit row and so contradicts REQ-F-008 inside the
  model's own definition, and PROTECT turns the audit trail into a reason an account
  cannot be closed.
- **Consequence:** The trail survives the deletion of anything it refers to, and it
  records what was presented rather than what it turned out to be - which is the
  question an audit answers. The cost is that a report joining events to records joins
  on a string rather than on a key, and that an event naming a deleted user cannot be
  resolved back to an account. Both are correct behaviour for an audit trail rather
  than limitations of one. This is the same argument
  `Qualification.canonical_fields()` already makes for keeping `issued_by` outside the
  signed payload.

## D-033 - Append-only is enforced in the application, not in the database

- **Context:** REQ-F-008 says no update or delete path exists. The strongest available
  mechanism is a database trigger that refuses UPDATE and DELETE on the table.
- **Decision:** Enforcement lives in Python. `AuditEvent.save()` raises
  `AppendOnlyError` when the row already has a primary key, `AuditEvent.delete()`
  always raises, and `AuditEventQuerySet` overrides `update()` and `delete()` to raise
  as well. The queryset override is the substantive half: `QuerySet.update()` writes
  SQL without ever calling `Model.save()`, so a guard on the model alone would leave
  `AuditEvent.objects.all().update(...)` working perfectly.
- **Rejected:** Database triggers. They would hold against raw SQL, which the Python
  guards cannot, and they would pin the schema to one backend in a way D-002's claim
  that the SQLite to PostgreSQL move is a configuration change does not survive. Also
  rejected: relying on `save()` alone, which is the version of this guarantee that
  looks complete and is not.
- **Consequence:** The guarantee holds against every path the application offers and
  against none outside it. A direct SQL UPDATE succeeds, and so would a data migration,
  because historical models in migrations receive a default manager rather than this
  one - Django only serialises managers marked `use_in_migrations`. That is stated in
  the technical report's critical evaluation rather than left for a reader to discover,
  because an application-level guarantee described as if it were a database one is the
  kind of claim that does not survive a viva question.

## D-034 - REQ-N-003 means one command to start, after one-time configuration

*Written in session 006 on `feature/REQ-N-003-docker-deployment` as D-026, and
renumbered here when that branch merged. `develop` had issued D-026 and D-027 to
different decisions in the meantime, so the branch's original numbers were already
taken. Nothing about the reasoning changed; only the label did. This is the one place
in the register where a number does not follow the session it was decided in, and it
is noted rather than smoothed over.*

- **Context:** REQ-N-002 forbids committing any secret. REQ-N-003 requires the system
  to start with no manual steps. The container runs with `QVS_DEBUG=0`, under which
  `config/settings.py` treats a missing `QVS_SECRET_KEY` as a start-up error by
  design. The two requirements cannot both be satisfied literally: the container needs
  a key it is forbidden to carry.
- **Decision:** `docker-compose.yml` reads `env_file: .env`, which is gitignored and
  excluded from the image build context. `.env` is generated once by
  `tools\New-DotEnv.ps1`, which produces both keys with `secrets.token_urlsafe(50)`
  and refuses to overwrite an existing file unless forced. REQ-N-003 therefore means
  one command to start, after one-time configuration.
- **Rejected:** Committing throwaway keys into `docker-compose.yml` to make the
  literal reading true. It would satisfy the wording of the weaker requirement by
  breaching the stronger one, and a committed key is the string that ends up in
  production - the same argument that kept a fallback out of `settings.py`. Also
  rejected: generating a key inside the entrypoint, which would produce a signing key
  that changes on every container start and so invalidates every signature already
  issued (D-003).
- **Consequence:** Configuration is a command rather than a paragraph, so it is done
  the same way every time. The cost is that a fresh clone cannot start the stack until
  `New-DotEnv.ps1` has been run once, and that this reading of REQ-N-003 is an
  interpretation rather than the requirement's literal text - which is why it is
  registered rather than assumed, and why it belongs in the report's critical
  evaluation as a case of two requirements in genuine tension.

  Under D-036 the same tension reappears one level up and is answered the same way:
  the platform generates both keys at first deploy and holds them, so the repository
  still carries no secret and the deployment still needs no manual key handling. The
  mechanism moved from a local script to a blueprint field; the argument did not move
  at all.

## D-035 - WhiteNoise serves static files, not a second container

*Written in session 006 as D-027 and renumbered on merge, for the reason given in
D-034.*

- **Context:** Django stops serving static files when `DEBUG` is off, and every
  deployed environment runs with `QVS_DEBUG=0`. Without something serving them, the
  Django admin renders with no stylesheet - which is what an assessor sees in the
  demonstration video, worth 15%.
- **Decision:** WhiteNoise, added to `requirements.txt` with no platform marker and
  wired in directly below `SecurityMiddleware`. `STORAGES` uses
  `CompressedStaticFilesStorage`, deliberately not the manifest variant: the manifest
  backend raises at render time for any `{% static %}` reference it cannot find, which
  would make the test suite depend on `collectstatic` having run first.
- **Rejected:** An nginx sidecar container. It is the correct answer for a production
  deployment and the wrong one here - it doubles the compose file, adds a service to
  explain on camera, and buys far-future cache headers for a demonstration dataset on
  a free instance that sleeps when idle. Also rejected: leaving the admin unstyled and
  calling it scoped-out under the `CLAUDE.md` Section 8 fence. That fence excludes
  styled UI of our own; it does not excuse a framework's own interface arriving
  broken.
- **Consequence:** One dependency and two settings changes, and the deployment serves
  a complete admin. The trade against nginx is a sentence in the report's critical
  evaluation. One visible cost locally: WhiteNoise warns `No directory at:
  staticfiles\` on any run where `collectstatic` has not been run, which includes the
  test suite and CI. Harmless - the entrypoint collects before gunicorn starts - but
  it is a warning that will be seen and should not be mistaken for a defect.

## D-036 - Render is the deployment platform

- **Context:** D-026 committed to a managed container service and named Cloud Run as a
  provisional pick, leaving the actual platform undecided. Six sessions later nothing
  was deployed anywhere, and the deliverables that depend on a running system - the
  demonstration video at 15%, and the deployment half of the working-software mark -
  were all blocked behind that open question.
- **Decision:** Render, free instance, Docker runtime, built from the existing
  `Dockerfile` and declared in `render.yaml`. Deploys from `main` with `autoDeploy`,
  so the gate that protects `main` (D-031) is also the gate on what reaches the public
  URL. Both keys are generated by the platform at first deploy.
- **Rejected:** Cloud Run, Azure, Railway and Fly.io. Cloud Run and Azure both sit
  behind a billing account and a card, which is days of friction for a demonstration
  system; Railway's free tier ended in 2023 and its trial credit expires; Fly.io no
  longer offers a free tier to new accounts. Render was the only candidate that puts a
  live HTTPS URL in front of an assessor with no card and no expiry. Also rejected:
  configuring the service by hand in the platform's console, which would leave the
  deployment unreviewable, undiffable and unreproducible - the same argument D-007
  makes for keeping the pipeline definition in the repository.
- **Consequence:** REQ-N-003's wording changes. It described a single
  `docker compose up`; the assessed start command is now a deployment that happens on
  merge to `main`, and the requirement is reworded in `docs/REQUIREMENTS.md` to name
  the public URL. `docker-compose.yml` stays in the repository - it is real,
  reviewable containerisation work and it still runs anywhere Docker exists, just not
  on this machine.

  Three properties of the free instance are limitations rather than defects, and each
  belongs in the report rather than being discovered by an assessor. The disk is
  ephemeral, so records registered through the live site do not survive a restart or a
  redeployment - the system demonstrates correctly within a session and resets between
  them. The instance sleeps after fifteen minutes idle and the next request waits
  thirty to sixty seconds for it to wake, so the URL must be warmed before it is shown
  on camera. And 512 MB is the whole memory allowance, which is why `WEB_CONCURRENCY`
  is set to 2 rather than the Dockerfile's local default of 3.

  Three code changes follow from deploying behind a TLS-terminating proxy, and all
  three would have failed silently. The exec-form `CMD` could not expand `${PORT}`, so
  the container would have listened on the wrong port and never received traffic;
  `SECURE_PROXY_SSL_HEADER` is required or the CSRF middleware rejects every POST the
  system has; and `ALLOWED_HOSTS` needs the platform's own hostname, which
  `settings.py` now reads from `RENDER_EXTERNAL_HOSTNAME` rather than waiting for
  someone to type it into a dashboard. The first of these is verified by the `image`
  job added to `ci.yml` under D-028, which starts the container with `PORT` set to a
  non-default value and requests `/health/` from outside it. Reading the Dockerfile
  could not have established that; running it is the only thing that could.
