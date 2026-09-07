# CLAUDE.md - QVS working agreement

Read automatically by Claude Code at session start, and read manually by Claude
Desktop as step 1 of the session-open sequence in `docs/HANDOVER.md`.

This file holds what is true **across every session and both accounts**. It is the
one place those facts live. If something here contradicts a chat message, this file
is wrong and should be corrected here, not worked around.

---

## 1. What this project is

QVS is a Qualification Verification System built for **MIM736**, a Master's practical
assignment. It is a school deliverable on a short deadline, not a production system.

Assessment weighting, which drives every prioritisation call:

| Deliverable | Weight |
|---|---|
| Git repository (history, issues, PRs, CI config) | 20% |
| Working software system | 25% |
| Technical report, 3,000-4,000 words | 25% |
| Demonstration video, 10-15 min | 15% |
| Individual contribution report | 15% |

**75% of the marks need no new features.** When time is short, features are cut
before evidence, documentation or the report. The final third of the calendar is
reserved for Sprint D and is not available for code.

Functional brief, in full: register qualifications; search and retrieve records;
verify authenticity; maintain an auditable history of verification activity.

---

## 2. Environment

| Fact | Value |
|---|---|
| Repo root | `C:\Users\Tonderai Machimbira\Projects\Development\Qualification Verification System` |
| Machine | ELITEBOOK-0001, personal, private network |
| OS / shell | Windows 11, **PowerShell 5.1**, VS Code integrated terminal |
| Python | **3.12.10**, the only interpreter registered |
| Git | 2.55.0.windows.3 |
| GitHub CLI | gh 2.100.0 |
| Docker | 29.7.2 (Docker Desktop) |
| Claude Code | 2.1.263, native install at `~\.local\bin\claude.exe` |
| Execution policy | CurrentUser = RemoteSigned |
| Dev server port | **8020** |

**There is no corporate network here.** No proxy, no certificate store issues, no push
restriction. Do not carry any of that reasoning over from the TaCRAS project. If
`git push` ever fails on this machine it is an ordinary problem, diagnosed normally.

