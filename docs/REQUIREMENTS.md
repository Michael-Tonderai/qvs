# QVS Requirements Register

Every requirement carries an ID and names the mechanism that verifies it. Most map to
tests marked `@pytest.mark.req("REQ-...")`; the rest are verified by the pipeline, by
branch protection, by the coverage gate or by the deployment itself. `tools/traceability.py`
joins both sides and generates the requirements traceability matrix in `docs/evidence/`.

That matrix is the evidence for the assignment's *Automated Verification of
Requirements* deliverable. It is generated, not written, and it goes into the
technical report as a figure.

**Tier is the triage order.** Under deadline pressure Tier 3 is deferred first, then
Tier 2. Tier 1 is the submission floor - without all of it, what is delivered is not
a qualification verification system.

Requirements are never renumbered and never deleted. A dropped requirement is marked
`DEFERRED` with a date and a reason, and that line becomes a sentence in the report's
critical evaluation - which is worth more than the feature would have been.

---

## Verification mechanisms

The `Verified by` column names how a requirement is checked without a human deciding
to check it. The assignment's *Automated Verification of Requirements* section asks
for test cases, validation rules, CI/CD quality gates and verification reports; these
tokens are this project's instances of those.

| Token | Mechanism |
|---|---|
| `suite` | A pytest test carrying a `req` marker for this ID |
| `pipeline` | A CI job in `.github/workflows/ci.yml` other than the test run - lint, bandit, or the image build |
| `protection` | Branch protection on `main` and its required status check (D-031) |
| `coverage` | The `fail_under` threshold in `pyproject.toml`, enforced wherever the suite runs |
| `deployment` | The running deployed instance and the platform's own health polling (D-036) |

A requirement whose mechanism includes `suite` and which has no test is a gap, and
`tools/traceability.py --check` exits non-zero on one. A requirement verified by any
other mechanism is not expected to have a test and is not counted as a gap.

---

## Functional

| ID | Requirement | Tier | Status | Verified by |
|---|---|---|---|---|
| REQ-F-001 | Each qualification record is issued a unique, non-guessable certificate ID | 1 | VERIFIED | suite |
| REQ-F-002 | Each record carries an HMAC-SHA256 signature computed over its canonical fields at issue | 1 | VERIFIED | suite |
| REQ-F-003 | An authorised user can register a qualification record | 1 | VERIFIED | suite |
| REQ-F-004 | An unauthenticated user cannot register or edit records | 1 | VERIFIED | suite |
| REQ-F-005 | Any user can verify a record by certificate ID, receiving VERIFIED, NOT FOUND or TAMPERED | 1 | VERIFIED | suite |
| REQ-F-006 | A record altered after issue fails verification | 1 | VERIFIED | suite |
| REQ-F-007 | Every verification attempt writes an audit event | 1 | BUILT | suite |
| REQ-F-008 | Audit events are append-only - no update or delete path exists | 1 | BUILT | suite |
| REQ-F-009 | Any user can search records by certificate ID, holder name or institution | 2 | OPEN | suite |
| REQ-F-010 | Any user can retrieve the detail of a single record | 2 | OPEN | suite |
| REQ-F-011 | An authorised user can view the audit history for a record | 3 | OPEN | suite |
| REQ-F-012 | A visitor arriving at the site root is taken to the public verification page | 2 | VERIFIED | suite |

## Non-functional

| ID | Requirement | Tier | Status | Verified by |
|---|---|---|---|---|
| REQ-N-001 | No change reaches `main` without passing lint, security scan and the test suite | 1 | VERIFIED | protection, pipeline |
| REQ-N-002 | No secret, key or credential is committed to the repository | 1 | OPEN | suite |
| REQ-N-003 | The system is deployed to a publicly accessible HTTPS URL, redeployed automatically on merge to `main` | 1 | VERIFIED | deployment |
| REQ-N-004 | Test coverage of application code meets the configured threshold, measured with branch coverage enabled | 2 | BUILT | coverage |
| REQ-N-005 | The system exposes a health endpoint the deployment platform can poll to decide whether an instance is serving | 1 | VERIFIED | suite, deployment |

