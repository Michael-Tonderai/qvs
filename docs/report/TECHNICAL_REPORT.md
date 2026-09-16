# A DevOps-Enabled Qualification Verification System

**Technical Report**

MIM736 Software Engineering - Practical Assignment, August 2026

---

## 1. Problem analysis

Qualification verification is a trust problem before it is a software problem. A
printed certificate carries both the claim and the only evidence for that claim, so a
relying party holding one has no independent way to distinguish a genuine award from a
convincing forgery. The usual remedy is to telephone or email the awarding
institution, which is slow, depends on somebody answering, produces no record that the
check ever happened, and scales badly when an employer is screening many applicants.

The problem is neither hypothetical nor marginal. Eaton and Carmichael (2023) document
a global market in fraudulent credentials sustained by diploma mills and transcript
tampering, and found that a majority of registrar, admissions and hiring staff surveyed
did not regard fake degrees as a significant concern. The binding constraint is
therefore not detection technology but the absence of a cheap, routine verification step
in hiring.

Three parties are involved and they want different things. The awarding institution
wants to remain the authority on what it did and did not award. The holder wants to
prove a qualification without surrendering control of their record to anybody who asks.
The relying party wants an answer it can act on, and wants that answer to be checkable
later if a dispute arises.

Those competing interests suggest four properties rather than a feature list. A record
needs an identifier that cannot be guessed, or the register can be enumerated. It needs
to be tamper-evident, so that alteration after issue is detectable rather than merely
discouraged. It needs a checking path open to people with no account, because the
relying party is by definition an outsider. And every check needs to leave a permanent
trace, because an unauditable verification is one nobody can appeal against.

The assignment brief asks for four capabilities - registering qualifications, searching
and retrieving records, verifying authenticity, and maintaining an auditable history of
verification activity - and each maps onto one of those properties. The system
described here, QVS, implements all four and deploys them to a public URL.

The dominant constraint was six weeks of calendar time alongside full-time employment.
The response was an explicit scope fence: features that add capability - a REST API, a
role hierarchy, blockchain-backed credentials, a JavaScript front end - were excluded at
the outset, on the reasoning that a defended rejection in this report is worth more than
a half-finished implementation. The fence was widened exactly once, for a single
stylesheet, when usability proved to be a named assessment criterion.

## 2. Requirements

The requirements register holds seventeen entries: twelve functional and five
non-functional. Each carries a permanent identifier, a tier, a status and a named
verification mechanism. Requirements are never renumbered and never deleted; a dropped
one is marked DEFERRED with a date and a reason, so the register records what was
decided rather than only what survived.

Tier is a triage order rather than a priority label. Tier 1 is the submission floor -
without all of it, what is delivered is not a qualification verification system. Under
deadline pressure Tier 3 is abandoned first, then Tier 2. Writing that ordering down
before it was needed is what made it useful when time grew short.

The verification mechanism column matters more than it appears to. Each requirement
names how it is checked without a human deciding to check it, using one of five tokens:
`suite` for a pytest test carrying a marker naming the requirement, `pipeline` for a
continuous integration job, `protection` for branch protection and its required status
check, `coverage` for the enforced threshold, and `deployment` for the running instance.
Fourteen requirements are verified by tests; three are verified by other mechanisms and
are not expected to have any.

That column was added late, in response to evidence. The register originally claimed
that every requirement mapped to at least one test. The first run of the traceability
generator disproved the claim: six requirements had no test, and three of those were
marked VERIFIED or BUILT. None was actually unverified. What was wrong was the
register's assumption that a test is the only thing that can verify a requirement
automatically - an assumption the brief's own list of mechanisms rejects.

Two requirements were reworded after they had been written, and both changes are
recorded rather than smoothed away. The deployment requirement originally described a
local container start command and now names a public HTTPS URL. The search and
retrieval requirements originally read "Any user" and now read "An authenticated user",
for reasons given in Section 4. A register containing two after-the-fact rewordings is
a register written early against a system nobody had built yet, and Section 8 treats
that as a finding rather than an embarrassment.

