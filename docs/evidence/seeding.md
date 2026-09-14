# Evidence: seeding and the first round trip on the deployed system

Session 014, 2026-09-12. Deployed from `main` at commit 4899f3f.

Transcribed by hand from artefacts under `dev_reports/` and from the browser. Nothing
here is pasted from `gh` output, which mangles non-ASCII characters to `?` and would
fail `tools/Check-Ascii.ps1` in this directory.

---

## 1. What this evidences

Before this session the deployed instance had no user and no records, and no way to
create either: the free plan gives no shell, and under D-036 the disk is ephemeral, so
the database is empty at every container start. Public verification rendered but could
not be exercised by anybody, and registration could not be shown at all.

Issue #22, PR #23 and PR #24 added a `seed_demo` management command, called from
`tools/docker-entrypoint.sh` on every start. This document records what was observed
afterwards on the running system.

## 2. Pipeline evidence

PR #23, `chore/D-037-seed-demo-data` into `develop`:

| Check | Result | Duration |
|---|---|---|
| Lint, security and tests | pass | 26s |
| Container image builds and serves | pass | 55s |

PR #24, `develop` into `main`, merged as 4899f3f with parents 1e02381 and 7aea617:

| Check | Result | Duration |
|---|---|---|
| Lint, security and tests | pass | 32s |
| Container image builds and serves | pass | 22s |

The image job builds the Dockerfile, starts the container with `PORT` set to a
non-default value and requests `/health/` from outside it. It therefore exercises the
new entrypoint line inside a real container. It does so on the seed's skip path,
because the runner carries no `QVS_DEMO_PASSWORD`.

Local gate before the commit: 78 tests passing, total coverage 96.71% with
`seed_demo.py` at 100% statement and branch coverage; `ruff check` clean;
`ruff format --check` clean; `bandit -r config qualifications -ll` reporting no issues;
`Check-Ascii.ps1` ASCII clean across 65 files; `Check-Docs.ps1` DOCUMENTS CURRENT.

## 3. The seed ran on the deployed instance

`curl` against `/health/` at 23:29:50 UTC returned `{"status": "ok", "service": "qvs"}`.

The fixed-ID record was then requested anonymously:

```
GET https://qvs-f3dk.onrender.com/verify/?certificate_id=QVS-TEST-CASE-2345-6789
```

Outcome **VERIFIED**, with:

| Field | Value |
|---|---|
| Certificate ID | QVS-TEST-CASE-2345-6789 |
| Holder | Tendai Marimo |
| Institution | Midlands State University |
| Qualification | Master of Commerce in Information Systems Management |
| Awarded | 2024-11-22 |
| Registered | 2026-09-12 23:27:19 UTC |

The registration timestamp is the evidence that this record was created by the
container's own start-up: the platform log shows the previous instance receiving
`SIGTERM` at 23:27:29, ten seconds later. This was the first execution of the seed on
its creating path anywhere - locally and in CI it had only ever taken the skip branch.

It is also the first time a signature has been verified outside a test database. The
record was signed with the `QVS_SIGNING_KEY` the platform generated at first deploy
(D-036), and the signature reproduced on a later, separate request.

## 4. The first POST against the deployed system

Sign-in at `/login/` as `registrar`, in a browser, succeeded and redirected to
`/register/`, which rendered with `Signed in as registrar`.

This settles the one fix registered in D-036 that had remained unproven.
`SECURE_PROXY_SSL_HEADER` matters only on a POST, and until an account existed there
was no POST anyone could make. Had the header been wrong, Django's CSRF middleware
would have rejected the submission with 403. It did not.

## 5. Registration and verification round trip

A record was registered through the live form and then verified anonymously.

| Field | Value |
|---|---|
| Certificate ID | QVS-DWCQ-2GTA-SZEV-KS9E |
| Holder | Florence Nyahora |
| Institution | Bindura State University |
| Qualification | BComm Business Management |
| Awarded | 2026-08-03 |
| Registered | 2026-09-12 23:41:09 UTC |
| Registered by | registrar |

The issued identifier contains no character outside `CERTIFICATE_ID_ALPHABET` - no
`I`, `L`, `O`, `U`, `0` or `1` - which is REQ-F-001's readability constraint holding on
a real issue rather than in a test.

Verification was performed twice, from two independent clients: the browser after
signing out, and `curl` with no cookie, no session and a different user agent. Both
returned VERIFIED with the four substantive fields intact.

Two details worth recording because they are design decisions rather than accidents:

- The registrar's confirmation page displays the signature; the public verification
  page does not. The digest is a receipt behind `login_required`, and it reveals
  nothing without the key.
- The public page shows no `Registered by`. `canonical_fields()` keeps `issued_by`
  outside the signed payload, so a verified record does not disclose which member of
  staff issued it.

## 6. Limitations, stated rather than discovered

- **The registered record is not durable.** The free instance has no persistent disk,
  so `QVS-DWCQ-2GTA-SZEV-KS9E` exists only until the next restart or redeploy. The
  seeded records return on every start; anything registered through the live site does
  not. This is why one seeded record carries a fixed identifier (D-037).
- **One deployed record has a guessable certificate ID.** `QVS-TEST-CASE-2345-6789` is
  a fixture inserted by a management command, not a credential this system issued.
  D-037 registers the reasoning and the tension with REQ-F-001.
- **The audit trail has been written but never read.** Every verification above created
  an audit event under REQ-F-007. REQ-F-011, which would display them, is still OPEN,
  so no evidence here rests on reading that trail back.
- **The instance sleeps after fifteen minutes idle** and takes 30 to 60 seconds to
  wake. Any URL shown to an assessor should be warmed first.
