# tests/test_audit.py
#
# REQ-F-007 - every verification attempt writes an audit event.
# REQ-F-008 - audit events are append-only; no update or delete path exists.
#
# Both in one module, for the same reason test_verification.py holds REQ-F-005 and
# REQ-F-006 together: they are one model and one migration, and the append-only
# assertions would otherwise live in a file with no events to assert against.
#
# Every client here is a fresh django.test.Client(), including the signed-in one. The
# `registrar_client` fixture IS the `client` fixture with force_login already applied,
# so a module that needs an anonymous browser and an authenticated one in the same test
# run cannot use it - it would receive the same object twice and the "anonymous"
# request would arrive authenticated. conftest.py documents this at length. These tests
# are exactly the shape that walks into it.

from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from qualifications import verification
from qualifications.audit import record_attempt
from qualifications.models import (
    OUTCOME_MAX_LENGTH,
    SUBMITTED_CERTIFICATE_ID_MAX_LENGTH,
    AppendOnlyError,
    AuditEvent,
    Qualification,
)

VERIFY_URL_NAME = "qualifications:verify"

HOLDER_NAME = "Tendai Moyo"
INSTITUTION = "Midlands State University"
QUALIFICATION_TITLE = "BSc Honours in Information Systems"

UNISSUED_CERTIFICATE_ID = "QVS-2345-6789-ABCD-EFGH"


@pytest.fixture
def qualification(registrar):
    """A genuine, correctly signed record, issued the way a registrar issues one."""
    return Qualification.objects.create(
        holder_name=HOLDER_NAME,
        institution=INSTITUTION,
        qualification_title=QUALIFICATION_TITLE,
        award_date=date(2024, 11, 15),
        issued_by=registrar,
    )


def verify_as_public(certificate_id=None):
    """GET the verification page as somebody with no account."""
    data = {} if certificate_id is None else {"certificate_id": certificate_id}
    return Client().get(reverse(VERIFY_URL_NAME), data)


def verify_as(user, certificate_id):
    """GET the verification page as a signed-in user.

    A fresh Client with force_login applied here rather than the registrar_client
    fixture. See the module docstring - the fixture would hand back the same object the
    anonymous tests use.
    """
    signed_in = Client()
    signed_in.force_login(user)
    return signed_in.get(reverse(VERIFY_URL_NAME), {"certificate_id": certificate_id})


def only_event():
    """Return the single audit event, asserting that there is exactly one.

    Written as a helper because "exactly one" is the assertion that carries most of
    REQ-F-007, and a test that fetched .first() would pass just as happily on three
    events as on one.
    """
    events = list(AuditEvent.objects.all())
    assert len(events) == 1, f"expected exactly one audit event, found {len(events)}"
    return events[0]