**The `Verified by` column was added on 2026-09-13**, in session 015, because the
first run of `tools/traceability.py` disproved this file's own opening claim. It had
said that every ID maps to at least one test. Six did not, and three of those six -
REQ-N-001, REQ-N-003 and REQ-N-004 - carried a status of VERIFIED or BUILT. None of
them was actually unverified: REQ-N-001 is enforced by branch protection and the
required status check, REQ-N-003 by the deployment itself, REQ-N-004 by the coverage
threshold the pipeline runs. What was wrong was the register's assumption that a
pytest test is the only thing that can verify a requirement automatically. The
matrix now reports the mechanism rather than reporting an absence, and D-038 records
why.

**REQ-F-001 moved to VERIFIED on 2026-09-12.** A record registered through the live
site was issued `QVS-DWCQ-2GTA-SZEV-KS9E`, which contains no character outside
`signing.CERTIFICATE_ID_ALPHABET`, and it was then verified anonymously from two
independent clients. Until this session the requirement had only ever been exercised
against a test database. Evidence in `docs/evidence/seeding.md`.

Note for the report rather than a qualification of the status: one record on the
deployed instance, `QVS-TEST-CASE-2345-6789`, carries a fixed identifier by design.
It is a fixture inserted by a management command and was never issued to anyone, so
it does not weaken this requirement - but it is visible on a public URL and D-037
argues the case rather than leaving it to be found.

**REQ-N-003 was reworded on 2026-09-12.** It previously read *the system starts from a
single `docker compose up` with no manual steps*. D-026 moved deployment off local
Docker after the machine that could run it was lost, and D-036 settled on a managed
platform that builds the image itself and redeploys on merge, so the old wording named
a start command nobody would ever run for assessment. The requirement is the same
requirement - the system must start with no manual steps - and only the mechanism it
names has changed. The original text is recorded here rather than overwritten silently,
because a requirement that quietly changes to match what was built is not evidence of
anything.

**REQ-F-012 was added on 2026-09-14.** It is not a new capability - the root redirect
has existed and been tested since REQ-F-005 landed. It is the retrospective
registration of a decision that was implemented and tested but never written down, and
D-038 named that omission as one of its two live findings: three tests in
`tests/test_routing.py` cited no requirement at all, so the traceability matrix showed
tested behaviour with nothing to trace it to.

The wording matters. This requirement is about **landing behaviour**, not about
verification. `tests/test_routing.py` argued in its own header that these tests should
carry no marker, on the grounds that marking them would let a URL configuration count
as evidence that the system can verify a qualification - and against `REQ-F-005` that
argument is correct. It does not hold against a requirement scoped to where the front
door opens. Delete the redirect and REQ-F-005 is still met by `/verify/`; delete the
view and no redirect saves it. Two separate claims, two separate requirements, and the
header comment in that file was rewritten in the same commit so it no longer
contradicts the markers beneath it.

It is deliberately absent from the assignment mapping table below. The brief asks for
four capabilities and this is none of them - it is a usability decision about the
public entry point, and the honest place for it is here rather than stretched to fit a
row it does not belong in.

**REQ-N-005 was added on 2026-09-12.** The health endpoint existed from Sprint A as a
toolchain smoke test and was cited by `tests/test_health.py` as evidence for
REQ-N-003, which it never was - answering 200 under the test client says nothing about
whether the system is deployed. Under D-036 the endpoint became the platform's health
check, which is infrastructure with a real failure mode: if it stops answering, the
instance is taken out of rotation. That deserves a requirement of its own, and the two
tests now cite it.

---

## Mapping to the assignment's functional brief

The assignment requires four capabilities. Each maps to requirements above, so
nothing in the brief is unaccounted for and nothing here is invented:

| Assignment capability | Covered by |
|---|---|
| Register qualifications or certifications | REQ-F-001, 002, 003, 004 |
| Search and retrieve qualification records | REQ-F-009, 010 |
| Verify the authenticity of qualifications | REQ-F-005, 006 |
| Maintain an auditable history of verification activities | REQ-F-007, 008, 011 |

## Status values

- **OPEN** - not yet implemented.
- **BUILT** - implemented and covered by a passing test, but not yet browser-verified.
- **VERIFIED** - browser-confirmed by Sir Ton. A green test suite is not a verified
  page (`CLAUDE.md` Section 5).
- **DEFERRED** - cut, with a date and a reason, for the critical evaluation.
