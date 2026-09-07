# HANDOVER.md - QVS session protocol

Canonical for how a session opens, how it closes, and how work passes between the
two Claude accounts. `CLAUDE.md` holds the working agreement; this file holds the
ritual around it.

Deliberately short. The whole protocol is one running log file, one open sequence and
one close block.

---

## Section 0 Session open

Run in order. Nothing is edited, written or committed before Section 0.6.

### Section 0.1 Read the standing documents

1. `CLAUDE.md` - the working agreement.
2. `docs/HANDOVER.md` - this file.
3. `docs/DECISIONS.md` - settled decisions, read **before** open work, so a closed
   question is not reopened.
4. `docs/REQUIREMENTS.md` - what done means, and the tier order for triage.

### Section 0.2 Read the last block of the log

`docs/SESSION_LOG.md`, last block only. It names the sprint, the branch, the HEAD it
left behind, and the next action.

### Section 0.3 Probe the connector

`list_directory` on the repo root. Instant return means the connector is live. A hang
is information, not a reason to retry - say so and stop.

### Section 0.4 Derive the state - do not trust the log

The last block is a **claim**. Verify it before repeating it. One command does the
whole census:

```powershell
.\tools\Session-Open.ps1
```

It writes `dev_reports\session_open.txt`, which Claude reads. It reports HEAD read
directly from `.git\refs`, the current branch, the working tree, whether the venv
exists and which Python it holds, and the tail of the session log.

**HEAD is confirmed by reading the refs file, never by trusting a summary.**

### Section 0.5 Reconcile

Compare what Section 0.4 derived against what Section 0.2 claimed. State any divergence explicitly
before doing anything else. In particular:

- **A dirty working tree at session open means the other account is mid-session.**
  Stop. Say so. Do not proceed and do not clean the tree.
- **HEAD ahead of the last logged HEAD** means work happened that was never logged.
  Stop and reconcile before building on it.

### Section 0.6 State the opening position

Before the first edit, say in one short block:

```
Account   : AccountA | AccountB
Session   : NNN
Sprint    : A | B1..B5 | C | D
Branch    : <branch>
HEAD      : <sha7>  [verified from .git\refs]
Tree      : clean | dirty
Next      : <the single next action>
```

Only then begin work.

---

## Section 1 Session close

Every session ends with a block appended to `docs/SESSION_LOG.md`, whether or not
anything shipped. Two shapes, depending on what happens next.

### Section 1.1 The two rules that make handover work

1. **A session ends committed and pushed.** There is no corporate network here and
   therefore no reason for an unpushed commit. A dirty tree handed to another account
   is how two accounts destroy each other's work.
2. **Never both accounts at once.** They alternate. If a session opens onto a dirty
   tree or an unlogged HEAD, the other account is still working.

### Section 1.2 SESSION CLOSE - same account continues

Four fields. Used when the same account will pick this up next.

```
## Session NNN - CLOSE - AccountA - YYYY-MM-DD HH:MM
Sprint  : B2
Branch  : feature/REQ-F-003-register-form
Done    :
  - <one line per completed thing>
HEAD    : <full sha>  PUSHED
Tree    : clean
Next    : <one sentence, specific enough to start from cold>
```

### Section 1.3 ACCOUNT HANDOVER - the other account picks up

Everything above, plus the context the receiving account cannot derive from the repo.
Used whenever the next session runs on the other account.

```
## Session NNN - ACCOUNT HANDOVER - AccountA -> AccountB - YYYY-MM-DD HH:MM
Token   : QVS-SNNN-A2B-<sha7>
Sprint  : B2
Branch  : feature/REQ-F-003-register-form
Done    :
  - <one line per completed thing>
HEAD    : <full sha>  PUSHED
Tree    : clean
Issues  : #7 open, #8 closed
Open    :
  - <anything half-finished, and exactly how far it got>
Decided :
  - <decisions taken this session, and the D-number if registered>
Watch   :
  - <anything that bit this session and could bite again>
Next    : <one sentence, specific enough to start from cold>
```