At submission, fourteen requirements are VERIFIED, two are BUILT and one is OPEN. The
open one forbids committing any secret or credential to the repository. It has one test
behind it, that test covers a single path, and no secret-scanning gate exists in the
pipeline. The requirement is therefore weaker than its row in the matrix suggests, and
saying so is more useful than quietly promoting it.

## 3. System architecture

QVS is a server-rendered Django 5.2 application running as a single containerised
process. There is one Django project package, `config`, and one application package,
`qualifications`. The deliberate absence of further structure is itself the
architectural decision: at seventeen requirements, splitting the domain across several
apps would add import ceremony and return nothing.

Within the application, responsibility is split by module rather than by framework
convention. `signing.py` holds pure functions - identifier generation, canonical payload
construction, keyed hash computation and constant-time comparison - and imports no
models. That independence is what allows the cryptographic core to be tested in
isolation, and twelve of the thirteen tests behind the signature requirement run without
touching a database. `models.py` defines the two persisted entities and calls into
`signing.py` when a record is first saved. `verification.py` holds the verification
decision and the three outcomes it can return. `audit.py` records attempts and retrieves
a record's history. `search.py` holds the query logic. `views.py`, `forms.py` and
`urls.py` form the HTTP surface, and templates render server side with no client-side
framework and no build step.

The data model has two entities. `Qualification` carries the holder, the qualification,
the awarding institution, the award date, an issue timestamp, a certificate identifier
and a signature computed over a canonical ordering of its substantive fields.
`AuditEvent` records one verification attempt: the identifier submitted, the outcome,
the actor, the remote address and a timestamp.

`AuditEvent` deliberately has no foreign keys. It stores the submitted identifier as a
string and the actor as a username snapshot, and the history page joins on that string.
The reasoning is that the events most worth auditing are those where somebody presented
an identifier this system never issued, and such events have no record to point at - a
nullable foreign key would be null on exactly the rows that matter most. On the actor
side, every deletion behaviour the ORM offers is wrong in a different way: cascading
destroys audit history, nulling rewrites an audit row and so contradicts the
append-only guarantee inside the model's own definition, and protecting turns the audit
trail into a reason an account cannot be closed. The trail therefore survives the
deletion of anything it refers to, and records what was presented rather than what it
turned out to be.

The public surface is narrow by design, and the asymmetry is the most interesting
security property the system has. Three things are reachable without an account: the
root redirect, the health endpoint, and verification by certificate identifier.
Registration, search, record detail and audit history all require authentication.
Verification is public because a holder chose to hand their certificate to somebody;
discovering records you were not given is a different act entirely.

The deployment topology is one container: gunicorn serving the application, WhiteNoise
serving static files from the same process rather than a second service, and SQLite on
the container filesystem. A health endpoint answers the platform's polling. The image is
built from a Dockerfile in the repository and the running service is declared in a
blueprint file committed alongside it, rather than configured by hand in a web console.

## 4. Design decisions

Forty-one decisions are recorded in the project's decisions register, each written as
four parts: the context that forced a choice, the choice, what was rejected, and what
the choice cost. The register is numbered, never renumbered and never deleted, so a
superseded decision stays in place carrying a pointer to whatever replaced it. Six are
argued here because they are the ones a reader is most likely to question.

**Django rather than a microframework.** Django supplies authentication, an ORM, forms,
CSRF protection, an admin interface and a test client. FastAPI or Flask would have meant
implementing each by hand, and each one is then a requirement to design, test and defend.
On a six-week budget, the framework doing the most unglamorous work is the correct one.

**HMAC-SHA256 rather than a blockchain.** The brief offers bonus marks for
blockchain-based credential verification, and the rejection was made early and on the
merits. Tamper-evidence requires that a record altered after issue be detectable. A
keyed hash over a canonical ordering of a record's substantive fields achieves this in
roughly thirty lines with no external dependency, using a construction whose security
properties are long established (Krawczyk, Bellare and Canetti, 1997). A distributed
ledger additionally resists an issuer who rewrites their own history - a real property,
but not one this problem requires, since the issuing institution is the trust anchor in
every scenario the system serves. Protecting against the one party everybody has already
agreed to trust is architecture in search of a requirement.

