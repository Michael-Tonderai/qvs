# QVS Requirements Register

Every requirement carries an ID. Every ID maps to at least one test, marked
`@pytest.mark.req("REQ-...")`, from which `tools/traceability.py` generates the
requirements traceability matrix in `docs/evidence/`.

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

## Functional

| ID | Requirement | Tier | Status |
|---|---|---|---|
| REQ-F-001 | Each qualification record is issued a unique, non-guessable certificate ID | 1 | OPEN |
| REQ-F-002 | Each record carries an HMAC-SHA256 signature computed over its canonical fields at issue | 1 | OPEN |
| REQ-F-003 | An authorised user can register a qualification record | 1 | OPEN |
| REQ-F-004 | An unauthenticated user cannot register or edit records | 1 | OPEN |
| REQ-F-005 | Any user can verify a record by certificate ID, receiving VERIFIED, NOT FOUND or TAMPERED | 1 | OPEN |
| REQ-F-006 | A record altered after issue fails verification | 1 | OPEN |
| REQ-F-007 | Every verification attempt writes an audit event | 1 | OPEN |
| REQ-F-008 | Audit events are append-only - no update or delete path exists | 1 | OPEN |
| REQ-F-009 | Any user can search records by certificate ID, holder name or institution | 2 | OPEN |
| REQ-F-010 | Any user can retrieve the detail of a single record | 2 | OPEN |
| REQ-F-011 | An authorised user can view the audit history for a record | 3 | OPEN |

## Non-functional

| ID | Requirement | Tier | Status |
|---|---|---|---|
| REQ-N-001 | No change reaches `main` without passing lint, security scan and the test suite | 1 | OPEN |
| REQ-N-002 | No secret, key or credential is committed to the repository | 1 | OPEN |
| REQ-N-003 | The system starts from a single `docker compose up` with no manual steps | 1 | OPEN |
| REQ-N-004 | Test coverage of application code meets the configured threshold, measured with branch coverage enabled | 2 | OPEN |

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
