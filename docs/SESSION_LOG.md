# QVS Session Log

The running record of every working session. Appended to, never rewritten. Newest
block last.

Protocol: `docs/HANDOVER.md` Section 1. Block shapes are `CLOSE` (same account continues)
and `ACCOUNT HANDOVER` (the other account picks up).

This file is tracked in git. Besides being the handover mechanism, it is the raw
material for the **Individual Contribution Report**, which is 15% of the module marks
and is written from exactly this kind of record. Write each block as though a marker
will read it, because in effect one will.

---

## Session 001 - CLOSE - AccountA - 2026-09-07 15:45

Sprint  : A (foundation)
Branch  : main
Context : Setup conducted from the TaCRAS Claude project environment, because the
          dedicated QVS project did not exist yet. The repository is now
          self-describing - `CLAUDE.md` and `docs/` carry everything a session needs -
          so work moves to the QVS project from session 002 and this log continues
          there unbroken.

Done    :
  - Machine audited from bare. Only VS Code 1.136.1 and winget were present.
  - Installed: Git 2.55.0.windows.3, Python 3.12.10 (the launcher registers 3.12 and
    nothing else), GitHub CLI 2.100.0, Docker Desktop 29.7.2, Claude Code 2.1.263.
  - Claude Code installed natively at `~\.local\bin\claude.exe`; that directory
    appended to the USER PATH only, reading User scope explicitly rather than writing
    the merged machine-plus-user path back into it.
  - Execution policy set to RemoteSigned at CurrentUser scope.
  - `gh auth login` completed as **Michael-Tonderai**
    (Tonderai M. Machimbira, tonderaimachimbira@gmail.com).
  - `git init -b main`; identity set at LOCAL scope; `core.autocrlf false`.
  - `.gitattributes` (LF everywhere) and `.gitignore` written. `git check-ignore`
    confirms `.gitignore:48` suppresses `dev_reports\` - verified BEFORE any commit
    exists, so artefacts cannot leak into the history.
  - `gh repo create qvs --public --source=. --remote=origin` executed. **UNVERIFIED**
    - it ran directly rather than through `Invoke-Logged.ps1`, so there is no
    artefact. Confirm from the REMOTES section of the next session-open census.
  - Tooling written: `Invoke-Logged.ps1`, `Bootstrap.ps1`, `Install-Toolchain.ps1`,
    `Add-LocalBinToPath.ps1`, `Session-Open.ps1`, `Setup-Repo.ps1`, `Setup-Venv.ps1`,
    `Check-Docs.ps1`.
  - Governance written: `CLAUDE.md` (incl. Section 10 staleness), `docs/HANDOVER.md`,
    `docs/DECISIONS.md` (D-001-D-016), `docs/REQUIREMENTS.md` (15 requirements,
    tiered, mapped to the assignment's four capabilities), this file.
  - `requirements.txt` and `requirements-dev.txt` written.
  - `Check-Docs.ps1` first run: **DOCUMENTS CURRENT**, 0 failures, 0 warnings.

HEAD    : (no commits yet)
Tree    : untracked - `.gitattributes`, `.gitignore`, `CLAUDE.md`, `docs/`, `tools/`,
          `requirements.txt`, `requirements-dev.txt`
Issues  : none opened yet

Decided :
  - D-010 Python 3.12 everywhere. D-011 `.venv` with explicit interpreter path.
    D-012 LF line endings, no exception. D-013 spaced folder name kept, tooling
    derives root from `$PSScriptRoot`. D-014 governance limited to three documents.
    D-015 staleness checked by command. D-016 dependency ranges, not a lockfile.
    All registered in `docs/DECISIONS.md`.

Watch   :
  - **A VS Code integrated terminal inherits its environment from the VS Code
    process, not the registry.** After any installer writes PATH, VS Code itself must
    be restarted - a new terminal is not enough. This cost one cycle.
  - `Invoke-Logged.ps1` originally buffered output and wrote once at the end, so an
    interrupted command left no artefact at all. It now streams to disk line by line
    and records STATUS RUNNING / COMPLETED / FAILED. Any future runner must do the
    same.
  - Every `tools\` script prints exactly two lines to the console - a verdict and the
    artefact path. An earlier version of `Add-LocalBinToPath.ps1` echoed its whole
    report; that is the anti-pattern.
  - D-016 was cited in `requirements.txt` before it was registered, and the original
    `Check-Docs.ps1` scanned only three governance files so it would not have caught
    it. The scan now covers `*.md` and `*.txt` at the root, all of `docs\`, and
    `tools\*.ps1` and `*.py`. Do not narrow it again.

Next    : Three commands, in order, none yet run:
            1. `.\tools\Session-Open.ps1`   - census; confirm `origin` exists
            2. `.\tools\Setup-Venv.ps1`     - create `.venv`, install the toolchain
            3. `.\tools\Check-Docs.ps1`     - interpreter assertion becomes checkable
          Then scaffold Django: `config` project, `qualifications` app, health-check
          view, `pyproject.toml` (ruff, pytest, coverage), first passing test.
          Nothing is committed yet - the first commit is still ahead and should carry
          the whole foundation as one deliberate change.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 002:

```
Session 002, AccountA. Sprint A.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any edit.

