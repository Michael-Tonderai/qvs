# tests/test_verification.py
#
# REQ-F-005 - any user can verify a record by certificate ID, receiving VERIFIED,
#             NOT FOUND or TAMPERED.
# REQ-F-006 - a record altered after issue fails verification.
#
# Both requirements are tested here rather than split across two modules. They are one
# page and one decision: REQ-F-006 is not a separate feature but the third outcome of
# REQ-F-005, and separating them would put the TAMPERED assertions in a file with no
# page to assert against.
#
# Every client in this module is a fresh django.test.Client(). The `registrar_client`
# fixture IS the `client` fixture with force_login already called on it, so a test that
# asks for both receives one object and its supposedly anonymous request arrives
# authenticated - a failure that is silent, because the test still passes while
# asserting nothing about the public. conftest.py documents this at length. These tests
# are the exact shape that walks into it, so they do not take either fixture.

from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from qualifications import verification
from qualifications.models import Qualification

VERIFY_URL_NAME = "qualifications:verify"

HOLDER_NAME = "Tendai Moyo"
INSTITUTION = "Midlands State University"
QUALIFICATION_TITLE = "BSc Honours in Information Systems"


@pytest.fixture
def qualification(registrar):
    """A genuine, correctly signed record.

    Created through the model rather than assembled by hand, so the signature under
    test is the one save() issues - the same code path a registrar exercises. A record
    signed by the test itself would verify against the test's own idea of canonical
    fields rather than the system's.
    """
    return Qualification.objects.create(
        holder_name=HOLDER_NAME,
        institution=INSTITUTION,
        qualification_title=QUALIFICATION_TITLE,
        award_date=date(2024, 11, 15),
        issued_by=registrar,
    )


def verify_response(certificate_id=None):
    """GET the verification page as a member of the public.

    A fresh Client on every call, never a fixture. See the module docstring.
    """
    data = {} if certificate_id is None else {"certificate_id": certificate_id}
    return Client().get(reverse(VERIFY_URL_NAME), data)


# --- REQ-F-005: the page is reachable and answers -----------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
def test_the_verification_page_is_public():
    """An anonymous visitor reaches the page, with no redirect to login.

    The assertion that carries the requirement's first half. Every other route in this
    app either requires a session or is a health probe; this one exists for people who
    have no account and never will. A 302 here would mean the capability was built
    behind the wall it was supposed to be outside.

    No database marker: the bare page renders a form and queries nothing.
    """
    response = verify_response()

    assert response.status_code == 200
    assert b"Verify a qualification" in response.content


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
def test_the_bare_page_reports_no_outcome():
    """Arriving at the page is not a failed verification.

    Someone who has not typed anything yet must not be told NOT FOUND. The first
    version of a page like this usually gets that wrong, because the empty string is
    easy to treat as an unknown ID.
    """
    content = verify_response().content

    assert b"NOT FOUND" not in content
    assert b"VERIFIED" not in content
    assert b"TAMPERED" not in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
@pytest.mark.django_db
def test_a_genuine_certificate_verifies(qualification):
    """The happy path, and the only outcome that shows the record's contents."""
    response = verify_response(qualification.certificate_id)

    assert response.status_code == 200
    assert b"VERIFIED" in response.content
    assert HOLDER_NAME.encode() in response.content
    assert INSTITUTION.encode() in response.content
    assert QUALIFICATION_TITLE.encode() in response.content


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
@pytest.mark.django_db
def test_an_unknown_certificate_id_is_not_found():
    """A well-formed ID that was never issued gets a clear, non-accusatory answer."""
    response = verify_response("QVS-2345-6789-ABCD-EFGH")

    assert response.status_code == 200
    assert b"NOT FOUND" in response.content
    assert b"VERIFIED" not in response.content


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
@pytest.mark.django_db
def test_an_unknown_id_still_returns_200(qualification):
    """NOT FOUND is an answer, not a broken URL.

    Asserted explicitly because 404 is the tempting choice. It would make the
    verification service look absent whenever it successfully reports that a
    certificate does not exist, and it would let an automated caller sort real IDs from
    invented ones by status code alone, without reading a response body.

    The genuine record exists in this test so that the two paths are compared under
    identical conditions - same page, same database, different ID.
    """
    assert verify_response(qualification.certificate_id).status_code == 200
    assert verify_response("QVS-9999-9999-9999-9999").status_code == 200


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
@pytest.mark.django_db
def test_a_certificate_id_typed_in_lower_case_verifies(qualification):
    """A holder reading an ID off a printed document types what they see.

    Case sensitivity here would produce a false NOT FOUND, which is the failure mode
    signing.py already pays entropy to avoid by excluding look-alike characters.
    """
    response = verify_response(qualification.certificate_id.lower())

    assert b"VERIFIED" in response.content


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
@pytest.mark.django_db
def test_a_pasted_id_with_stray_whitespace_verifies(qualification):
    """Copying an ID out of an email brings leading, trailing or wrapped spaces."""
    certificate_id = qualification.certificate_id
    wrapped = f"  {certificate_id[:12]} {certificate_id[12:]}  "

    response = verify_response(wrapped)

    assert b"VERIFIED" in response.content


