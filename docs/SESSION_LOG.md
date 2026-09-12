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

---

## Session 005 - SESSION CLOSE - AccountA - 2026-09-08 00:45

Sprint  : A
Branch  : develop (work committed on fix/invoke-logged-stderr, PR #7 open)

Done    :
  - tools/Invoke-Logged.ps1 stderr defect fixed - issue #5. The 2>&1 was applied to
    the Invoke-Expression cmdlet rather than to the native process inside the string
    it evaluated. Redirection moved inside the evaluated string; merged stderr now
    rendered with ToString() rather than Out-String, which would have wrapped each
    one-line git message in the full PowerShell error apparatus. The resulting
    single-command constraint is written into the script header.
  - Log currency moved from tools/Check-Docs.ps1 to tools/Session-Open.ps1 - issue #6,
    D-025. It now measures commits rather than dates: the newest block names the
    commit its session left behind, and HEAD should be that commit or the close
    commit one above it. Check-Docs keeps version drift, document map and decision
    references and is now three families, not four.
  - Artefact encoding changed from UTF8 to ASCII in both scripts. PowerShell 5.1
    emits a byte order mark for -Encoding UTF8, which had been sitting at the head of
    every artefact - the corruption class D-018 exists to remove, inside the tooling.
  - Stale remotes/origin/ci/REQ-N-001-github-actions tracking ref pruned. Session 004
    deleted the remote branch; the local tracking ref had survived.
  - Documents updated in the same session as the change: CLAUDE.md Sections 6 and 10,
    docs/HANDOVER.md Section 0.4, docs/DECISIONS.md (D-024, D-025, and D-015 marked
    REFINED BY D-025 rather than edited).
  - Issues #5 and #6 opened, commit 5f14db1 pushed, PR #7 opened against develop.

HEAD    : ea98a11  PUSHED  (develop - unchanged by this session's work)
Work    : 5f14db1 on fix/invoke-logged-stderr, PUSHED, PR #7 open and unmerged
          main remains at 06ab3dc.
Tree    : clean
Issues  : #1, #3 closed previously. #5 and #6 OPEN - both close on PR #7 merging.

Decided :
  - One pull request closes two issues. #6's check failed on every commit including
    the commit fixing #5, so the alternatives were to park a verified fix or to argue
    past a gate. Arguing past a gate is how it stops being one. Recorded in D-025.
  - Log currency measured in commits, not dates (D-025). The date in a block is typed
    by hand; the commit carrying it is made minutes later. Session 004's block is
    headed 22:35 and its commit landed 00:05, so the gap crossed midnight and a
    current log was reported one day stale. Beneath that, a block cannot be written
    until its session closes, so every second commit of every session would have
    tripped the same gate. A one-day tolerance was rejected as a snooze.
  - gh issue and PR bodies use --body-file, as commit messages do under D-020 (D-024).
  - Artefact encoding treated as D-018 applied rather than as a new decision.

Open    :
  1. **PR #7 is open and unmerged.** The D-009 self-review comment has NOT been
     posted; its text is written and waiting at dev_reports\pr_review.txt. The CI run
     that the pull request triggered was never checked this session. Merging is the
     first action next session.
  2. **Section 1.3 and the new currency check both assume the session's work commit
     is on the branch the log is committed to.** Closing with an open PR breaks that,
     which is why this block records develop's sha under HEAD and the work commit
     under Work. Decide properly next session whether the HEAD field means the branch
     being logged or the work being handed over - do not leave it implicit.
  3. main is not protected. Repository is public and the CI check name is selectable.
  4. Nothing enforces D-022. Carried from session 003. Belongs in tools\Check.ps1.
  5. Check-Docs.ps1 Section B cannot see a mapped DIRECTORY. Carried from session 004.
  6. Sprint A is not finished. No Dockerfile, no docker-compose.yml. REQ-N-003 is
     unsatisfiable until they exist.
  7. Session-Open.ps1 prints "a dirty tree at session open means the other account is
     mid-session" whenever the tree is dirty. Correct at session open, misleading when
     the script is re-run mid-session as an acceptance test. Cosmetic.

Watch   :
  - **Three times this session Claude stated that a file had been written to disk
    when no write call had been issued** - the commit message file twice, and the PR
    body once. One of those compounded it by claiming a read-back that never happened.
    Each failed loudly and cheaply because the command was wrapped and the artefact
    carried git's own explanation. Composing a document inside a reply and writing it
    to disk are two acts that feel like one. The ordering that prevents it: write
    call, read-back, THEN the sentence describing the file. Never the sentence first.
  - The third of those failures is the best evidence in the change. An unplanned git
    failure produced "fatal: could not read log file ... No such file or directory" in
    the artefact where the old runner would have left a bare exit code.
  - Coverage under CI parity is 87.50%, not 93.75%. Carried from session 004. Read it
    from a QVS_DEBUG=0 run.
  - The Filesystem connector's edit_file matches the FIRST occurrence of its anchor.
    Carried from session 004. Anchor on text unique to the newest block.
  - Environment variables set in session 004's terminal (QVS_DEBUG=0 and two throwaway
    keys) persist only until that terminal closes. A fresh terminal has neither, and
    the suite will exercise the settings.py fallback the coverage note is about. Set
    them explicitly rather than relying on inheritance.

Next    : Post the self-review comment on PR #7 from dev_reports\pr_review.txt,
          confirm the CI run is green, squash-merge with --delete-branch, then switch
          back to develop and pull - gh pr merge leaves you on main, confirmed twice.
          Then the Dockerfile and docker-compose.yml pinning name: qvs (REQ-N-003,
          D-008, D-013) through D-009. Then protect main and open a release PR from
          develop.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 006:

```
Session 006. Sprint A.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any
edit.

No token: session 005 closed on the same account, so this is a SESSION CLOSE
rather than an ACCOUNT HANDOVER and Section 1.3 does not apply.

To reconcile at Section 0.5:
  1. The census now reports a LOG VERDICT as well as a TREE VERDICT. This is new in
     session 005 (D-025) and should read "current" with a distance of 1 - the
     session 005 close commit sitting above ea98a11 on develop.
  2. The session 005 block records HEAD as ea98a11, which is develop, and the
     session's actual work commit 5f14db1 under a separate Work field, because that
     commit is on an unmerged branch. Expected, and open item 2 in that block.
  3. PR #7 is OPEN against develop and closes both #5 and #6. It has no self-review
     comment yet. Its CI run has never been checked.
  4. develop is FOUR commits ahead of main plus the session 005 close commit, so
     five. main sits at 06ab3dc and moves by release PR only. Expected.
  5. main is still not protected.

Already run:  Everything in Sprint A except Docker. Issues #5 and #6 opened and
              fixed; commit 5f14db1 pushed to fix/invoke-logged-stderr; PR #7
              opened. Invoke-Logged.ps1 now captures stderr - verified four times,
              once by an unplanned failure. Log currency moved to Session-Open.ps1.
              Artefacts are ASCII with no byte order mark. The stale origin/ci
              tracking ref is pruned.
Not yet run:  The PR #7 self-review comment - its text is already written and
              waiting at dev_reports\pr_review.txt, so write nothing new for it,
              read that file. No CI check on PR #7. No merge. Anything Docker: no
              Dockerfile, no docker-compose.yml, no container ever built. main has
              never been protected.

Next action: post the self-review comment on PR #7 from dev_reports\pr_review.txt,
confirm the CI run is green, then squash-merge with --delete-branch and switch back
to develop and pull - gh pr merge leaves you on main, which has now bitten twice.
Then the Dockerfile and docker-compose.yml pinning name: qvs (REQ-N-003, D-008,
D-013) through D-009. Then protect main and open a release PR from develop.

Method note, from three failures in session 005: when a file is needed on disk,
issue the write call, read it back, and only then describe it. Claude stated three
times that a file was written when no write had been issued. The wrapped runner
caught every one, which is the argument for D-022 made by its own author's errors.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages and gh bodies are written to a file, used with -F or --body-file, and
deleted afterwards (D-020, D-024). Run the suite with QVS_DEBUG=0 to match CI, and
set it explicitly - a fresh terminal has not inherited it.

Give me commands in separate labelled blocks, one command per block.
```

---

## Session 006 - SESSION CLOSE - AccountA - 2026-09-08 13:40

Sprint  : A
Branch  : develop (session work on feature/REQ-N-003-docker-deployment, unmerged)

Done    :
  - PR #7 merged. Self-review comment posted from dev_reports\pr_review.txt, CI run
    confirmed green ("Lint, security and tests", 19s), squash-merged with
    --delete-branch. develop fast-forwarded 87aeaff..0bf7bd8 across six files.
    Issues #5 and #6 closed with it, and Check-Docs.ps1 passes on develop again -
    the D-024/D-025 citation failure is gone.
  - The session 005 stderr fix verified on live commands rather than on its own diff:
    `git switch` put "Switched to a new branch" into an artefact, and the Docker
    daemon failure printed its entire message. The pre-merge runner discarded both,
    and did so once in this session - `gh pr merge` logged "(no output)" beside exit
    0 because its confirmation goes to stderr.
  - Docker deployment written and committed as 4d1b1cb on
    feature/REQ-N-003-docker-deployment, pushed: Dockerfile (single stage,
    python:3.12-slim, non-root uid 10001, gunicorn), tools/docker-entrypoint.sh
    (migrate, collectstatic, exec), docker-compose.yml (name: qvs per D-013, host
    8020, named volume qvs-data), .dockerignore, and tools/New-DotEnv.ps1 which
    generates .env with two keys and refuses to overwrite an existing file.
  - WhiteNoise added to requirements.txt and wired into config/settings.py below
    SecurityMiddleware, with the compressing storage backend rather than the manifest
    variant.
  - Issue #8 opened for REQ-N-003 and deliberately left OPEN.
  - CLAUDE.md Section 2 now records Docker Desktop's per-user install path, that WSL
    is absent, and that wsl.exe writes UTF-16.

HEAD    : 0bf7bd8  PUSHED  (develop, before this block's close commit)
Work    : 4d1b1cb on feature/REQ-N-003-docker-deployment, PUSHED, NO PR opened.
          main remains at 06ab3dc, six behind develop.
Tree    : clean
Issues  : #5 and #6 closed by PR #7. #8 OPEN - REQ-N-003, and it stays open until a
          container is confirmed serving.

Decided :
  - REQ-N-003 read as one command to start after one-time configuration. REQ-N-002
    forbids committing the key the container cannot start without, so the two
    requirements cannot both be satisfied literally. Resolved with env_file .env,
    generated once by tools\New-DotEnv.ps1. Registered on the unmerged branch.
  - WhiteNoise rather than an nginx sidecar, and the compressing static storage
    backend rather than the manifest variant so the suite acquires no dependency on
    collectstatic. Registered on the unmerged branch.
  - **This block cites neither decision by number, deliberately.** Both are
    registered in docs/DECISIONS.md on feature/REQ-N-003-docker-deployment only. A
    numbered citation here would fail Check-Docs Section C on develop for exactly the
    reason session 005's citations did. Session 005 committed against that stale
    verdict in breach of CLAUDE.md Section 10; this session declines to repeat it.
    The numbers go in when the branch merges.
  - Session 005 open item 2 answered: **HEAD is the branch the log is committed to,
    Work is the commit being handed over.** The currency check in Session-Open.ps1
    measures develop, so HEAD must be develop or it measures nothing at all.
  - No PR opened for the Docker branch. Its body would have to describe a deployment
    nobody has run, and D-009 wants Closes #8 in it, which would close an unverified
    issue on merge.

Open    :
  1. **WSL is installed but the machine has not rebooted, so Docker has still never
     run.** Docker Desktop's Linux engine lives inside WSL2. `wsl --install
     --no-distribution` COMPLETED during this session - WSL 2.7.13 installed and the
     VirtualMachinePlatform optional component enabled - with DISM reporting that the
     changes take effect only after a restart. That restart had not happened when this
     block was written. Until it does, no image can be built, REQ-N-003 is unverified,
     and #8 cannot close. Note also that CLAUDE.md Section 2 **on the Docker branch**
     states that WSL is not installed. That was true when written and is now stale;
     correct it on that branch once the reboot has proved the engine starts.
  2. feature/REQ-N-003-docker-deployment is pushed with no pull request. Open it once
     the container is verified, with Closes #8 in the body.
  3. The HEAD/Work rule decided above belongs in docs/DECISIONS.md as a numbered
     entry. It was answered in a log block, which is where it was asked, not where it
     belongs. Register it when the Docker branch merges.
  4. **Check-Ascii.ps1 does not scan every file.** It reported 34 files on develop
     and 38 on feature/REQ-N-003-docker-deployment - a rise of four after five files
     were added. So exactly one of Dockerfile, .dockerignore, docker-compose.yml,
     tools/docker-entrypoint.sh and tools/New-DotEnv.ps1 is invisible to it. The
     extensionless Dockerfile is the likeliest candidate. Confirm which, then decide
     whether D-018's scope is what it should be - the verdict currently covers less
     of the repository than its wording suggests.
  5. main is not protected. Carried from session 003.
  6. Nothing enforces D-022. Carried from session 003. Belongs in tools\Check.ps1.
  7. Check-Docs.ps1 Section B cannot see a mapped DIRECTORY. Carried from session 004.
  8. Session-Open.ps1's dirty-tree wording is misleading when re-run mid-session.
     Cosmetic. Carried from session 005.

Watch   :
  - **Docker Desktop is a per-user install** at %LOCALAPPDATA%\Programs\DockerDesktop.
    Claude guessed C:\Program Files from "Docker Desktop" in CLAUDE.md Section 2 and
    lost a round trip. A version number is not an installation path. Now recorded.
  - **"docker 29.7.2" passing in Check-Docs proves only that a client binary exists.**
    It reported PASS on a machine whose engine cannot start at all. Every version
    check in Section A has this shape; none of them probes a running service.
  - **`docker info` returned EXIT CODE 0 while printing "Docker Desktop is unable to
    start".** The exit code was not a verdict. Read the artefact body, not the code.
  - wsl.exe writes UTF-16 while everything else here writes ANSI or ASCII, so its
    output arrives in an artefact spaced out. Encoding, not corruption.
  - WhiteNoise warns "No directory at: ...\staticfiles\" on any run where
    collectstatic has not run, which includes the local suite and CI. Harmless - the
    entrypoint collects before gunicorn starts - but it will be seen and is not a
    defect.
  - Coverage under CI parity is now 87.76%, threshold 80%. Read it from a QVS_DEBUG=0
    run.
  - Environment variables (QVS_DEBUG and the two throwaway keys) are shell-only and
    die with the terminal. Carried from session 004. The container is unaffected - it
    reads .env, which persists.
  - The Filesystem connector's edit_file matches the FIRST occurrence of its anchor.
    Carried from session 004. Anchor on text unique to the newest block.

Next    : Reboot, then `docker compose up -d --build`,
          browser-verify http://localhost:8020/admin/ serves with its stylesheet,
          confirm the qvs-data volume survives a down and a second up, then open the
          PR for feature/REQ-N-003-docker-deployment with Closes #8 in the body,
          self-review it, and merge. Then protect main and open a release PR from
          develop.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 007:

```
Session 007. Sprint A.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any
edit.

No token: session 006 closed on the same account, so this is a SESSION CLOSE and
Section 1.3 does not apply.

To reconcile at Section 0.5:
  1. develop does NOT contain the Docker work. It is committed as 4d1b1cb on
     feature/REQ-N-003-docker-deployment, pushed, with NO pull request open. That is
     deliberate - no container has ever been built, and a PR body would have had to
     describe a deployment nobody has run.
  2. docs/DECISIONS.md on develop ends at D-025. Two decisions from session 006 - the
     REQ-N-003 configuration reading and the WhiteNoise choice - are registered only
     on that branch. The session 006 log block describes both and cites neither by
     number, on purpose, so that Check-Docs passes on develop. Do not add the numbers
     to anything on develop before the branch merges.
  3. Check-Docs.ps1 and Check-Ascii.ps1 both PASS on develop. Session-Open.ps1 now
     prints a LOG VERDICT as well as a TREE VERDICT - PR #7 merged, so the
     session-005 tooling is live. Expect currency "current" at a distance of 1.
  4. develop is SIX commits ahead of main, which sits at 06ab3dc and moves by release
     PR only. Expected.
  5. main is still not protected.

Already run:  PR #7 merged and its branch deleted; issues #5 and #6 closed. Issue #8
              opened for REQ-N-003 and left OPEN on purpose. All five Docker files
              written, committed as 4d1b1cb and pushed. WhiteNoise installed in the
              local .venv and wired into settings. .env generated by
              tools\New-DotEnv.ps1 and present on disk - do NOT regenerate it, the
              script refuses for a reason. Suite green at 87.76%.
Not yet run:  ANYTHING Docker at runtime. No image has been built, no container has
              ever started. `wsl --install --no-distribution` COMPLETED in session
              006 - WSL 2.7.13 plus VirtualMachinePlatform - but the reboot it
              requires had NOT been done, so verify the daemon rather than assuming
              it. CLAUDE.md Section 2 on the Docker branch still says WSL is not
              installed and needs correcting there. No PR for the Docker branch. main
              has never been protected. No release PR from develop.

Next action: confirm WSL is installed and the daemon answers, then
`docker compose up -d --build` from the feature branch. Browser-verify
http://localhost:8020/admin/ renders WITH its stylesheet - that is the whole point of
the WhiteNoise dependency, and a green suite does not test it. Confirm the qvs-data
volume survives `docker compose down` and a second `up`. Only then open the PR for
feature/REQ-N-003-docker-deployment with Closes #8, post a self-review comment, and
squash-merge. Then protect main and open a release PR from develop.

Three things session 006 learnt the hard way:
  - A version number in Check-Docs is not a working service. "docker 29.7.2" passed
    on a machine where the engine could not start, because the check reads the client
    binary. Do not treat a green Check-Docs as evidence that anything runs.
  - `docker info` exited 0 while printing that Docker Desktop could not start. Read
    the artefact body; the exit code lied.
  - Docker Desktop is at %LOCALAPPDATA%\Programs\DockerDesktop, not Program Files.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022) - now the
fixed runner, so stderr reaches the artefact. Commit messages and gh bodies are
written to a file, used with -F or --body-file, and deleted afterwards (D-020,
D-024). Run the suite with QVS_DEBUG=0 to match CI, and set it and the two throwaway
keys explicitly - a fresh terminal has inherited none of them, and QVS_DEBUG=0
without a key is fatal by design.

Give me commands in separate labelled blocks, one command per block.
```

---

## Session 007 - CLOSE - account not recorded - 2026-09-08 (written retrospectively)

Session 007 crashed out and never closed. This block was reconstructed during session
008 from the opening prompt session 008 was given, and from nothing else. Where a fact
was not stated there, it is recorded as not stated rather than inferred.

Sprint  : A
Branch  : develop
Done    :
  - Ran a census at 14:03:03. Local and origin shas identical, nothing lost.
  - Established, conclusively, that the personal laptop's boot loop is not held shut
    by Docker's virtualization layer: hypervisorlaunchtype was verified Off in the BCD
    store and Windows still would not boot.
  - Took the Route B deployment decision. Could not register it - no repository access.
HEAD    : c8df98a  (unchanged - session 007 made no commit)
Tree    : clean

Repository state as verified by that census:
  - develop at c8df98a, clean, seven commits ahead of main.
  - main at 06ab3dc, the root scaffold commit, not protected, no release PR.
  - feature/REQ-N-003-docker-deployment at 4d1b1cb, pushed, all five Docker files
    written, no pull request open. Issue #8 open for REQ-N-003.
  - docs/DECISIONS.md on develop ended at D-025.
  - Suite last green at 87.76%.

What session 007 established about the laptop, for the record and for whenever it
comes back:
  - Docker Desktop's engine had never started. `docker desktop start` hung
    provisioning the WSL distro, the machine hard-crashed, and it has not booted since.
  - Second occurrence this year, same trigger point.
  - Cleared: SSD SMART and component test; partition layout (EFI 100MB FAT32, 475GB
    NTFS healthy, 904MB recovery); Windows present at C:\WINDOWS; Startup Repair
    reporting zero root causes; memory quick check.
  - CONCLUSIVE: hypervisorlaunchtype Off in the BCD store, Windows still would not
    boot. The original crash may still have corrupted system files.
  - Remaining fix: an in-place repair upgrade from Windows 11 install media, keeping
    files and apps. Not attempted - media never built.
  - Untested: extensive memory test, power tests, processor, system board.

Watch   :
  - The laptop holds no unique repository content. Local and origin were identical at
    census time, so nothing is stranded on it.

---

## Session 008 - ACCOUNT HANDOVER - AccountA -> AccountB - 2026-09-08 22:45

Token   : QVS-S008-A2B-9fbefa9
Sprint  : A
Branch  : develop
Done    :
  - Moved the project to the corporate machine. Cloned fresh to
    C:\Users\tmachimbira\Projects\Development\qvs, rebuilt .venv on Python 3.12.6,
    regenerated .env, installed gh 2.100.0 at user scope, authenticated it.
  - Probed the network rather than assuming it: no proxy, no TLS interception on the
    github.com path (Sectigo public CA), api.github.com and the release-asset host both
    reachable, push exercised successfully.
  - Rewrote CLAUDE.md Section 2 against the machine as probed. Check-Docs returns
    DOCUMENTS CURRENT, one warning for Docker being absent.
  - Registered D-026 (Route B), D-027 (folder rename to qvs), D-028 (the Docker
    branch's merge gate becomes CI evidence). Marked D-008 and D-013 superseded.
  - Issue #9, branch feature/REQ-F-001-certificate-signing, PR #10 with a self-review
    comment, CI green in 29s, squash-merged to develop as 9fbefa9.
  - REQ-F-001, REQ-F-002 and REQ-N-004 moved to BUILT.
  - Wrote session 007's block retrospectively (above).
HEAD    : 9fbefa97522cbbf07a40f1c85de3a47b56465bc2  PUSHED
Tree    : clean
Issues  : #8 open (REQ-N-003), #9 closed by PR #10
Open    :
  - main is still not protected. No release PR from develop.
  - feature/REQ-N-003-docker-deployment has no PR. Under D-028 its gate is now a CI
    job that builds the image and starts the container on a runner. That job does not
    exist yet and must be written before the PR can be opened.
  - git fetch --prune is needed: origin/fix/invoke-logged-stderr is gone from the fresh
    clone as expected, but origin/feature/REQ-F-001-certificate-signing survives the
    --delete-branch as a stale tracking ref.
  - tools/traceability.py does not exist. REQUIREMENTS.md describes it as the generator
    for the traceability matrix in docs/evidence/, which is the evidence for the
    assignment's Automated Verification of Requirements section.
  - REQUIREMENTS.md defines VERIFIED as browser-confirmed, which no non-functional
    requirement can reach. REQ-N-001, REQ-N-002 and REQ-N-004 will sit at BUILT
    permanently under the current wording. Settle before generating the matrix.
  - REQ-N-003 still reads "starts from a single docker compose up". Under D-026 that is
    no longer the assessed start command.
  - canonical_payload uses default=str, which accepts any type silently. Revisit when
    REQ-F-003 starts feeding it model fields.
  - .vscode/ is untracked and not covered by .gitignore.
Decided :
  - D-026 Route B: deploy to a managed container service, superseding D-008.
  - D-027 the repository folder is renamed to qvs, superseding D-013.
  - D-028 the Docker branch merges on CI evidence, not on a local container run.
  - Not registered, taken inline: certificate IDs use a 30-symbol alphabet formatted
    QVS-XXXX-XXXX-XXXX-XXXX; the canonical payload is JSON with sorted keys; the
    signing key has no development fallback. All three are argued in PR #10's body and
    in the module's comments, which is where the report will draw them from.
Watch   :
  - DO NOT install Docker Desktop, WSL or any hypervisor component on this machine.
    It carries TaCRAS as well. CLAUDE.md Section 2 records this as a standing rule.
  - Commit 4d1b1cb is five files written from reasoning and executed nowhere, on any
    machine. It is the largest untested assumption in the repository and it may fail
    its first CI build. A green suite on develop is not evidence about it.
  - Invoke-WebRequest hangs indefinitely on this profile, with and without
    -UseBasicParsing. Cause not established. Use curl.exe with --max-time for
    downloads.
  - Session-Open.ps1 reports "branch not on origin - nothing pushed yet" on a fresh
    clone, because remote refs live in .git\packed-refs rather than as loose files.
    Cosmetic, but it will misreport on every future clone.
  - The old QVS_SIGNING_KEY died with the laptop and is unrecoverable, because .env is
    gitignored under REQ-N-002. Nothing had been signed, so nothing was lost. The
    tension between "no secret is committed" and "a signing key must outlive its
    machine" belongs in the report's critical evaluation.
  - tools/New-DotEnv.ps1 exists only on 4d1b1cb, not on develop. .env was hand-written
    this session from .env.example. Retrieve or rewrite the script when that branch
    merges.
Next    : Open the issue for REQ-F-003, branch, and add the Qualification model with a
          unique constraint on certificate_id, its signature field populated at issue
          via qualifications/signing.py, its first migration, and the register view
          behind login for REQ-F-004.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 009:

```
Session 009. Sprint B.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any edit.

Token: QVS-S008-A2B-9fbefa9

The environment changed in session 008 and CLAUDE.md Section 2 now describes it
correctly. Work happens on the corporate machine at
C:\Users\tmachimbira\Projects\Development\qvs, alongside TaCRAS.

DO NOT install Docker Desktop, WSL or any hypervisor component on this machine.
Not for verification, not for a quick check. Under D-026 the image is built and
run on a CI runner or not at all.

To reconcile at Section 0.5:
  1. Expect HEAD one commit above 9fbefa9, that commit being the session 008 close.
     That is the shape Section 1.3 describes.
  2. Two session 006 decisions - the REQ-N-003 configuration reading and the
     WhiteNoise choice - still exist only on feature/REQ-N-003-docker-deployment and
     are deliberately uncited by number on develop. Do not number them before merge.
  3. Session-Open.ps1 may report "branch not on origin" for a branch that is pushed.
     That is a defect in how it reads refs after a fresh clone, not a real divergence.
  4. main is still at 06ab3dc and still unprotected.

Already run:  Machine move complete - fresh clone, .venv on 3.12.6, .env written,
              gh 2.100.0 installed and authenticated as Michael-Tonderai. CLAUDE.md
              Section 2 rewritten and Check-Docs green. D-026, D-027, D-028
              registered. Issue #9 closed by PR #10, squash-merged as 9fbefa9.
              REQ-F-001, REQ-F-002, REQ-N-004 at BUILT. Session 007's block written
              retrospectively.
Not yet run:  git fetch --prune. Anything Docker, anywhere. The CI job that D-028
              requires before the Docker branch's PR can open. tools/traceability.py.
              main has never been protected and there is no release PR.

Next action: open the issue for REQ-F-003, branch, and add the Qualification model -
unique constraint on certificate_id, signature populated at issue through
qualifications/signing.py, first migration - then the register view behind login,
which carries REQ-F-004 with it.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages and gh bodies via file with -F or --body-file, deleted afterwards (D-020,
D-024). Run the suite with QVS_DEBUG=0 and both throwaway keys set explicitly - a
fresh terminal has inherited none of them. Use curl.exe with --max-time for any
download; Invoke-WebRequest hangs on this profile.

Give me commands in separate labelled blocks, one command per block.
```

---

## Session 009 - ACCOUNT HANDOVER - AccountA -> AccountB - 2026-09-10 21:30

Token   : QVS-S009-A2B-fcca63f
Sprint  : B
Branch  : develop
Done    :
  - Issues #11 (REQ-F-003) and #12 (REQ-F-004), branch
    feature/REQ-F-003-register-qualification, PR #13 squash-merged to develop as
    fcca63f. Two commits on the branch: 65200e5 the feature, d139468 the root redirect.
  - Qualification model, first migration, QualificationForm with a future-date
    validation rule, register view behind login_required, confirmation page also behind
    login, login and logout routes on Django's own auth views, four templates.
  - 24 new tests across four modules plus tests/conftest.py. Suite 41 passing,
    coverage 96.32% branch. models.py, forms.py, views.py, urls.py and signing.py all
    at 100%.
  - CI green twice on PR #13, 22s and 24s.
  - REQ-F-003 and REQ-F-004 moved to VERIFIED on browser evidence: all five steps in
    the PR body plus two follow-ups - a clean login with no `next` parameter, and a
    future award date rejected with the submitted fields preserved on re-render.
  - Fixed LOGIN_REDIRECT_URL, which was "/" and routed nowhere, so a successful login
    landed on a 404.
  - Routed the root to the register view. It had answered 404 since the project was
    scaffolded.
  - .vscode/ added to .gitignore.
  - Registered D-029 and D-030.
HEAD    : fcca63f  PUSHED
Tree    : clean
Issues  : #8 open (REQ-N-003), #11 and #12 closed by PR #13
Open    :
  - main is still at 06ab3dc, still not protected, still no release PR. This is now the
    oldest outstanding item in the project and REQ-N-001 cannot leave OPEN until it
    changes.
  - feature/REQ-N-003-docker-deployment has no PR. Under D-028 its gate is a CI job
    that builds the image and starts the container on a runner. That job does not exist.
  - tools/Set-Env.ps1 does not exist. D-030 registers the decision, not the script.
  - tools/traceability.py does not exist.
  - REQUIREMENTS.md defines VERIFIED as browser-confirmed, which no non-functional
    requirement can reach. REQ-N-001, REQ-N-002 and REQ-N-004 will sit at BUILT
    permanently under the current wording. Settle before generating the matrix.
  - REQ-N-003 still reads "starts from a single docker compose up". Under D-026 that is
    no longer the assessed start command.
  - canonical_payload still carries default=str. D-029 records why the model-side fix
    was taken instead and why tightening the function needs its own branch.
  - REQ-F-006 has four tests carrying its marker and a status of OPEN. The signature
    does break on tampering and those tests prove it, but the requirement is about
    verification behaviour and there is no verification path until REQ-F-005. The
    traceability matrix will show a requirement with tests and an OPEN status. That is
    honest, not a defect - but decide before the matrix is generated whether the
    generator should flag it.
  - The root redirect is temporary (302) and points at a login wall. REQ-F-005 gives
    the public an actual destination; revisit then.
Decided :
  - D-029 issued_at is inside the signed payload, set explicitly rather than by
    auto_now_add, with save() made idempotent over the issued fields so that tampering
    cannot repair itself.
  - D-030 the environment is loaded by an explicit tools\Set-Env.ps1 rather than by
    python-dotenv in settings.py.
  - Not registered, taken inline: certificate_id, issued_at, issued_by and signature
    are editable=False so no ModelForm can build inputs for them; the register view
    redirects after POST so a refresh cannot issue a second certificate; the root
    redirect is 302 rather than 301; the confirmation page is behind login because
    REQ-F-005 owns public lookup. All are argued in PR #13's body.
Watch   :
  - NO SELF-REVIEW COMMENT WAS POSTED ON PR #13. Session 008 posted one on PR #10, so
    this is a break in practice and the repository deliverable marks code review. It
    was declined deliberately: a review written by the author of the code does not
    answer the question that deliverable asks, and the four substantive objections were
    already disclosed in the PR body under their own headings. If a review thread is
    wanted, it needs Sir Ton reading the diff cold and objecting to something the author
    did not flag. Decide the policy before PR #14, and apply the same answer to #10
    retrospectively in the report rather than leaving two PRs treated differently.
  - The registrar_client fixture IS the client fixture with force_login called on it. A
    test asking for both receives one object and its supposedly anonymous request
    arrives authenticated. This passed silently once during session 009 before being
    caught. tests/conftest.py documents it. REQ-F-005 adds public verification tests,
    which is exactly the shape that walks into it - build a fresh django.test.Client().
  - A fresh terminal inherits none of QVS_DEBUG, QVS_SECRET_KEY or QVS_SIGNING_KEY, and
    twelve tests fail on ImproperlyConfigured when it has not been set. That is D-003
    working as designed, not a defect. It cost two runs this session. D-030 is the fix.
  - The signature covers issued_at to microsecond precision. Exact on SQLite and
    PostgreSQL; a backend that truncated sub-second precision would silently invalidate
    every existing record. Narrows D-002's claim - see D-029.
  - DO NOT install Docker Desktop, WSL or any hypervisor component on this machine. It
    carries TaCRAS as well. CLAUDE.md Section 2 records this as a standing rule.
  - Commit 4d1b1cb is five files written from reasoning and executed nowhere. Largest
    untested assumption in the repository.
  - Session-Open.ps1 did NOT misreport "branch not on origin" this session - local and
    origin shas matched and it read them correctly. The defect described in session
    008's block is quiescent on this clone, not fixed.
  - Session 008's opening-prompt copy in this log lists `git fetch --prune` under "Not
    yet run". It ran at 22:43:00, eighteen seconds after the close commit was written
    at 22:42:45, so the block was accurate when committed. It has deliberately NOT been
    edited: correcting a closed block to match what happened afterwards destroys the
    record. dev_reports\fetch_prune.txt is the evidence.
Next    : FIRST, protect main and open a release PR from develop. This has been listed
          as outstanding in every block since session 005 and has been read as
          background every time, because it has never appeared on a Next line. It is
          the direct evidence for REQ-N-001, the only requirement about the pipeline
          itself, and REQ-N-001 cannot leave OPEN until a merge to main is demonstrably
          gated. Budget is small; the risk is that branch protection may not be
          available for this repository's visibility and plan, in which case record the
          constraint rather than working around it silently - a documented inability to
          protect main is a legitimate paragraph in the critical evaluation, and an
          undocumented one is a missing requirement.
          THEN write tools\Set-Env.ps1 per D-030.
          THEN open the issue for REQ-F-005 and REQ-F-006 together - the verification
          view is what makes REQ-F-006 a behaviour rather than a property of the signing
          module - and build the public verification page answering VERIFIED, NOT FOUND
          or TAMPERED.

Opening prompt (D-017, `docs/HANDOVER.md` Section 1.5) - for session 010:

```
Session 010. Sprint B.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any edit.

Token: QVS-S009-A2B-fcca63f

Work happens on the corporate machine at
C:\Users\tmachimbira\Projects\Development\qvs, alongside TaCRAS.

DO NOT install Docker Desktop, WSL or any hypervisor component on this machine.
Not for verification, not for a quick check. Under D-026 the image is built and
run on a CI runner or not at all.

To reconcile at Section 0.5:
  1. Expect HEAD above fcca63f, which was PR #13's squash-merge. Session 009 closed
     with docs-only commits stacked on it: 9892a87 wrote the close block, and at least
     one further commit amended the Next line. Do not chase an exact count or an exact
     sha - any HEAD on develop whose commits above fcca63f are all docs commits is the
     shape Section 1.3 describes. A code commit above fcca63f would NOT be, and is
     worth stopping for.
  2. Two session 006 decisions - the REQ-N-003 configuration reading and the
     WhiteNoise choice - still exist only on feature/REQ-N-003-docker-deployment and
     are deliberately uncited by number on develop. Do not number them before merge.
  3. main is still at 06ab3dc and still unprotected.
  4. REQ-F-006 carries four tests and a status of OPEN. That is deliberate and
     explained in session 009's block. Do not "fix" it by changing the status.

Already run:  PR #13 squash-merged to develop as fcca63f - Qualification model,
              first migration, register view behind login, login and logout routes,
              four templates, 24 tests. Suite 41 passing at 96.32%. CI green twice.
              REQ-F-003 and REQ-F-004 at VERIFIED on browser evidence. Root now
              redirects to the register view; it used to answer 404. D-029 and D-030
              registered.
Not yet run:  tools\Set-Env.ps1 - D-030 registers the decision, not the script.
              Anything Docker, anywhere. The CI job D-028 requires before the Docker
              branch's PR can open. tools/traceability.py. main has never been
              protected and there is no release PR.

Next action, in this order:
  1. Protect main and open a release PR from develop. Do this FIRST. It has been
     outstanding since session 005 and has been read as background every session
     because it has never been an instruction. It is the direct evidence for
     REQ-N-001, which cannot leave OPEN until a merge to main is demonstrably
     gated. If branch protection turns out to be unavailable for this repository's
     visibility and plan, record that constraint explicitly rather than quietly
     working around it - a documented inability is a paragraph in the critical
     evaluation, an undocumented one is a missing requirement.
  2. Write tools\Set-Env.ps1 per D-030.
  3. Open the issue for REQ-F-005 and REQ-F-006 together and build the public
     verification page - certificate ID in, VERIFIED, NOT FOUND or TAMPERED out.

Two hazards session 009 hit, both silent:
  - registrar_client IS the client fixture with force_login called on it. A test
    asking for both gets one object and its "anonymous" request arrives
    authenticated. Build a fresh django.test.Client() instead. REQ-F-005's public
    tests are exactly the shape that walks into this.
  - A fresh terminal inherits no environment variables and twelve tests fail on
    ImproperlyConfigured. That is D-003 working, not a defect.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages and gh bodies via file with -F or --body-file, deleted afterwards (D-020,
D-024). Run the suite with QVS_DEBUG=0 and both throwaway keys set explicitly.
Use curl.exe with --max-time for any download; Invoke-WebRequest hangs on this
profile.

Give me commands in separate labelled blocks, one command per block.
```

## Session 010 - ACCOUNT HANDOVER - AccountA -> AccountB - 2026-09-11 23:35
Token   : QVS-S010-A2B-61b5d1c
Sprint  : B
Branch  : develop
Done    :
  - main protected for the first time since the repository was created. Classic
    branch protection applied by API from dev_reports/branch_protection.json rather
    than by hand: required check "Lint, security and tests" bound to GitHub Actions
    app id 15368 and strict; pull request required with 0 approvals; enforce_admins
    on; force pushes and branch deletion refused; conversation resolution required;
    linear history off.
  - D-031 registered, covering the mechanism, the zero-approval reasoning and the
    linear-history call.
  - PR #14 opened from develop and merged to main as 1253dd6 - a real merge commit
    with parents 06ab3dc and bafa013 - having passed the required check. The first
    merge main has ever received.
  - REQ-N-001 moved OPEN -> VERIFIED, browser-confirmed on the merged PR showing the
    check as required and on the branch protection settings page.
  - tools/Set-Env.ps1 written, delivering D-030. Loads .env into the current
    PowerShell session only, prints names and never values, splits each line on the
    first '=' so a key containing one is not truncated.
  - PR #15 opened and squash-merged to develop as 61b5d1c, CI green.
  - Suite 41 passing at 96.32% on the corporate machine after a reboot, with the
    environment supplied by Set-Env.ps1 rather than by hand.
HEAD    : 61b5d1cae2502b3c1c844427b03a692fbd8b19b6  PUSHED
Tree    : clean
Issues  : PR #14 merged to main, PR #15 merged to develop. No GitHub issue was
          opened this session and the issue list was never queried. The issue
          covering REQ-F-005 and REQ-F-006 remains unopened.
Open    :
  - Nothing half-finished. Both units of work reached a merged PR.
  - REQ-F-005 and REQ-F-006 not started: no issue, no branch, no code.
Decided :
  - D-031, registered.
  - Taken inline, not registered: feature and chore branches squash into develop so
    its history reads one commit per unit of work, and develop merges into main so
    main inherits the full history. PR #15 squashed, PR #14 merged, deliberately.
  - Taken inline: merged branches are not deleted. Branch history is assessed.
Watch   :
  - D-025's log currency check produced its second false positive. It counts commits
    above the newest logged HEAD and calls two or more STALE, which assumes a close
    is exactly one commit. Session 009 closed and then amended its block twice, so a
    correctly logged repository read STALE. Session 010's opening prompt anticipated
    it in prose. That is twice now, and it is worth a decision rather than a third
    prose warning.
  - gh pr merge returns exit 0 with no output through Invoke-Logged.ps1. Do not read
    the silence as failure, and do not read exit 0 as proof the merge happened.
    Confirm with git log --oneline --parents on the target branch.
  - gh pr view has no "merged" field; state and mergedAt carry it. Asking for it
    fails the whole command with exit 1.
  - .env holds five variables, not the three D-030's context claims: QVS_DEBUG,
    QVS_SECRET_KEY, QVS_SIGNING_KEY, QVS_ALLOWED_HOSTS, QVS_DATABASE_PATH. The
    decision is unaffected; the sentence is wrong and was left uncorrected pending
    Sir Ton's word.
  - Green CI runs carry annotations_count 1. Never examined. Most likely an action
    deprecation notice, which stops being cosmetic when the action version retires.
  - enforce_admins is on, so main cannot be pushed to directly by anyone, including
    the owner. Changes arrive by pull request or not at all.
  - Carried from session 009 and still live: registrar_client IS the client fixture
    with force_login called on it. A test asking for both gets one object and its
    "anonymous" request arrives authenticated. Build a fresh django.test.Client().
    REQ-F-005's public tests are exactly the shape that walks into this.
Next    : Open one GitHub issue covering REQ-F-005 and REQ-F-006 together, branch
          feature/REQ-F-005-public-verification off develop, and build the public
          verification page - certificate ID in, VERIFIED, NOT FOUND or TAMPERED out.
Opening prompt :
```
Session 011. Sprint B.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any edit.

Token: QVS-S010-A2B-61b5d1c

Work happens on the corporate machine at
C:\Users\tmachimbira\Projects\Development\qvs, alongside TaCRAS.

DO NOT install Docker Desktop, WSL or any hypervisor component on this machine.
Not for verification, not for a quick check. Under D-026 the image is built and
run on a CI runner or not at all.

Run .\tools\Set-Env.ps1 before anything that touches Django. A fresh terminal has
no environment variables and twelve tests fail on ImproperlyConfigured. The script
is new as of session 010 - it did not exist before, so do not conclude from an older
block that the environment must be set by hand.

To reconcile at Section 0.5:
  1. Expect HEAD one commit above 61b5d1c, that commit being session 010's close
     block. That is the Section 1.3 shape. If further docs commits were stacked on
     it the census will read STALE - check that every commit above 61b5d1c is a docs
     commit. A code commit above it would not be the expected shape and is worth
     stopping for.
  2. main is at 1253dd6 and is now PROTECTED. It is no longer the unprotected
     background every session has read it as. Nothing can be pushed to it directly,
     including by the owner, and REQ-N-001 is VERIFIED rather than OPEN.
  3. Two session 006 decisions - the REQ-N-003 configuration reading and the
     WhiteNoise choice - still exist only on feature/REQ-N-003-docker-deployment and
     are deliberately uncited by number on develop. Do not number them before merge.
  4. REQ-F-006 carries four tests and a status of OPEN. That is deliberate and
     explained in session 009's block. Do not "fix" it by changing the status.
  5. Merged branches are not deleted. origin/feature/REQ-F-003-register-qualification
     and origin/chore/D-030-set-env are both intact on purpose, not stale refs.

Already run:  main protected under D-031. PR #14 merged develop to main as 1253dd6,
              a merge commit with two parents, through the required check. REQ-N-001
              at VERIFIED. tools/Set-Env.ps1 written and merged by PR #15, squashed
              to develop as 61b5d1c. Suite 41 passing at 96.32% after a reboot.
Not yet run:  Anything Docker, anywhere. The CI job D-028 requires before the Docker
              branch's PR can open. tools/traceability.py. No issue has ever been
              opened for REQ-F-005 or REQ-F-006, and the issue list has never been
              queried.

Next action, in this order:
  1. Open one GitHub issue covering REQ-F-005 and REQ-F-006 together. They are one
     page and one test file; two issues would split the evidence.
  2. Branch feature/REQ-F-005-public-verification off develop.
  3. Build the public verification page - certificate ID in, VERIFIED, NOT FOUND or
     TAMPERED out - with tests, then browser-verify before either requirement moves
     past BUILT. A green suite is not a verified page (CLAUDE.md Section 5).

Hazards, all silent:
  - registrar_client IS the client fixture with force_login called on it. A test
    asking for both gets one object and its "anonymous" request arrives
    authenticated. Build a fresh django.test.Client() instead. REQ-F-005's public
    tests are exactly the shape that walks into this.
  - gh pr merge returns exit 0 and prints nothing. Confirm every merge with
    git log --oneline --parents on the target branch, never by exit code alone.
  - gh pr view has no "merged" field. Asking for it fails the whole command.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages and gh bodies via file with -F or --body-file, deleted afterwards (D-020,
D-024). Run .\tools\Set-Env.ps1, then QVS_DEBUG=0 for the suite.
Use curl.exe with --max-time for any download; Invoke-WebRequest hangs on this
profile.

Give me commands in separate labelled blocks, one command per block.
```

---

## Session 011 - ACCOUNT HANDOVER - AccountA -> AccountB - 2026-09-12 11:45
Token   : QVS-S011-A2B-604e157
Sprint  : B
Branch  : develop
Done    :
  - Issue list queried for the first time in eleven sessions. It found that no PR
    had ever carried a Closes reference, so five issues stood open describing work
    that was merged and shipped. #1, #3, #11 and #12 closed with comments citing the
    decision or merge commit that delivered each, and saying the closure was
    retrospective rather than pretending the link had always been there.
  - Issue #16 opened covering REQ-F-005 and REQ-F-006 together.
  - feature/REQ-F-005-public-verification branched off develop at bbecea1.
  - qualifications/verification.py written: the three-outcome decision, outside the
    view, answerable without a request cycle.
  - The public verification page built, with its template and 14 tests.
  - The root redirect repointed from register to verify, folded into this branch on
    Sir Ton's word rather than left for later. test_routing.py rewritten to match.
  - REQ-F-005 and REQ-F-006 browser-verified and moved OPEN -> VERIFIED.
  - PR #17 opened, CI green in 30s, squash-merged to develop as 604e157. Confirmed
    by git log --oneline --parents, not by exit code. Issue #16 closed by the
    commit message - the first Closes reference this repository has ever carried.
  - Suite 55 passing at 97.04%, up from 41 at 96.32%. verification.py and views.py
    both at 100% with branch coverage.
HEAD    : 604e1576138a084250925205dccdf9d7c6ce743e  PUSHED
Tree    : clean
Issues  : #1, #3, #11, #12 closed retrospectively. #16 opened and closed by PR #17.
          #8 (REQ-N-003 docker) and #9 (REQ-F-001, REQ-F-002) remain open, both on
          purpose. Next issue number will be #18.
Open    :
  - Nothing half-finished. The unit of work reached a merged PR.
  - Issue #9 held open deliberately, pending a decision recorded under Watch.
  - REQ-F-007 and REQ-F-008 not started. The verification view is where the audit
    hook lands, and it was fenced out in writing in issue #16, in the module
    docstring and in the PR body, so the exclusion is argued rather than forgotten.
Decided :
  - Nothing registered. Everything below was taken inline.
  - A tampered result carries no record. VerificationResult attaches the
    qualification only on VERIFIED, so the template cannot render fields the system
    has just refused to vouch for. Enforced by the data, not by discipline.
  - All three outcomes return 200. A 404 for NOT FOUND would claim the verification
    page does not exist and would let an automated caller sort real IDs from
    invented ones by status code alone.
  - Certificate IDs are uppercased and stripped of whitespace, but look-alike
    characters are NOT repaired. signing.py excludes 0 and 1 as well as O and I, so
    there is no correct target to fold onto, and silently verifying the wrong record
    is worse than a NOT FOUND on a typo. A test asserts this stays un-fixed.
  - Verification is GET, not POST. It reads and changes nothing, so the result is
    shareable and needs no CSRF token on a page anonymous users must reach. Worth
    revisiting when REQ-F-007 makes it write.
  - The routing tests stay unmarked by requirement even though the root now points
    at verification. Marking them would let the traceability matrix count a URL
    configuration as evidence of verification capability.
  - One commit, not two. The redirect touches the same urls.py region as the new
    route; splitting cleanly would have meant staging by hunk and reverting
    test_routing.py for the first commit, risking an intermediate commit whose
    suite is red.
  - The first two are the strongest candidates for registration as numbered
    decisions. Left unnumbered pending Sir Ton's word.
Watch   :
  - REQ-F-002 is browser-verified in everything but the register entry. A
    certificate was minted at 10:09, its signature recomputed and matched at 10:10,
    and the same record rejected at 10:20 after one column changed. Promoting it to
    VERIFIED and closing issue #9 citing both requirements is the recommendation.
    REQ-F-001 should stay at BUILT: a browser saw one well-formed ID used as a
    lookup key, and no amount of clicking demonstrates uniqueness or
    non-guessability. Not done, because it is a status change outside the branch's
    scope and it waits on Sir Ton.
  - gh output reaches Invoke-Logged artefacts with its success glyph mangled to
    "???" - PowerShell 5.1 decoding UTF-8 as ANSI, the same phenomenon as D-018 but
    in tool output rather than repository text. Harmless while dev_reports is
    gitignored. It stops being harmless the moment a gh artefact is copied into
    docs/evidence, where Check-Ascii.ps1 will reject it. Sprint D assembles that
    folder.
  - D-025's log currency check behaved correctly this session - one commit above
    the logged HEAD, verdict current. The false positive needs two or more stacked
    commits, so session 010's second occurrence remains the live case and the
    decision it deserves is still unwritten.
  - gh pr merge again returned exit 0 with no output. Confirmed live this session.
  - Filesystem:edit_file matches the FIRST occurrence of its anchor text, silently.
    Session 011's close block was written once against an anchor that ends every
    session's opening prompt and landed between sessions 001 and 002. Caught from
    the returned diff's trailing context, removed and rewritten against text unique
    to session 010. Anchor on a token line or a sha, never on boilerplate.
  - .env holds five variables, not the three D-030's context claims. Carried
    uncorrected, still pending Sir Ton's word.
  - Green CI runs carry annotations_count 1. Still never examined.
  - registrar_client IS the client fixture with force_login applied. Still live, and
    tests/test_verification.py was written specifically around it - every client in
    that module is a fresh django.test.Client(). The next module with public tests
    must do the same.
  - GET /favicon.ico returns 404 on every page load. Cosmetic, but it will appear
    in the demonstration video if the server terminal is screen-recorded.
  - The direction letters in a token record intent, not fact. Session 010 wrote A2B
    and session 011 then ran on AccountA. The sha7 is what reconciles; the letters
    do not.
Next    : Decide REQ-F-002 and issue #9, then build REQ-F-007 and REQ-F-008 - the
          audit event on every verification attempt, append-only. The hook lands in
          the verification view. tools/traceability.py is the other unbuilt piece
          the assignment's verification deliverable depends on.
Opening prompt :
```
Session 012. Sprint B.
Closing session ran on: AccountA. State at Section 0.6 which account you are
actually on - it may not be the one this prompt expects. The direction letters in
the token record intent, not fact.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full - probe the connector, have me run
.\tools\Session-Open.ps1 and read the artefact yourself, reconcile it against the
last SESSION_LOG block, and state the Section 0.6 opening position before any edit.

Token: QVS-S011-A2B-604e157

Work happens on the corporate machine at
C:\Users\tmachimbira\Projects\Development\qvs, alongside TaCRAS.

DO NOT install Docker Desktop, WSL or any hypervisor component on this machine.
Not for verification, not for a quick check. Under D-026 the image is built and
run on a CI runner or not at all.

Run .\tools\Set-Env.ps1 before anything that touches Django. A fresh terminal has
no environment variables and twelve tests fail on ImproperlyConfigured. Note that
QVS_DEBUG=0 set for a pytest run persists for the life of that shell - starting
runserver in the same terminal runs with DEBUG off, and WhiteNoise is still
unmerged.

To reconcile at Section 0.5:
  1. Expect HEAD one commit above 604e157, that commit being session 011's close
     block. That is the Section 1.3 shape. A code commit above it would not be the
     expected shape and is worth stopping for.
  2. main is at 1253dd6 and is PROTECTED. Nothing can be pushed to it directly,
     including by the owner. develop has moved four commits past it and main has
     not received a merge since PR #14.
  3. Two session 006 decisions - the REQ-N-003 configuration reading and the
     WhiteNoise choice - still exist only on feature/REQ-N-003-docker-deployment and
     are deliberately uncited by number on develop. Do not number them before merge.
  4. REQ-F-001 is BUILT and REQ-F-002 is BUILT, and issue #9 covering both is open
     on purpose. Session 011 recommends promoting REQ-F-002 to VERIFIED and leaving
     REQ-F-001 at BUILT. That decision has not been taken. Do not take it silently.
  5. Merged branches are not deleted. origin/feature/REQ-F-005-public-verification,
     origin/feature/REQ-F-003-register-qualification and origin/chore/D-030-set-env
     are all intact on purpose, not stale refs.

Already run:  Issue list queried and four stale issues closed. Issue #16 opened and
              closed by PR #17, which squash-merged to develop as 604e157 through a
              green required check. REQ-F-005 and REQ-F-006 browser-verified and at
              VERIFIED. The root now redirects to /verify/. Suite 55 passing at
              97.04%.
Not yet run:  Anything Docker, anywhere. The CI job D-028 requires before the Docker
              branch's PR can open. tools/traceability.py. REQ-F-007 and REQ-F-008.
              No issue has been opened for the audit requirements.

Next action, in this order:
  1. Settle REQ-F-002 and issue #9. One decision, then a status line and a close.
  2. Open one issue covering REQ-F-007 and REQ-F-008 - the audit event and its
     append-only guarantee. They are one model and one migration.
  3. Build them. The hook lands in qualifications/views.py verify(), which is
     currently a pure read; adding the write changes that, and the GET-not-POST
     reasoning recorded in session 011 is worth re-reading before it does.

Hazards, all silent:
  - registrar_client IS the client fixture with force_login called on it. A test
    asking for both gets one object and its "anonymous" request arrives
    authenticated. Build a fresh django.test.Client() instead. Every client in
    tests/test_verification.py already does; match it.
  - gh pr merge returns exit 0 and prints nothing. Confirm every merge with
    git log --oneline --parents on the target branch, never by exit code alone.
  - gh pr view has no "merged" field. Asking for it fails the whole command.
  - Filesystem:edit_file matches the FIRST occurrence of its anchor, silently. Never
    anchor on text that repeats across session blocks; use a token line or a sha.
  - gh output reaches artefacts with non-ASCII glyphs mangled to "???". Harmless in
    gitignored dev_reports, rejected by Check-Ascii.ps1 if copied into docs/evidence.
  - PRs did not carry Closes references before #17. If an issue looks stale, query
    the list rather than assuming the work is unfinished.

Every git and gh command goes through .\tools\Invoke-Logged.ps1 (D-022). Commit
messages and gh bodies via file with -F or --body-file, deleted afterwards (D-020,
D-024). Run .\tools\Set-Env.ps1, then QVS_DEBUG=0 for the suite.
Use curl.exe with --max-time for any download; Invoke-WebRequest hangs on this
profile.

Give me commands in separate labelled blocks, one command per block.
```