To reconcile at Section 0.5:
  1. `gh repo create qvs --public --source=. --remote=origin` ran outside
     Invoke-Logged.ps1 and is recorded UNVERIFIED. Confirm `origin` from the
     REMOTES section of the census, not from the log.
  2. There are no commits yet and the working tree is untracked, not dirty. That
     is the expected state and does NOT mean the other account is mid-session.

Already run:  Bootstrap.ps1, Install-Toolchain.ps1, Add-LocalBinToPath.ps1,
              Setup-Repo.ps1, Check-Docs.ps1 (verdict DOCUMENTS CURRENT),
              gh auth login, gh repo create.
Not yet run:  Session-Open.ps1, Setup-Venv.ps1, and a second Check-Docs.ps1.

Next action: run those three, then scaffold Django - `config` project,
`qualifications` app, health-check view, `pyproject.toml` configuring ruff,
pytest and coverage, and one passing test.

Do not commit until the whole foundation is in place. The first commit should be
one deliberate change carrying all of it.

Give me commands in separate labelled blocks, one command per block.
```

## Session 002 - ACCOUNT HANDOVER - AccountA -> AccountB - 2026-09-07 20:05

Token   : QVS-S002-A2B-NOHEAD
          There is still no commit, so the sha7 the token format requires does not
          exist. See Open item 3 - HANDOVER.md Section 1.3 assumes a HEAD and has no
          shape for a handover made before the first commit.

Sprint  : A (foundation)
Branch  : main (unborn - a branch does not appear in refs until it has a commit)

Done    :
  - Section 0 run in full. `origin` CONFIRMED from the census REMOTES section as
    https://github.com/Michael-Tonderai/qvs.git. The UNVERIFIED marker session 001
    put on `gh repo create` is retired.
  - `.venv` created on Python 3.12.10. Installed: Django 5.2.17, pytest 9.1.1,
    pytest-django 4.14.0, pytest-cov 7.1.0, ruff 0.16.6, bandit 1.9.4,
    coverage 7.16.0, pip 26.2.1. `gunicorn` was correctly skipped by its
    `sys_platform` marker - D-016 working on its first real test.
  - `tools\Session-Open.ps1` rewritten for three defects found on its first run:
      (a) the working tree was classified on whether `git status --porcelain`
          returned anything, so an untracked-only repository reported DIRTY. DIRTY
          is the one signal Section 0.5 uses to mean "the other account is
          mid-session", and a false positive there stops a session for nothing -
          worse than no signal, because a signal that cries wolf gets overridden by
          habit. It now classifies on the porcelain status codes.
      (b) the "(no commits yet)" fallback never fired. `git log` on an unborn branch
          writes to stderr; `2>&1` turned that into a nine-line NativeCommandError
          dump, and the fallback tested for empty output, which error text is not.
          Commit presence is now established with `git rev-parse --verify HEAD` and
          its exit code, with stderr sent to $null.
      (c) the session-log tail was read without `-Encoding UTF8`.
    It also writes its artefact as ASCII with no BOM, and prints the tree verdict on
    the console so the one fact a session most needs arrives before any file is read.
  - `tools\Check-Ascii.ps1` written. New, read-only. Reports non-ASCII characters by
    code point with the offending line rendered safely, and treats a byte order mark
    as a failure.
  - `tools\Fix-Encoding.ps1` written. New, one-time normaliser with `-DryRun`,
    `-Exclude` and automatic backups.
  - Repository normalised: 131 characters across 6 files - 85 em dashes, 43 section
    signs, 3 en dashes. Zero unmapped, zero CRLF found (D-012 was already holding on
    its own), zero BOMs. Verified afterwards as ASCII CLEAN across 19 files.
    Backups in `dev_reports\encoding_backup\`.
  - `CLAUDE.md` Section 5 gained the ASCII rule, inserted surgically with an anchor
    that had to match exactly once.
  - D-018 registered in `docs\DECISIONS.md`, appended rather than rewritten.

HEAD    : (no commits yet)  NOT PUSHED
Tree    : untracked only - no tracked modifications. This is the expected state and
          does NOT mean an account is mid-session.
Issues  : none opened yet

Decided :
  - D-018 - repository text is ASCII only, enforced by `tools\Check-Ascii.ps1`.
    Registered.
  - The Django scaffold was deliberately not started. The session budget went to the
    census and encoding defects instead. That was the right trade: both are
    foundation faults, and a foundation fault gets more expensive the moment there is
    history sitting on top of it. Nothing about the scaffold got harder by waiting.

Open    :
  1. `CLAUDE.md` Section 7 says Claude Code writes files into the repo. This session
     Claude Desktop wrote three `tools\` scripts directly through the Filesystem
     connector, because they needed line-by-line reasoning and routing them through a
     second agent adds a translation step plus the "Claude Code's own report is not
     evidence" problem. Deliberately NOT registered as a decision, because Sir Ton
     has not ruled on it. Either amend Section 7 - Desktop writes tooling and docs,
     Claude Code writes application code - or revert to routing everything through
     Claude Code. Do not leave the file contradicting the practice.
  2. The Django scaffold. This is the next action and nothing blocks it.
  3. HANDOVER.md Section 1.3 has no shape for a handover made before the first
     commit. It requires a sha7 for the token and a pushed HEAD, and Section 1.1.1
     says a session ends committed and pushed. Two sessions have now closed without a
     commit, both for good reasons. Either write the pre-first-commit exception into
     Section 1.1 or accept that the first commit must land before any further
     handover. Currently the protocol is being knowingly deviated from, which is the
     state it exists to prevent.
  4. `requirements-dev.txt` bounds pytest as `>=8.0` with no upper bound and it
     resolved to 9.1.1. Django is correctly bounded `>=5.2,<5.3`. Either bound the
     test tooling the same way or record in D-016 why the runtime and the toolchain
     are treated differently.

Watch   :
  - **A script that rewrites repository text must be written so it cannot match its
    own source.** `Fix-Encoding.ps1` first carried a tidy-up pass whose search string
    was the word Section followed by two spaces. Running over its own file it
    collapsed that literal, leaving a `while` loop whose condition is always true -
    an infinite loop, in a script that writes files, in a repository with no commit
    to recover from. The dry run caught it before it ran. Build needles from numeric
    character codes (`[char] 0x2014`), never from the characters themselves, and
    prefer a regex that consumes what follows to a second tidy-up pass.
  - **A file queued for writing with nothing in its report is a defect, not a
    no-op.** That blank line was what made the bug easy to miss.
    `Fix-Encoding.ps1` now says so explicitly.
  - The Filesystem connector writes UTF-8 with no BOM and preserves LF. Confirmed by
    `Check-Ascii.ps1` scanning the three files it had just written.
  - `bandit --version` reports itself as `__main__.py 1.9.4`. A naive version regex
    in `Check-Docs.ps1` will not match that if bandit is ever asserted there.
  - `Check-Docs.ps1` still reads five files without `-Encoding UTF8` and writes its
    artefact with a BOM. Both are harmless under D-018 and were deliberately left:
    rewriting 250 lines to change nothing that matters is not a good use of the
    deadline.

Next    : Scaffold Django. `config` project, `qualifications` app, health-check view,
          `pyproject.toml` configuring ruff, pytest and coverage, and one passing
          test. Then `Check-Ascii.ps1`, `Check-Docs.ps1`, and one deliberate first
          commit carrying the entire foundation. Nothing is committed before that.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 003:

```
Session 003, AccountB. Sprint A.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any
edit.