# --- REQ-F-006: alteration is detected ----------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_an_altered_record_reports_tampered(qualification):
    """The requirement, in one assertion.

    The alteration goes through queryset.update() rather than through save(). update()
    writes the column directly, with no model logic in the way, which is the closest a
    test can get to someone editing the database by hand - and that is the threat
    REQ-F-006 exists to answer. Using save() would also work, because save() refuses to
    re-sign an existing record, but it would leave the test depending on that guard
    rather than testing the signature.
    """
    Qualification.objects.filter(pk=qualification.pk).update(
        holder_name="Someone Else",
    )

    response = verify_response(qualification.certificate_id)

    assert response.status_code == 200
    assert b"TAMPERED" in response.content
    assert b"VERIFIED" not in response.content


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_a_tampered_record_does_not_display_its_contents(qualification):
    """Refusing to vouch for a record means refusing to show it.

    Rendering the altered fields under a warning heading would put unverified data on
    screen in the same layout a genuine record uses, and a reader who skims carries
    away a name the system has just refused to stand behind. The view attaches no
    record to a TAMPERED result, so there is nothing for the template to leak.

    Both the altered value and the original are asserted absent: showing either one
    would be a disclosure, and the original would additionally be a lie about what the
    database now contains.
    """
    Qualification.objects.filter(pk=qualification.pk).update(
        holder_name="Someone Else",
    )

    content = verify_response(qualification.certificate_id).content

    assert b"TAMPERED" in content
    assert b"Someone Else" not in content
    assert HOLDER_NAME.encode() not in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_an_altered_award_date_reports_tampered(qualification):
    """A second field, because a one-field signature would pass the test above.

    award_date is chosen deliberately: it is the field most worth forging on a
    qualification, and it is stored as a date rather than a string, so it also exercises
    the ISO-8601 normalisation in canonical_fields() that keeps a genuine record from
    being falsely accused.
    """
    Qualification.objects.filter(pk=qualification.pk).update(
        award_date=date(2020, 1, 1),
    )

    assert b"TAMPERED" in verify_response(qualification.certificate_id).content


@pytest.mark.integration
@pytest.mark.req("REQ-F-006")
@pytest.mark.django_db
def test_a_record_stripped_of_its_signature_is_tampered(qualification):
    """An empty signature is tampering, not a malformed record.

    Deleting the signature is the laziest possible attack and it must not produce a
    crash, an exception page, or - worse - a pass. signing.verify_signature answers
    False for an absent signature precisely so this lands as TAMPERED.
    """
    Qualification.objects.filter(pk=qualification.pk).update(signature="")

    response = verify_response(qualification.certificate_id)

    assert response.status_code == 200
    assert b"TAMPERED" in response.content


# --- Normalisation, tested without a request ----------------------------------------


@pytest.mark.unit
@pytest.mark.req("REQ-F-005")
def test_normalisation_uppercases_and_removes_whitespace():
    """The two repairs that are safe to make."""
    assert (
        verification.normalise_certificate_id("  qvs-2345-6789-abcd-efgh  ")
        == "QVS-2345-6789-ABCD-EFGH"
    )
    assert (
        verification.normalise_certificate_id("QVS-2345-6789\n-ABCD-EFGH")
        == "QVS-2345-6789-ABCD-EFGH"
    )


@pytest.mark.unit
@pytest.mark.req("REQ-F-005")
def test_normalisation_does_not_repair_look_alike_characters():
    """The repairs that are not safe to make, asserted so nobody adds them casually.

    Crockford base32 folds O onto 0 and I onto 1, and it would be natural to copy that
    here. signing.py excludes 0 and 1 from the alphabet as well, so there is no correct
    target to fold onto - a typed O is not a character any issued ID contains. Guessing
    at a repair risks normalising one valid ID into a different valid ID, and silently
    verifying the wrong record is far worse than answering NOT FOUND to a typo.
    """
    assert verification.normalise_certificate_id("QVS-IO01") == "QVS-IO01"


@pytest.mark.unit
@pytest.mark.req("REQ-F-005")
def test_an_empty_certificate_id_is_not_found_rather_than_an_error():
    """verify() stays total, so a blank box cannot produce an exception page.

    The view avoids calling it for blank input, which is a presentation choice. This is
    the safety net underneath that choice, and it needs no database: the guard returns
    before any query runs.
    """
    result = verification.verify("")

    assert result.outcome == verification.NOT_FOUND
    assert result.qualification is None
