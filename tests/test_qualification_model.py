# tests/test_qualification_model.py
#
# REQ-F-003 at the model layer, and the parts of REQ-F-001 and REQ-F-002 that only
# become testable once there is a record to attach them to.
#
# tests/test_signing.py already proves the signing primitives in isolation. These tests
# prove the model uses them correctly, which is a different claim and the one that
# fails silently if save() is ever reordered.

from datetime import UTC, date, datetime

import pytest
from django.db import IntegrityError, transaction

from qualifications import signing
from qualifications.models import CERTIFICATE_ID_MAX_LENGTH, Qualification


def _unsaved() -> Qualification:
    """An in-memory record with every signed field populated.

    No database, so the tests built on it stay unit tests. The identifier and issue
    time are fixed literals rather than generated, because a test asserting how values
    are normalised should not also depend on what those values happen to be.
    """
    return Qualification(
        certificate_id="QVS-2345-6789-ABCD-EFGH",
        holder_name="A Holder",
        institution="An Institution",
        qualification_title="BSc Something",
        award_date=date(2024, 6, 1),
        issued_at=datetime(2026, 9, 10, 12, 0, 0, tzinfo=UTC),
    )


@pytest.mark.unit
@pytest.mark.req("REQ-F-001")
def test_certificate_id_column_is_wide_enough_for_a_generated_id():
    """The model's column width matches what the generator actually produces.

    CERTIFICATE_ID_MAX_LENGTH is a literal because a migration must record a fixed
    width. This is the test that stops the literal and the generator drifting apart -
    without it, changing the group size in signing.py would produce a database error at
    the moment a certificate is issued rather than a failure here.
    """
    assert len(signing.new_certificate_id()) == CERTIFICATE_ID_MAX_LENGTH


@pytest.mark.unit
@pytest.mark.req("REQ-F-003")
def test_str_identifies_the_record_by_certificate_id():
    """The readable form leads with the identifier, not the holder's name.

    This is what appears in the admin, in logs and in a shell session. Two people can
    share a name; the certificate ID is the thing that distinguishes one record from
    another, so it goes first.
    """
    assert str(_unsaved()) == "QVS-2345-6789-ABCD-EFGH - A Holder"


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_canonical_fields_normalises_every_value_to_a_string():
    """No non-string value reaches the signing layer.

    signing.canonical_payload() carries `default=str`, so it will serialise a date
    rather than raise. That is exactly what makes this worth asserting: if a date ever
    slipped through, nothing would fail loudly - the record would simply stop verifying
    against its own signature once it had been read back from the database.
    """
    fields = _unsaved().canonical_fields()

    assert all(isinstance(value, str) for value in fields.values())
    assert fields["award_date"] == "2024-06-01"
    assert fields["issued_at"].startswith("2026-09-10T12:00:00")


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_canonical_fields_covers_the_intended_fields_and_no_others():
    """The signed field set is pinned by a test, not by reading the method.

    Adding a field to the model without adding it here leaves it unsigned and therefore
    freely alterable, which is the quiet way REQ-F-006 stops being true. issued_by is
    absent on purpose - a signature that depends on a row in another table cannot
    survive the deletion of a user account.
    """
    assert set(_unsaved().canonical_fields()) == {
        "certificate_id",
        "holder_name",
        "institution",
        "qualification_title",
        "award_date",
        "issued_at",
    }


def _build(registrar, **overrides) -> Qualification:
    """Create and save a qualification with sensible defaults."""
    fields = {
        "holder_name": "Tendai Moyo",
        "institution": "Midlands State University",
        "qualification_title": "BSc Honours in Information Systems",
        "award_date": date(2024, 11, 15),
        "issued_by": registrar,
    }
    fields.update(overrides)
    return Qualification.objects.create(**fields)


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_saving_populates_the_issued_fields(registrar):
    """A saved record carries an identifier, an issue time and a signature."""
    qualification = _build(registrar)

    assert qualification.certificate_id.startswith("QVS-")
    assert len(qualification.certificate_id) == CERTIFICATE_ID_MAX_LENGTH
    assert qualification.issued_at is not None
    assert len(qualification.signature) == 64


@pytest.mark.integration
@pytest.mark.req("REQ-F-002")
@pytest.mark.django_db
def test_a_registered_record_verifies_against_its_own_signature(registrar):
    """The round trip that matters: sign at issue, read back, still valid.

    Read back from the database rather than asserting against the in-memory instance.
    An instance that has never left Python holds the same objects it was signed with,
    so it would verify even if the stored representation were lossy. The database is
    where the date becomes a stored value and comes back as a fresh object, and that is
    the step capable of breaking a signature.
    """
    certificate_id = _build(registrar).certificate_id

    stored = Qualification.objects.get(certificate_id=certificate_id)

    assert signing.verify_signature(stored.canonical_fields(), stored.signature)


@pytest.mark.integration
@pytest.mark.req("REQ-F-001")
@pytest.mark.django_db
def test_each_record_gets_a_distinct_certificate_id(registrar):
    """Two records registered in succession do not collide."""
    first = _build(registrar)
    second = _build(registrar)

    assert first.certificate_id != second.certificate_id


@pytest.mark.integration
@pytest.mark.req("REQ-F-001")
@pytest.mark.django_db
def test_duplicate_certificate_ids_are_refused_by_the_database(registrar):
    """The unique constraint exists and bites.

    Entropy makes a collision negligible; the constraint makes a collision that does
    happen fail loudly instead of overwriting a record. Belt and braces, deliberately -
    silent overwrite is the failure mode this system can least afford.
    """
    existing = _build(registrar)

    with transaction.atomic(), pytest.raises(IntegrityError):
        _build(registrar, certificate_id=existing.certificate_id)


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_altering_a_substantive_field_breaks_verification(registrar):
    """Editing the record in the database invalidates its signature."""
    qualification = _build(registrar)

    qualification.holder_name = "Someone Else"

    assert not signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    )


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_backdating_the_issue_time_breaks_verification(registrar):
    """issued_at is inside the signature, so a backdated record fails.

    This is the test that earns the decision to set issued_at explicitly rather than
    with auto_now_add. Had it been left outside the signed payload, this assertion
    would fail and a record could be made to look older than it is with no trace.
    """
    qualification = _build(registrar)

    qualification.issued_at = datetime(2020, 1, 1, tzinfo=UTC)

    assert not signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    )


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_re_saving_does_not_re_sign_or_reissue(registrar):
    """save() is idempotent over the issued fields.

    The subtle failure this guards against: if save() re-signed unconditionally, then
    altering a field and saving would produce a record that verifies against its new
    contents. Tampering would repair itself and REQ-F-006 would never fire on anything.
    """
    qualification = _build(registrar)
    original_id = qualification.certificate_id
    original_signature = qualification.signature
    original_issued_at = qualification.issued_at

    qualification.holder_name = "Someone Else"
    qualification.save()

    assert qualification.certificate_id == original_id
    assert qualification.signature == original_signature
    assert qualification.issued_at == original_issued_at
    assert not signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    )