**Append-only enforced in the application, not the database.** The strongest available
mechanism is a database trigger refusing UPDATE and DELETE. Enforcement was instead
written in Python: the model's save method raises when the row already exists, its
delete method always raises, and - the substantive half - the queryset class overrides
update and delete as well, because the ORM's queryset update writes SQL without ever
calling the model's save. A guard on the model alone would have left a bulk update
working perfectly while appearing complete. The rejected trigger would have held against
raw SQL, which these guards do not, and would have pinned the schema to one backend. The
guarantee holds against every path the application offers and nothing outside it, which
Section 8 states plainly.

**Search and retrieval behind authentication.** Both requirements were originally
written as "Any user", by symmetry with public verification. Read literally, that
specifies a public index of every record the system holds, searchable by a person's name
and by their awarding institution. Building it as written would have defeated the
non-guessable identifier entirely - an unguessable reference buys nothing once the
record it names can be found by typing the holder's name - and would have broken the
consent chain that makes public verification defensible. The requirements were reworded
and the capability built behind login. Building behind login while leaving the register
saying "Any user" was rejected explicitly, because that is how a governance document
stops describing the system it governs.

**A dedicated page for audit history rather than the admin interface.** Registering the
audit model in Django's admin would have taken minutes and produced a changelist
carrying update and delete controls that the model raises on, making a deliberate
guarantee look like a broken screen. The page instead joins on an exact match of the
normalised identifier. Substring matching, which the search feature uses, was rejected
here because it would pull any other certificate whose identifier contained this one
into the page, mixing two records' audit trails.

**A managed container platform rather than local Docker.** The original decision was
local Docker, on the reasoning that a cloud account meant billing friction for no extra
marks. It was superseded when the machine the project moved to could not have Docker
Desktop, WSL or any hypervisor component installed. The image definition was kept and
the build moved to the continuous integration runner, so containerisation remained real,
reviewable work rather than being discarded; the running system moved to a managed
platform building from the same Dockerfile. The cost is three properties of a free
instance that are limitations rather than defects: an ephemeral disk, so records created
through the live site do not survive a restart; a fifteen-minute idle sleep with a cold
start of up to a minute; and a 512 MB memory ceiling.

## 5. DevOps workflow

The repository uses three kinds of branch, following the structure popularised by
Driessen (2010). `main` holds released code and deploys automatically on merge.
`develop` is the integration branch. Short-lived branches named for the requirement or
decision they implement are cut from `develop` and merged back through pull requests.
Eleven such branches survive on the remote at submission, undeleted on purpose, because
branch history is assessed and tidying it away would destroy the evidence.

Every change travels through an issue, a branch and a pull request with a self-review
comment. The alternative - committing directly and reconstructing a plausible history
afterwards - cannot be done convincingly. Two standing exceptions exist and both are
registered rather than quietly taken. The repository's root commit landed directly on
`main`, because `develop` cannot be branched from a commit that does not exist and the
hosting platform cannot protect a branch with no reference. Session-close log commits
also go directly to `develop`, because a pull request reviewed by the person who wrote
it minutes earlier produces a review artefact with no reviewer and no finding.

Continuous integration follows the practice Fowler (2006) describes: every change is
built and tested automatically on integration, so that defects surface within minutes
rather than at a late integration phase. The pipeline runs on GitHub Actions, defined in
a workflow file committed to the repository, so the pipeline definition is itself part
of the assessed deliverable rather than configuration living in a web console. Two jobs
run on every pull request and every push. The first runs an encoding check, lint, format
check, security scan and the test suite with coverage. The second builds the container
image, starts it with the port set to a non-default value, and requests the health
endpoint from outside the container.

The path from a merge to a running system is automated end to end, which is the
deployment pipeline Humble and Farley (2010) argue for: releasing should be a routine,
low-risk event rather than a scheduled ordeal. `main` is protected, the first job is a
required status check with strict mode enabled so a stale head must rebuild before
merging, and administrator enforcement is on - meaning the sole maintainer cannot push
to `main` either. Changes arrive by pull request or not at all. Linear history was
deliberately left off, because a release merge from `develop` carries two parents and
would be refused, and squashing `develop` into `main` would collapse the branch history
being assessed. Forsgren, Humble and Kim (2018) find deployment frequency and lead time
to be among the measures that distinguish higher-performing delivery organisations, and
the arrangement here optimises for exactly that: a merge to `main` is a deployment.