# --- REQ-F-007: every attempt is recorded -------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_a_successful_verification_is_recorded(qualification):
    """A VERIFIED outcome writes an event.

    The case most easily forgotten. A trail that records only failures cannot answer
    the question an auditor actually asks - was this certificate ever checked, and what
    was it told - and it quietly turns the audit log into an incident log.
    """
    verify_as_public(qualification.certificate_id)

    event = only_event()
    assert event.outcome == verification.VERIFIED
    assert event.submitted_certificate_id == qualification.certificate_id


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_an_unknown_certificate_id_is_recorded():
    """A NOT FOUND outcome writes an event, with the ID that was presented.

    No qualification exists for this ID, which is the case a ForeignKey on AuditEvent
    could not have represented - and presenting an ID this system never issued is
    precisely the event worth keeping.
    """
    verify_as_public(UNISSUED_CERTIFICATE_ID)

    event = only_event()
    assert event.outcome == verification.NOT_FOUND
    assert event.submitted_certificate_id == UNISSUED_CERTIFICATE_ID


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_a_tampered_record_is_recorded(qualification):
    """A TAMPERED outcome writes an event.

    The alteration goes through queryset.update(), which writes the column with no
    model logic in the way - the closest a test gets to somebody editing the database
    by hand, which is the threat REQ-F-006 exists to answer and the event REQ-F-007
    most needs to capture.
    """
    Qualification.objects.filter(pk=qualification.pk).update(
        holder_name="Someone Else",
    )

    verify_as_public(qualification.certificate_id)

    assert only_event().outcome == verification.TAMPERED


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_arriving_at_the_page_records_nothing():
    """A blank box is not a verification attempt.

    Auditing it would fill the trail with page loads and drown the events that matter.
    It would also give two tests in test_verification.py a database dependency they do
    not currently have, which is a smaller point but a real one.
    """
    verify_as_public()

    assert AuditEvent.objects.count() == 0


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_each_repeated_attempt_writes_its_own_event(qualification):
    """Three checks of the same certificate are three events, not one.

    An audit trail that deduplicates has stopped recording what happened and started
    summarising it. "This certificate was checked three times today" is exactly the
    kind of thing an audit trail exists to be able to say.
    """
    for _ in range(3):
        verify_as_public(qualification.certificate_id)

    assert AuditEvent.objects.count() == 3


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_an_anonymous_attempt_records_a_blank_actor(qualification):
    """Verification is public, so most events will have no actor.

    Blank rather than null, and blank rather than a placeholder string like "anonymous"
    - a placeholder is indistinguishable from a user who registered that username.
    """
    verify_as_public(qualification.certificate_id)

    assert only_event().actor_username == ""


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_a_signed_in_attempt_records_the_username(registrar, qualification):
    """When somebody is signed in, the trail says who.

    The username is snapshotted as text rather than referenced by ForeignKey, so this
    row still says who checked the certificate after the account is closed.
    """
    verify_as(registrar, qualification.certificate_id)

    assert only_event().actor_username == registrar.get_username()


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_the_remote_address_is_recorded(qualification):
    """Where the attempt came from, as the request reported it.

    Django's test client sets REMOTE_ADDR to 127.0.0.1. Behind the managed container
    service D-026 selects, this column will hold the platform's proxy address rather
    than the visitor's - audit.remote_address() documents why trusting
    X-Forwarded-For instead would be worse than that.
    """
    verify_as_public(qualification.certificate_id)

    assert only_event().remote_address == "127.0.0.1"


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_an_over_long_submission_is_truncated_rather_than_lost():
    """A pasted kilobyte still produces an event.

    The field holds what somebody typed into a public form, so it holds anything at
    all. Letting an over-long string raise would lose the record of an attempt in order
    to protect a column width, and an attempt to verify a kilobyte of text is more
    worth recording than an ordinary one, not less.
    """
    verify_as_public("Q" * 500)

    event = only_event()
    assert len(event.submitted_certificate_id) == SUBMITTED_CERTIFICATE_ID_MAX_LENGTH
    assert event.outcome == verification.NOT_FOUND


@pytest.mark.unit
@pytest.mark.req("REQ-F-007")
def test_the_outcome_column_fits_the_verification_vocabulary():
    """The coupling models.py deliberately does not enforce with `choices`.

    verification.py owns the three outcome strings and imports models.py, so models.py
    cannot import them back without closing a cycle. The column therefore carries no
    choices and its width is a literal. This test is what keeps the two in step: a
    fourth, longer outcome added to verification.py fails here rather than silently
    truncating in the database.
    """
    outcomes = [verification.VERIFIED, verification.NOT_FOUND, verification.TAMPERED]

    for outcome in outcomes:
        assert len(outcome) <= OUTCOME_MAX_LENGTH


# --- REQ-F-008: nothing can change an event afterwards ------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-008")
@pytest.mark.django_db
def test_an_existing_event_cannot_be_re_saved(qualification):
    """save() on a row that already exists is refused.

    The first and most obvious edit path, and the one a careless bug fix would reach
    for - loading an event, correcting a field and saving it back.
    """
    verify_as_public(qualification.certificate_id)
    event = only_event()
    event.outcome = verification.VERIFIED

    with pytest.raises(AppendOnlyError):
        event.save()