Token: QVS-S002-A2B-NOHEAD
There is no commit yet, so the token carries no sha7. That is not a mismatch.

To reconcile at Section 0.5:
  1. There are still no commits and the working tree is untracked, not dirty. The
     census now says UNTRACKED ONLY rather than DIRTY - that wording is the fix
     made in session 002, not a new state.
  2. main is unborn, so the BRANCHES section is empty. Expected.
  3. origin was VERIFIED in session 002 from the census REMOTES section. Do not
     re-litigate it.

Already run:  Bootstrap.ps1, Install-Toolchain.ps1, Add-LocalBinToPath.ps1,
              Setup-Repo.ps1, Session-Open.ps1, Setup-Venv.ps1, Check-Ascii.ps1,
              Fix-Encoding.ps1 (applied, repository is ASCII CLEAN),
              gh auth login, gh repo create.
Not yet run:  Check-Docs.ps1 since the venv was created and CLAUDE.md was patched.
              Run it early - it can now verify the interpreter assertion, which it
              could not before.

Next action: scaffold Django - config project, qualifications app, health-check
view, pyproject.toml configuring ruff, pytest and coverage, and one passing test.

Before the first commit, decide Open item 1 from the session 002 block: CLAUDE.md
Section 7 says Claude Code writes files, but Claude Desktop wrote three tools\
scripts through the Filesystem connector in session 002. Amend the file or change
the practice; do not let them disagree across a commit.