One piece of local tooling shaped the evidence base. Every version-control and platform
CLI command runs through a wrapper script that writes full output to a dated artefact
file, quiet commands included, because an exception list is a second rule that drifts out
of sync with the first. Every operation therefore left a readable record of what was run
and what it returned, which terminal scrollback was never going to provide.

## 6. Testing strategy

The suite holds 108 tests, run under pytest with the Django plugin. Every test carries
two kinds of marker: one declaring whether it is a unit or an integration test, and one
naming the requirement it verifies. The brief assesses unit and integration tests
separately, and the requirement marker is what makes automated traceability possible.
Django's own test runner was rejected for this reason: without markers, both the unit
and integration split and the traceability matrix would be maintained by hand.

The distribution across the two markers is informative. The signature and identifier
modules are tested almost entirely as unit tests, because they were written as pure
functions with no model imports. Everything touching HTTP, persistence or authentication
is an integration test exercised through Django's test client, which is why the audit,
search and history requirements are verified almost wholly by integration tests.
Architecture and test strategy here are the same decision viewed from two sides.

Coverage is measured with branch coverage enabled and enforced by a threshold in the
project configuration rather than read off a report by a human. The most recent full
local run measured 97.04 per cent across application code. Branch coverage was preferred
to statement coverage because the interesting failures in this system are conditional:
an identifier that normalises to nothing, a record whose signature is missing rather
than wrong, a request from a user who is not signed in. The figure should not be
over-read: Inozemtseva and Holmes (2014) found only a low to moderate correlation
between coverage and a suite's ability to detect faults once suite size is controlled
for, so a high percentage evidences that code is exercised, not that it is correct.

Several tests exist to pin design commitments that would otherwise erode silently. One
asserts that loading a record's audit history writes no audit event, because a trail
recording its own inspection would bury the events it exists to show. Another asserts
that arriving at the verification page without submitting anything records nothing. A
third asserts that the fixed demonstration identifier is one the system could
legitimately have issued, rather than a special case the verification path must know
about.

## 7. Verification strategy

Requirements traceability is the ability to follow a requirement forwards and backwards
across its life, from origin through specification to deployment (Gotel and Finkelstein,
1994). Their analysis attributes most traceability failures to the links being
reconstructed after the fact rather than captured as work happens, which is the failure
this project's generated matrix is designed to avoid.

The matrix is produced by a script and committed as evidence. Its rows come from the
requirements register and tests are left-joined onto them. That direction is the whole
point. A matrix assembled from test markers can only contain requirements that already
have tests, so an uncovered requirement vanishes from the document and the artefact
silently asserts complete coverage - the opposite of what evidence is for. Driving rows
from the register means a requirement with no test appears as a visible row with an
empty cell.

The generator collects markers in-process rather than parsing console output, whose
format is free to change between releases. A missing test is reported as a gap only
where the register named the test suite as the mechanism; a requirement verified by
branch protection, a pipeline job, the coverage threshold or the running deployment is
listed with no test because that is correct rather than because something is absent.

The matrix currently reports seventeen requirements, fourteen with at least one test,
three verified outside the suite, zero gaps, 108 tests collected and zero tests citing
no requirement. That last figure was not always zero: three routing tests originally
cited nothing, because they pinned a behaviour that had been implemented and tested but
never written down as a requirement. Writing the requirement down was the fix.

Above the matrix sits the pipeline, which is where requirements are verified without
anybody choosing to verify them. The brief names test cases, validation rules, quality
gates and verification reports as four mechanisms, and this project has an instance of
each: the suite; the form and model validation refusing a future award date or a
submission dictating its own identifier; the required status check on `main`; and the
generated matrix together with transcribed pipeline evidence.

## 8. Critical evaluation

The most consequential weakness is structural. For most of this project's life the
implementation had a single author, and every pull request that author opened was merged
on the strength of a self-review and a green pipeline rather than a second person's
judgement. The review gate is the pipeline, not a reviewer. That substitution is
defensible as far as it goes - an automated gate is impartial, runs every time, and
cannot be talked round - but it catches only what it was told to look for. A human
reviewer asks whether a design is right; a status check asks whether the tests pass. Two
pull requests from other group members arrived in the closing days and did receive
substantive review, one with changes requested and subsequently addressed, so genuine
peer review exists in this repository - but it arrived far too late to have shaped any
design decision in it. Every claim in this report about process rigour should be read
with that distinction in mind.