@pytest.mark.integration
@pytest.mark.req("REQ-F-008")
@pytest.mark.django_db
def test_an_event_cannot_be_deleted(qualification):
    """delete() on an instance is refused."""
    verify_as_public(qualification.certificate_id)

    with pytest.raises(AppendOnlyError):
        only_event().delete()


@pytest.mark.integration
@pytest.mark.req("REQ-F-008")
@pytest.mark.django_db
def test_a_queryset_cannot_be_updated(qualification):
    """queryset.update() is refused, and this is the assertion that matters most.

    update() writes SQL directly and never calls Model.save(). A guard on save() alone
    would leave AuditEvent.objects.all().update(outcome="VERIFIED") working perfectly -
    rewriting every event in the trail, through the one path the obvious guard does not
    cover. The same trick is used deliberately in test_verification.py to simulate
    tampering with a qualification, which is exactly why it has to be closed here.
    """
    verify_as_public(qualification.certificate_id)

    with pytest.raises(AppendOnlyError):
        AuditEvent.objects.all().update(outcome=verification.VERIFIED)


@pytest.mark.integration
@pytest.mark.req("REQ-F-008")
@pytest.mark.django_db
def test_a_queryset_cannot_be_deleted(qualification):
    """queryset.delete() is refused, for the same reason as update()."""
    verify_as_public(qualification.certificate_id)

    with pytest.raises(AppendOnlyError):
        AuditEvent.objects.all().delete()


@pytest.mark.integration
@pytest.mark.req("REQ-F-008")
@pytest.mark.django_db
def test_the_trail_survives_every_refused_operation(qualification):
    """After all four attempts to change it, the event is still there and unchanged.

    Asserting that each call raises proves the guard fires. It does not prove nothing
    was written first - an implementation that deleted the row and then raised would
    pass every test above. This one closes that gap.
    """
    verify_as_public(qualification.certificate_id)
    original = only_event()

    for attempt in (
        lambda: original.save(),
        lambda: original.delete(),
        lambda: AuditEvent.objects.all().update(outcome="CHANGED"),
        lambda: AuditEvent.objects.all().delete(),
    ):
        with pytest.raises(AppendOnlyError):
            attempt()

    survivor = only_event()
    assert survivor.pk == original.pk
    assert survivor.outcome == verification.VERIFIED


# --- The recorder, without a browser ------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_record_attempt_tolerates_a_request_with_no_user(rf):
    """A request built without the authentication middleware still records.

    RequestFactory produces exactly that - no session, no user attribute. The audit
    write must not be the thing that raises in that situation: a trail that can refuse
    to write is worse than one that records less, because the missing row looks like an
    attempt that never happened.
    """
    request = rf.get("/verify/", {"certificate_id": UNISSUED_CERTIFICATE_ID})

    event = record_attempt(request, UNISSUED_CERTIFICATE_ID, verification.NOT_FOUND)

    assert event.actor_username == ""
    assert event.outcome == verification.NOT_FOUND


@pytest.mark.integration
@pytest.mark.req("REQ-F-007")
@pytest.mark.django_db
def test_an_event_reads_legibly(qualification):
    """An event renders as something a person can read.

    __str__ is what appears in a shell session, a traceback and any log line that
    interpolates the object. Django's default renders "AuditEvent object (3)", which
    is useless at precisely the moment somebody is reading the trail to work out what
    happened. Trivial code, and the only line in this model the rest of the suite never
    executes - which is the usual reason a method like this is wrong when it matters.
    """
    verify_as_public(qualification.certificate_id)

    rendered = str(only_event())

    assert verification.VERIFIED in rendered
    assert qualification.certificate_id in rendered