PowerShell 5.1 constraints: no `&&` chaining, multi-line logic goes in a script under
`tools\`, and paths containing spaces must be quoted.

---

## 3. Python - the one rule

**Every Python invocation goes through `.\.venv\Scripts\python.exe`. Without
exception.**

```powershell
.\.venv\Scripts\python.exe manage.py runserver 8020
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\pip.exe install django
```

Never `python`, never `py manage.py`, never an activated-shell assumption. Reasons:

- `C:\Users\...\AppData\Local\Microsoft\WindowsApps\python.exe` is a Microsoft Store
  alias stub that prints an advert instead of running. An unqualified `python` can
  reach it.
- Activation depends on execution policy and on the shell remembering state. An
  explicit interpreter path depends on nothing.
- It removes "which interpreter am I on" as a question that can ever be asked.

`py` is used exactly once, to create the virtual environment, and never again.

---

## 4. Running commands

**Every command whose output Claude needs goes through `Invoke-Logged.ps1`:**

```powershell
.\tools\Invoke-Logged.ps1 '<command>' '<artefact_name>'
```

It writes `dev_reports\<artefact_name>.txt`, which Claude opens directly. Add `-Echo`
only when you want to watch a long install progress live.

### The rules around it

- **Claude never asks for pasted terminal output.** The output is on disk. Asking for
  it is a defect in method, not a limitation of tooling. The same applies to any file
  Claude can open - never ask for it to be described, quoted or uploaded.
- **Read before asking, and read before re-issuing.** If a command sequence was
  handed over, assume it ran and look in `dev_reports\` before asking for a repeat.
- **Every `tools\` script prints exactly two lines**: a one-line verdict and the
  artefact path. Everything else goes to the file. A script that floods the terminal
  is a script to fix.
- **Commands are given in separate labelled blocks**, one command per block, never
  stacked into a single paste.
- **Provenance on every claim.** Read it, ran it, inferred it, or were told it. "The
  coverage artefact shows 74%" is honest; asserting 74% without opening the file is
  not.
- `dev_reports\` is gitignored. Artefacts are working evidence, not deliverables.
  Anything that belongs in the submission is copied to `docs/evidence/`.

---

## 5. Code delivery

- **Complete files, never partial patches or diffs.**
- **Line 1 is a comment giving the file's path** relative to the repo root.
- **Comments explain why, not what.** The report is assembled from this reasoning.
- Line endings: **LF everywhere**, enforced by `.gitattributes` (`* text=auto eol=lf`).
  There is no PowerShell exception - PowerShell 5.1 reads LF scripts without
  complaint, and a single rule cannot drift out of sync with itself.
- Characters: **ASCII only**, enforced by `tools\Check-Ascii.ps1` (D-018). Write
  "Section 3", not a section sign; a hyphen, not an em dash; straight quotes. Same
  rule as line endings and for the same reason - PowerShell 5.1 reads a UTF-8 file
  with no byte order mark as ANSI, so one non-ASCII character corrupts every artefact
  it reaches and every string comparison that touches it.
- After a change, always state whether it needs a **hard refresh (Ctrl+Shift+R)** or
  a **server restart**. Template or Python means restart; static asset means refresh.
- **Browser-verify before calling a page done.** A green test suite is not a verified
  page.

---

## 6. Git conventions

- `main` protected. `develop` is the integration branch. Work on
  `feature/REQ-F-00X-name`, or `fix/`, `ci/`, `docs/`, `test/`.
- Conventional Commits: `feat:`, `fix:`, `test:`, `ci:`, `docs:`, `refactor:`,
  `chore:`. Subject under 72 characters, imperative. Body cites the requirement it
  serves: `Implements REQ-F-005.`
- **`git add` uses explicit paths. Never `git add .`.**
- Every requirement gets an issue before it gets a branch; every PR closes its issue
  with `Closes #n` and carries a self-review comment. `gh` is installed so this costs
  two commands, not a browser round trip.
- Meaningful commit history is an explicit assessment criterion. A wall of `wip`
  costs real marks.
- **Commit messages are written to a file, used, then deleted.** Claude writes the
  message to `dev_reports\commit_message.txt`, the commit is made with
  `git commit -F dev_reports\commit_message.txt`, and the file is removed by an
  explicit PowerShell command in the same sequence. Never `-m` for a message carrying
  a body. See D-020.

---

## 7. How Claude and Sir Ton work together

- **Lead with the answer, then the reasoning.** Direct and technically fluent.
- **Push back before implementing**, not after. Prefer a targeted fix to an
  exhaustive diagnostic.
- Where there is a real design choice, present it with a recommendation and the
  trade-off, and **stop for a decision** rather than picking silently.
- "go" means proceed with the plan as reviewed. "Go with your recommendations" means
  make the call and report what was decided and why.
- Small decisions may be taken inline, with the rationale stated afterwards and a
  veto left open.
- **Time is the scarce resource, not correctness.** Given a thorough path and a path
  that reaches a demonstrable state today, take the second and record the trade-off
  in `docs/DECISIONS.md`. That record is report material.
- **Errors are disclosed at the point they are found**, not absorbed. A defect in
  Claude's own method is stated plainly and fixed.
- Overview first, depth on demand.

### Division of labour

Claude Desktop plans, reviews, decides, writes prose, and reads artefacts through the
Filesystem connector. **Claude Desktop is also the default writer.** It writes files
into the repository directly through the connector, so the agent that reasoned about a
file is the agent that wrote it - no translation step, and no second-hand report to
trust.

Claude Code is used where a second agent pays for itself: bulk or repetitive edits
across many files, long command sequences, and `gh` operations. Prompts to Claude Code
are self-contained: full path, full file content, explicit success criterion.