Related to it, merge conflict management is a named assessment criterion this project
never genuinely exercised. Branches were short-lived and merged quickly, so conflicts did
not arise. A conflict could have been manufactured, and was not, because a staged
conflict demonstrates the commands rather than the judgement.

Three limitations in the system are real and are stated here rather than left to be
found. First, the append-only guarantee holds against every path the application offers
and nothing else: a direct SQL update succeeds, and so would a data migration, because
historical models in migrations receive a default manager rather than the overridden one.
An application-level guarantee described as though it were a database one would not
survive a viva question. Second, a record's audit history is not the whole trail.
Attempts presenting an identifier the system never issued are recorded just as
permanently and belong to no record, so no record's history page can display them - the
system can audit what happened to a credential but cannot answer what has been attempted
against itself. Third, one seeded demonstration record carries a fixed, guessable
identifier, a genuine departure from the non-guessable identifier requirement. The
defensible reading is that the requirement constrains what the system issues, and a
fixture inserted by a management command was never issued to anybody; the identifier says
so in its own text.

The requirement that remains open is the prohibition on committing secrets. It has one
test, that test covers a single path, and no secret-scanning gate exists in the pipeline.
Adding one is perhaps an hour of work and it was not done. It is the clearest instance
here of a requirement whose row in the matrix looks stronger than the requirement is, and
the first thing that would be fixed.

The quality gate has never stopped anything. Both transcribed pipeline runs are
successes and no change has been blocked by a red check, so the strength of this gate
rests on its configuration rather than on a demonstrated save. The same caution applies
to the coverage figure, for the reason given in Section 6.

Two process observations earned their cost. The register contains two requirements
reworded after the fact, which is what happens when requirements are written early
against a system nobody has built; discovering that during implementation and recording
the change is a better outcome than either freezing the wrong wording or editing it
silently. And the decision to spend time on a decisions register rather than on further
features repaid itself in this document: most of what appears above was argued at the
moment the choice was made, not reconstructed weeks later, which is the difference
between a report that explains a system and one that rationalises it.

Given more time, the order would be: a secret-scanning gate to close the open
requirement; a system-wide audit view to answer the question a record-scoped history
cannot; and a persistent database to remove the ephemeral-disk limitation. A second
reviewer is absent from that list because review arrived late rather than never, and the
lesson this project takes from it is about when it arrived.

## References

Driessen, V. (2010) *A successful Git branching model*. Available at:
https://nvie.com/posts/a-successful-git-branching-model/ (Accessed: 14 September 2026).

Eaton, S.E. and Carmichael, J.J. (eds.) (2023) *Fake Degrees and Fraudulent Credentials
in Higher Education*. Cham: Springer.

Forsgren, N., Humble, J. and Kim, G. (2018) *Accelerate: The Science of Lean Software
and DevOps*. Portland, OR: IT Revolution Press.

Fowler, M. (2006) *Continuous Integration*. Available at:
https://martinfowler.com/articles/continuousIntegration.html (Accessed: 14 September
2026).

Gotel, O.C.Z. and Finkelstein, A.C.W. (1994) 'An analysis of the requirements
traceability problem', *Proceedings of the First International Conference on
Requirements Engineering*. Colorado Springs, CO: IEEE Computer Society Press, pp. 94-101.

Humble, J. and Farley, D. (2010) *Continuous Delivery: Reliable Software Releases
through Build, Test, and Deployment Automation*. Boston, MA: Addison-Wesley.

Inozemtseva, L. and Holmes, R. (2014) 'Coverage is not strongly correlated with test
suite effectiveness', *Proceedings of the 36th International Conference on Software
Engineering*. New York: ACM, pp. 435-445.

Krawczyk, H., Bellare, M. and Canetti, R. (1997) *HMAC: Keyed-Hashing for Message
Authentication*. RFC 2104. Internet Engineering Task Force.