Do not commit until the whole foundation is in place. The first commit should be
one deliberate change carrying all of it, and Check-Ascii.ps1 and Check-Docs.ps1
both run before it.

Give me commands in separate labelled blocks, one command per block.
```

## Session 003 - ACCOUNT HANDOVER - AccountB -> AccountA - 2026-09-07 21:20

Token   : QVS-S003-B2A-06a7ad4
          Per HANDOVER.md Section 1.3, the sha7 is the commit this session's WORK left
          behind, not the close commit carrying this block. Expect the census to show
          HEAD one commit ahead of the token, and that commit to be this close commit.

Sprint  : A (foundation)
Branch  : develop

Done    :
  - Section 0 run in full. No divergence. The census artefact on disk at open was
    stale - written 18:36, thirteen minutes before Session-Open.ps1 was itself
    rewritten - so it was re-run rather than trusted. An artefact older than the
    script that produced it is not evidence.
  - Open item 1 decided. D-019 registered: Claude Desktop is the default writer
    through the Filesystem connector; Claude Code is for bulk edits, long command
    sequences and gh. CLAUDE.md Section 7 amended to match, before any file was
    written under the new rule.
  - Django foundation scaffolded and committed. config project (settings, urls,
    wsgi), qualifications app (apps, models, urls, views, migrations package),
    tests package, manage.py, pyproject.toml, .env.example. Hand-written rather than
    generated, because CLAUDE.md Section 5 requires a path comment on line 1 and
    django-admin startproject does not produce one.
  - pyproject.toml configures ruff (lint and format, Django rules on, security rules
    left to bandit), pytest (pytest-django, strict markers, unit/integration/req) and
    coverage (branch measurement, floor of 80).
  - Root commit 06ab3dc on main, pushed. develop branched from it and pushed.
  - D-020 registered and CLAUDE.md Section 6 amended: commit messages are written to
    dev_reports\commit_message.txt, used with git commit -F, and deleted by an
    explicit command afterwards.
  - D-021 registered: the root commit lands directly on main because develop cannot
    be branched from a commit that does not exist and GitHub cannot protect an
    unborn ref. Later refined by D-023.
  - D-022 registered and CLAUDE.md Section 4 amended: every git and gh command goes
    through Invoke-Logged.ps1 whether or not Claude needs the output. Delivered
    through the full workflow - issue #1, branch, PR #2 with a self-review comment,
    squash merge into develop. The first exercise of D-009.
  - HANDOVER.md Section 1.3 amended to define which sha7 the token carries, closing
    session 002 open item 3. The token cannot name the commit that contains it.
  - D-023 registered: session-close log commits go straight to develop.
  - REQ-N-004 reworded - branch coverage is enabled, so the requirement said
    "statement coverage" while the configuration measured more than that.
  - Session 002 open item 4 closed. requirements-dev.txt now bounds the test
    toolchain with upper bounds, with the runtime-versus-toolchain distinction
    written into the file.

HEAD    : 06a7ad4e9cd2c89a95696b7a5438e76e8e9ff50c  PUSHED  (develop)
          main is at 06ab3dcc3ea27293b861ab6817ea5cc9a82a8d13, one commit behind by
          design - main moves by release PR, not by drift.
Tree    : clean
Issues  : #1 closed by PR #2. No issues open.

Decided :
  - D-019 - Claude Desktop is the default writer; Claude Code for bulk and gh.
  - D-020 - commit messages written to a file, used with -F, then deleted.
  - D-021 - the root commit lands directly on main. Refined by D-023.
  - D-022 - git and gh output goes to an artefact, never to the terminal.
  - D-023 - session-close log commits go straight to develop.
  - The scaffold carries no model. Putting a half-specified Qualification model in
    the root commit would have put a migration into history before REQ-F-001 and
    REQ-F-002 were designed, and a migration is the expensive thing to take back.
  - Settings carry no committed SECRET_KEY fallback, not even a development one. A
    missing key generates an ephemeral value under QVS_DEBUG=1 and is a start-up
    error otherwise. A committed placeholder is the string that reaches production.
  - TIME_ZONE is UTC, not Africa/Harare. REQ-F-007 writes an audit event per
    verification attempt and an audit trail that moves with a server's local zone is
    not evidence.

Open    :
  1. main is not protected. The command was deliberately not issued because it is
     not known whether rule enforcement is available on this repository's plan and
     visibility. Check what the repository supports before asserting a command.
  2. Nothing enforces D-022. Check-Ascii and Check-Docs cannot see whether a command
     was wrapped, so the rule holds by discipline alone - which is precisely what
     D-015 exists because it failed before. A guard is possible in tools\Check.ps1
     once that exists. Named in the PR #2 self-review and deliberately not built
     there; it should become an issue.
  3. docs/evidence/ is on the CLAUDE.md Section 9 document map and does not exist on
     disk. Check-Docs section B passed because it checks the five .md files by name
     and enumerates docs\*.md in the other direction - a mapped DIRECTORY is checked
     by neither.
  4. The census log tail has stopped being useful. Session-Open.ps1 reads the last 40
     lines of SESSION_LOG.md, and since D-017 every block ends with a ~40-line
     opening prompt, so the tail now shows only the previous session's prompt. Sprint,
     HEAD, Tree and Next are all above the window.
  5. Sprint A is not finished. No Dockerfile, no docker-compose.yml, no GitHub
     Actions workflow. REQ-N-001 and REQ-N-003 are both unsatisfiable until they
     exist, and D-007 commits the pipeline definition to the repository.

Watch   :
  - **A staging list written by hand omits what nobody is looking for.** tools\ was
    left out of the first git add. Ten scripts - including the three gates whose
    verdicts the commit message cited - sat untracked while the commit claimed to
    carry the whole foundation. The pre-commit git status caught it, but only because
    the artefact was read: the instruction given beforehand named what to forbid
    (.venv, dev_reports, coverage.xml) and not what to expect. Absence is harder to
    see than presence. Name the expected set, not the forbidden one. Fixed by
    amending the root commit with --force-with-lease, which was cheap only because
    nothing had been fetched by anyone.
  - gh pr merge --delete-branch leaves you on the repository's DEFAULT branch, which
    is main, not on develop. Switch back explicitly or the next piece of work starts
    from the wrong branch, invisibly.
  - Check-Docs.ps1 section C is live from this session. It skipped for three sessions
    with "no commits yet - nothing to compare against" and now runs a real comparison.
    It will fail the moment the session log falls behind a commit.
  - ruff format and the E501 ignore on config/settings.py are load-bearing together.
    The AUTH_PASSWORD_VALIDATORS entry is 90 characters even after the formatter
    expands it, because a string literal cannot be split. Removing the per-file
    ignore will fail lint; removing the expansion will fail format.
  - The venv interpreter assertion in Check-Docs section A ran for the first time
    this session. It could not run before because .venv did not exist when the check
    was last executed.

Next    : Finish Sprint A. Dockerfile and docker-compose.yml pinning name: qvs
          (REQ-N-003, D-008, D-013), then .github/workflows/ci.yml running ruff,
          bandit and pytest on push and pull request (REQ-N-001, D-007). Both through
          the D-009 workflow - issue, branch, PR into develop, self-review. Then
          protect main and open a release PR from develop.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 004:

```
Session 004, AccountA. Sprint A.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any
edit.