**Whoever writes, Claude Desktop reads the file back through the connector before it
counts as done.** Claude Code's own report is not evidence, and neither is a write
call that returned successfully - the file on disk is. See D-019.

---

## 8. Scope fence

Not in this project. Not "later" - not at all, unless Sprint D is complete:

Blockchain. A REST API separate from the server-rendered views. Any JavaScript
framework. PostgreSQL or MySQL. Celery or async workers. Document upload or OCR.
Email notification. Multi-tenancy. Role hierarchies beyond `is_staff`. Agentic AI.
Kubernetes. Any styled UI beyond legible browser defaults.

If one of these is proposed mid-build, the answer is a sentence in the report's
critical evaluation explaining why it was scoped out. That sentence earns more than
the half-built feature.

**Also fenced: TaCRAS governance machinery.** No findings register, no workstream
claims file, no prediction scorecard, no session-open census ritual beyond the one in
`docs/HANDOVER.md`. This project is small, short and serial. That apparatus would cost
more than it protects.

---

## 9. Document map

| File | Holds |
|---|---|
| `CLAUDE.md` | This file. Cross-session, cross-account working agreement. |
| `docs/HANDOVER.md` | Session open and close protocol. Canonical for Section 0. |
| `docs/SESSION_LOG.md` | The running record. Appended, never rewritten. |
| `docs/REQUIREMENTS.md` | REQ-F / REQ-N register with tiers. |
| `docs/DECISIONS.md` | Numbered decisions. Source for the report. |
| `docs/evidence/` | Submission evidence: pipeline runs, coverage, traceability. |
| `dev_reports/` | Gitignored working artefacts Claude reads. |

One fact, one home. Where a rule lives in `docs/HANDOVER.md`, this file points at it
rather than restating it - two copies of a rule is how one of them goes stale.

---

## 10. Keeping documents current

A governance document that has silently fallen behind the repository is worse than no
document, because it is trusted. Recovering a current position from a stale one is
expensive, and it is the single most avoidable way this project loses time.

### The rule

**A document is updated in the same session as the change it describes - not later,
not in a cleanup pass.** Specifically:

| When this changes | Update this, that session |
|---|---|
| A tool version, path, port or environment fact | `CLAUDE.md` Section 2 |
| A design or process choice is made | `docs/DECISIONS.md`, next free D-number |
| A requirement is added, deferred or reworded | `docs/REQUIREMENTS.md` |
| Anything at all happens in a session | `docs/SESSION_LOG.md`, at close |
| A new document is created | `CLAUDE.md` Section 9 document map |

### The mechanism

Discipline alone is what failed on TaCRAS, so the rule is backed by a command:

```powershell
.\tools\Check-Docs.ps1
```

It is read-only and reports drift in four families:

- **Version drift** - every tool version and path asserted in Section 2 above, checked
  against the machine. If Python, git, gh, docker, Claude Code or the repo root has
  moved and this file has not, it fails.
- **Document map** - every file listed in Section 9 exists, and every `.md` in `docs\` is
  listed in Section 9. A document nobody listed is a document nobody maintains.
- **Log currency** - compares the newest date in `docs/SESSION_LOG.md` against the
  newest commit date. **Commits newer than the newest log block means the log is
  stale**, and it reports by how many days. This is the check that matters most.
- **Decision references** - every `D-nnn` cited anywhere must exist in
  `docs/DECISIONS.md`. A decision cited but unregistered cannot be found when the
  report is written.

### When it runs

**Before every commit, without exception.** It costs seconds. A `STALE` verdict is
fixed before the commit is made, never noted and deferred - a deferred staleness fix
is how the backlog starts.

It also runs as part of the local gate (`tools\Check.ps1`) once that exists, so it
cannot be forgotten.

### What it cannot check

Prose. It verifies that facts match and that documents exist and are mapped; it
cannot tell whether a paragraph still describes how the project actually works. That
remains a judgement call, made at session close, and it is the reason the session log
carries a `Decided` field - a decision written down at the moment it is taken never
needs reconstructing.