**The token** is `QVS-S<NNN>-A2B|B2A-<sha7>`. The receiving session quotes it in its
Section 0.6 opening block. Its only job is to prove the receiving session read the
right block and is standing on the right commit - a mismatched token means the log
and the repo have diverged.

**Which sha7.** The commit the session's work left behind - the last substantive
commit, not the session-close commit that carries this block. The two cannot be the
same: the token lives inside the block, so committing the block would change the sha
the token names. A receiving session therefore expects the census to show HEAD **one
commit ahead** of the token, and that commit to be the close commit itself. HEAD more
than one commit ahead, or one commit ahead of something other than a close commit, is
the Section 0.5 stop condition.

**Before the first commit** the token carries `NOHEAD` in place of the sha7. Two
sessions closed in that state and both were correct to. It is not a mismatch, and the
receiving session should not treat it as one.

### Section 1.4 Appending

`docs/SESSION_LOG.md` is **appended to, never rewritten**. Blocks accumulate in
chronological order, newest last. The file is tracked in git, so it survives a fresh
clone and doubles as raw material for the individual contribution report - which is
15% of the marks and is written from exactly this kind of record.

### Section 1.5 The opening prompt for the next session

**Every session close produces the opening prompt for the next session.** It is
written by Claude, not by Sir Ton, and it is the last thing produced before the chat
ends.

The reason is that at session close Claude holds context that exists nowhere else:
what was half-finished and how far it got, what turned out to be a dead end, which
claim is unverified and why, and what the single next action actually is. A prompt
written from inside that context starts the next session already oriented. A prompt
written by Sir Ton from outside it cannot carry the same information, and asking him
to reconstruct it is asking him to do work Claude is better placed to do.

#### Where it goes

**Both places, every time:**

1. **In the session log block**, as a fenced code block under an `Opening prompt`
   field. This is the durable copy. It is tracked in git, so it survives a fresh
   clone and reaches the other account without depending on a chat being findable.
2. **Directly in chat**, at session close, as a copy-pasteable block. A prompt that
   exists only inside a document is a prompt Sir Ton has to go and extract, and the
   whole point is that the next session starts with one paste.

#### What it must contain

- **Session number and account** for the session being opened, not the one closing.
- **An instruction to read the repository documents and run Section 0 in full.** The prompt
  never substitutes for the protocol - it points at it.
- **Anything Section 0.5 must reconcile**, named explicitly: unverified claims, expected-but
  unusual repository states, anything that would otherwise look like a problem.
- **The single next action**, specific enough to start from cold.
- **What has and has not already been run**, so the receiving session does not
  re-issue commands that were already executed.
- **Nothing that contradicts `CLAUDE.md` or this file.** Where they differ, they win,
  and the prompt should say so.

#### Template

```
Session NNN, AccountA | AccountB. Sprint X.

Read the repository documents in the order given in the project instructions
before replying. CLAUDE.md and docs/HANDOVER.md are canonical; nothing in this
message overrides them.

Then run HANDOVER.md Section 0 in full, ending with the Section 0.6 opening position.

[For an account handover only:]
Token: QVS-SNNN-A2B-<sha7>

To reconcile at Section 0.5:
  1. <unverified claim, and how to verify it>
  2. <expected-but-unusual state, and why it is not a problem>

Already run:  <what not to re-issue>
Not yet run:  <what is pending>

Next action: <one sentence>

Give me commands in separate labelled blocks, one command per block.
```

#### The closing obligation

A session is not closed until the prompt exists in both places. If Claude ends a
session without producing it, that is a defect in method, to be stated and corrected
rather than absorbed.

---

## Section 2 What is not in this protocol

Named so that their absence is a decision rather than an oversight, and so no session
reinvents them:

- **No workstream claims file.** The accounts alternate rather than run concurrently,
  so there is nothing to claim against. Rule Section 1.1.2 covers it.
- **No findings register.** Small defects are fixed when found or become a GitHub
  issue. A third register would compete with both.
- **No prediction scorecard.** Useful on a long codebase where calibration compounds.
  Six weeks is not long enough to earn it back.
- **No formal document register.** Section 9 of `CLAUDE.md` is the document map.

If one of these starts to feel necessary, that is a signal the project has outgrown
its deadline, not a signal to add process.