Token: QVS-S003-B2A-06a7ad4

To reconcile at Section 0.5:
  1. The token names 06a7ad4, the commit session 003's WORK left behind. HEAD will
     be ONE commit ahead of it - that commit is the session 003 close commit
     carrying the log block. HANDOVER.md Section 1.3 now defines this. It is the
     expected state, not a divergence. HEAD more than one ahead is not.
  2. develop is the current branch and is AHEAD of main by the D-022 merge. main
     moves by release PR only. Expected.
  3. main is not protected yet. Open item 1, not an oversight.
  4. The census log tail will show only the tail of this opening prompt, not the
     Sprint, HEAD, Tree and Next fields. Open item 4. Read the log file directly
     rather than relying on the census tail.

Already run:  Everything in Sprint A up to and including the Django scaffold, the
              root commit 06ab3dc on main, develop branched and pushed, and issue
              #1 / PR #2 delivering D-022 through the full D-009 workflow.
              Bootstrap.ps1, Install-Toolchain.ps1, Add-LocalBinToPath.ps1,
              Setup-Repo.ps1, Setup-Venv.ps1, Session-Open.ps1, Check-Ascii.ps1,
              Check-Docs.ps1, Fix-Encoding.ps1, gh auth login, gh repo create.
Not yet run:  Anything Docker. Anything CI. No workflow file exists, so no pipeline
              has ever run.

Next action: finish Sprint A. Dockerfile and docker-compose.yml pinning name: qvs
(REQ-N-003, D-008, D-013), then .github/workflows/ci.yml running ruff, bandit and
pytest on push and pull request (REQ-N-001, D-007). Each through the D-009
workflow - issue, branch, PR into develop, self-review comment. D-023 exempts only
the session-close commit.

Also worth doing early, both small: open an issue for the D-022 enforcement gap
(open item 2 - nothing checks that git and gh commands are wrapped), and decide
whether docs/evidence/ should be created or removed from the CLAUDE.md Section 9
map (open item 3).

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages are written to a file, used with -F, and deleted afterwards (D-020).

Give me commands in separate labelled blocks, one command per block.
```

---

## Session 004 - ACCOUNT HANDOVER - AccountB -> AccountA - 2026-09-07 22:35

Token   : QVS-S004-B2A-44e1cfb
Sprint  : A
Branch  : develop

Done    :
  - .github/workflows/ci.yml added - the project's first pipeline. One job,
    quality, on ubuntu-latest and Python 3.12, running five named steps: the ASCII
    guard under pwsh (D-018), ruff check and ruff format --check (D-005), bandit
    -ll (D-006), and pytest with branch coverage (D-004, REQ-N-004). Triggers are
    push to main and develop, and pull_request into either.
  - REQ-N-001 now has a mechanism. It was unsatisfiable for three sessions because
    no workflow existed and no pipeline had ever run.
  - The pipeline was GREEN on its first ever run - completed success in 27 seconds,
    run 34159059800, pull_request trigger. No runner-versus-local difference
    surfaced.
  - tools/Check-Ascii.ps1 made separator-agnostic. It trimmed and split relative
    paths on backslash only, so under pwsh on Linux the path came back as one
    element, nothing matched $SkipDirs, and .git was scanned. It would have passed
    regardless - but only because no file inside .git happens to carry an extension
    in $TextExt.
  - pyproject.toml no longer describes REQ-N-004 as statement coverage. Session 003
    reworded the requirement to branch coverage and branch = true sits two lines
    below the comment, so it contradicted both.
  - docs/evidence/ created with an empty .gitkeep. Session 003 open item 3 closed as
    to its symptom; the underlying Check-Docs gap is not fixed and is carried below.
  - Issue #3 opened, PR #4 opened with a full self-review comment, squash-merged
    into develop, branch deleted. The second exercise of D-009.
  - Session 003 open item 1 answered with fact rather than assumption: gh repo view
    reports the repository is PUBLIC, owner Michael-Tonderai, default branch main.
    Classic branch protection is therefore available, and after the first pipeline
    run GitHub now knows the check name to require. Protecting main is an
    actionable task, not a constraint to document.
  - docs/HANDOVER.md Section 1.3 and Section 1.5 amended - see Decided below.

HEAD    : 44e1cfb  PUSHED  (develop)
          main is at 06ab3dc, now THREE commits behind develop by design - main
          moves by release PR, not by drift.
Tree    : clean
Issues  : #1 closed by PR #2. #3 closed by PR #4. No issues open.

Decided :
  - CI was built before Docker, reversing the order session 003 left behind. The two
    do not depend on each other, and going CI-first meant every subsequent pull
    request carries a check rather than the Docker PR merging unchecked; the CI PR
    validated its own workflow because GitHub runs pull_request workflows from the
    PR head; the check name needed for branch protection now exists; and the
    riskiest piece was front-loaded while session time remained.
  - No docker build step in ci.yml. REQ-N-001 names lint, security scan and tests.
    A build step would have coupled the CI PR to a Dockerfile that did not exist.
  - One job with named steps rather than four parallel jobs. Four jobs would each
    pay for a checkout, a Python setup and a dependency install to run one command.
    Revisit only if the report wants four separate ticks in a screenshot.
  - Ubuntu, not Windows, despite Windows development. The deployment target is a
    Linux container (D-008); testing on Windows would leave the container's platform
    untested while proving something about a platform nothing ships on.
  - CI runs with QVS_DEBUG=0 and keys generated inside the step. Under QVS_DEBUG=1
    the settings.py fallback generates an ephemeral SECRET_KEY, which would mask a
    missing key rather than prove the start-up error works. No key is committed, so
    REQ-N-002 holds.
  - tools/Check-Docs.ps1 deliberately NOT in CI. It asserts the tool versions and
    paths in CLAUDE.md Section 2 against the machine it runs on, and a runner has no
    Docker Desktop, no gh at the pinned version and no .venv. It would fail for
    being correct. It stays a pre-commit gate.
  - docs/evidence/.gitkeep is deliberately empty. CLAUDE.md Section 9 already states
    what the directory holds, and a second copy of that sentence is how one of them
    goes stale.
  - The three issues this session identified were NOT opened, to conserve a nearly
    exhausted account budget. They are recorded under Open below and lose nothing by
    being opened by the session that fixes them.
  - docs/HANDOVER.md Section 1.5 amended so the opening prompt no longer asserts
    which account will open the next session. A closing session can state an
    intention, not a fact. The opening session states the account it is actually
    signed into at Section 0.6, and that statement wins over the prompt.
  - docs/HANDOVER.md Section 1.3 amended to say the token's direction letters record
    intent, not fact. B2A with the same account continuing is a naming artefact; the
    sha7 does the token's actual job regardless of who holds the keyboard.

Open    :
  1. **tools/Invoke-Logged.ps1 does not capture stderr from native commands.** The
     most important item in this block. The 2>&1 applies to the Invoke-Expression
     cmdlet, not to the native process inside the string it evaluates, so git's
     stderr reaches the console and never the artefact. Evidence: git fetch --prune
     demonstrably deleted a stale remote ref and git switch -c demonstrably created
     a branch, and both artefacts recorded "(no output)". The push artefact splits
     exactly on stream boundaries - the "set up to track" line is present (stdout)
     while the remote: lines and the To https://... summary are absent (stderr).
     Reproducible, not flaky. WHY IT MATTERS: when a git command FAILS, the error
     text is exactly what will be missing, leaving a non-zero exit code and a silent
     file. D-022 exists so git detail is read from disk, and it currently delivers a
     filtered half. Likely fix is to apply the redirection inside the evaluated
     string rather than to the cmdlet. Should be the next session's first action.
  2. main is not protected - now a task, not an unknown. The repository is public
     and the CI check has run, so the check name is selectable.
  3. Nothing enforces D-022. Carried from session 003 and from PR #2's self-review,
     still unbuilt. A guard belongs in tools\Check.ps1 once that exists.
  4. Check-Docs.ps1 Section B cannot see a mapped DIRECTORY. It verifies named .md
     files in one direction and enumerates docs\*.md in the other. Creating
     docs/evidence/ fixed the instance and left the hole for the next one.
  5. The census log tail is still not useful - Session-Open.ps1 reads the last 40
     lines and every block ends with a long opening prompt. Carried from session
     003. Read the log file directly.
  6. Sprint A is not finished. No Dockerfile, no docker-compose.yml. REQ-N-003 is
     unsatisfiable until they exist.

Watch   :
  - **Coverage under CI parity is 87.50%, not the 93.75% an older artefact reports.**
    The gap is config/settings.py lines 36-41, the ephemeral SECRET_KEY fallback,
    which only executes when QVS_DEBUG=1 and no key is supplied. The deployed
    configuration has materially less headroom above the REQ-N-004 floor of 80 than
    the development one. Read the number from a QVS_DEBUG=0 run or it flatters
    itself.
  - **The Filesystem connector's edit_file matches the FIRST occurrence of the text
    it is given, not the last.** This block was initially appended after session 001
    instead of at the end of the file, because the anchor used was the closing line
    of an opening prompt - which is identical at the end of every block. Caught by
    reading the returned diff, which showed "## Session 002" immediately after the
    inserted text. Reverted and re-applied against an anchor unique to the last
    block. When appending to this file, anchor on something only the newest block
    contains, and read the diff before trusting the edit.
  - The session 003 Watch note about gh pr merge --delete-branch was correct and
    fired again: it leaves you on main, not develop. Switching back explicitly is
    the whole fix, now confirmed twice.
  - Session 004's opening prompt said AccountA; the session actually ran on
    AccountB, because session 003 wrote the prompt expecting a handover that did not
    happen. The Section 0.6 block repeated the prompt instead of the reality, which
    is the wrong way round. Fixed at the cause by the Section 1.5 amendment.
  - Running the suite under QVS_DEBUG=1 exercises a configuration that is never
    deployed. Local runs should set QVS_DEBUG=0 to match CI.

Next    : Fix the Invoke-Logged.ps1 stderr defect first, through the D-009 workflow -
          it is small, and until it lands every git command is logged blind. Then the
          Dockerfile and docker-compose.yml pinning name: qvs (REQ-N-003, D-008,
          D-013), also through D-009. Then protect main and open a release PR from
          develop to main, which will be the first change to reach main since the
          root commit.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 005:

```
Session 005. Sprint A.
Closing session ran on: AccountB. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects. Session 004 opened under
a prompt naming the wrong account precisely because the closing session guessed.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any
edit.

Token: QVS-S004-B2A-44e1cfb

To reconcile at Section 0.5:
  1. The token names 44e1cfb, the commit session 004's WORK left behind. HEAD will
     be ONE commit ahead of it - the session 004 close commit carrying the log
     block. HANDOVER.md Section 1.3 defines this. Expected, not a divergence. HEAD
     more than one ahead is not.
  2. The token reads B2A. Per Section 1.3 as amended in session 004, the direction
     letters record intent, not fact. If you are on AccountB, say so at Section 0.6
     and carry on - the sha7 is what the token is actually for.
  3. develop is THREE commits ahead of main, which sits at 06ab3dc. main moves by
     release PR only. Expected.
  4. main is not protected. Open item 2, now a task rather than an unknown - the
     repository is public and the CI check has run, so the check name is selectable.
  5. The census log tail shows only the tail of this prompt, not the Sprint, HEAD,
     Tree and Next fields. Open item 5. Read the log file directly.

Already run:  Everything in Sprint A except Docker. Django scaffold, root commit
              06ab3dc on main, develop branched, issue #1 / PR #2 delivering D-022,
              and issue #3 / PR #4 delivering .github/workflows/ci.yml - which ran
              GREEN on its first execution. gh auth login, gh repo create, and all
              of Bootstrap, Install-Toolchain, Add-LocalBinToPath, Setup-Repo,
              Setup-Venv, Session-Open, Check-Ascii, Check-Docs, Fix-Encoding.
Not yet run:  Anything Docker. No Dockerfile, no docker-compose.yml, no container
              has ever been built. main has never been protected.

Next action: fix the tools\Invoke-Logged.ps1 stderr defect FIRST - see Open item 1
in the session 004 block for the evidence and the likely fix. It is small, and
until it lands every git command is logged blind: a FAILING git command writes its
error to stderr, which the artefact currently discards, leaving a non-zero exit
code and a silent file. Through the D-009 workflow. Then the Dockerfile and
docker-compose.yml pinning name: qvs (REQ-N-003, D-008, D-013), also through
D-009. Then protect main and open a release PR from develop.

Also still open and unopened as issues, deliberately: the D-022 enforcement gap
(nothing checks that git and gh commands are wrapped) and the Check-Docs gap on
mapped directories. Open them when you fix them.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages are written to a file, used with -F, and deleted afterwards (D-020).
Run the suite with QVS_DEBUG=0 to match CI.

Give me commands in separate labelled blocks, one command per block.
```
