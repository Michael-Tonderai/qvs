# tests/test_audit_history.py
#
# REQ-F-011 - an authorised user can view the audit history for a record.
#
# This module also does something none of the others could: it exercises REQ-F-007 and
# REQ-F-008 through a page. Both were BUILT and unverifiable before this - the events
# were written on every verification and no surface in the system could display one.
#
# EVERY TEST HERE IS MARKED `integration`, for the reason tests/test_search.py gives at
# length: pyproject.toml defines `unit` as no request cycle AND no database, and
# audit.history_for issues a query. The separation audit.py buys is still real - the
# matching rule below is asserted with no client, URL or template near it - it just is
# not the separation the marker names.

from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from qualifications import audit, verification
from qualifications.models import AuditEvent, Qualification


def make_record(
    registrar,
    holder_name="Tendai Moyo",
    institution="Midlands State University",
    qualification_title="BSc Honours in Information Systems",
    award_date=date(2024, 11, 15),
):
    """Create a signed record. Deliberately a local copy of the helper in
    tests/test_search.py rather than a shared import: a test module that imports another
    test module couples two suites that should be able to change independently, and the
    four lines are cheaper than that coupling."""
    return Qualification.objects.create(
        holder_name=holder_name,
        institution=institution,
        qualification_title=qualification_title,
        award_date=award_date,
        issued_by=registrar,
    )


def make_event(submitted_certificate_id, outcome=verification.VERIFIED, actor=""):
    """Write one audit event directly.

    Direct creation rather than a round trip through the verification page, because most
    tests here are about how events are found and displayed, not about how they come to
    exist. tests/test_audit.py owns the writing path, and one test below still exercises
    the real one end to end so the two halves are known to meet.
    """
    return AuditEvent.objects.create(
        submitted_certificate_id=submitted_certificate_id,
        outcome=outcome,
        actor_username=actor,
    )


# --- The lookup rule ----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_history_finds_attempts_that_presented_this_certificate_id(registrar):
    record = make_record(registrar)
    make_event(record.certificate_id)
    make_event(record.certificate_id, outcome=verification.TAMPERED)

    assert audit.history_for(record.certificate_id).count() == 2


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_history_excludes_attempts_against_a_different_certificate_id(registrar):
    record = make_record(registrar)
    make_event("QVS-ZZZZ-ZZZZ-ZZZZ-ZZZZ", outcome=verification.NOT_FOUND)

    assert not audit.history_for(record.certificate_id).exists()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_history_does_not_match_a_submitted_string_that_merely_contains_the_id(
    registrar,
):
    """Exact match, not `icontains` - and this is the test that pins the difference.

    search.find matches fragments because a registrar holds a partial string. Here a
    substring match would mix a second record's audit trail into this record's page,
    which is the one thing an audit page must never do.
    """
    record = make_record(registrar)
    make_event(record.certificate_id + "EXTRA", outcome=verification.NOT_FOUND)

    assert not audit.history_for(record.certificate_id).exists()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_history_normalises_the_certificate_id_it_is_given(registrar):
    """A hand-typed lower-case identifier finds the same events as the canonical
    form."""
    record = make_record(registrar)
    make_event(record.certificate_id)

    assert audit.history_for(record.certificate_id.lower()).count() == 1


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_history_is_newest_first(registrar):
    record = make_record(registrar)
    first = make_event(record.certificate_id, outcome=verification.NOT_FOUND)
    second = make_event(record.certificate_id, outcome=verification.VERIFIED)

    assert list(audit.history_for(record.certificate_id)) == [second, first]


# --- Access control -----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_anonymous_history_is_redirected_to_login(client, registrar):
    """D-040 extended to REQ-F-011.

    Verification is public because a holder chose to hand somebody a certificate.
    Nothing in that choice extends to showing a stranger who else has been checking it.

    `client` and `registrar` rather than `registrar_client`: the conftest fixture IS the
    client fixture with force_login applied, so asking for both would make this request
    authenticated while the test believed it was not.
    """
    record = make_record(registrar)
    history_url = reverse("qualifications:record_history", args=[record.certificate_id])

    response = client.get(history_url)

    assert response.status_code == 302
    assert reverse("login") in response.url
    assert history_url in response.url


# --- The history page ---------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_the_page_lists_real_attempts_made_through_the_verification_page(
    registrar_client, registrar
):
    """End to end: the write path and the read path meet.

    A separate anonymous Client, not the `client` fixture, because `registrar_client`
    already is that fixture - see the hazard documented in tests/conftest.py.
    """
    record = make_record(registrar)
    public = Client()
    public.get(
        reverse("qualifications:verify"), {"certificate_id": record.certificate_id}
    )
    public.get(
        reverse("qualifications:verify"), {"certificate_id": record.certificate_id}
    )

    response = registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id])
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "2 recorded attempts" in content
    assert verification.VERIFIED in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_an_anonymous_attempt_is_shown_as_anonymous(registrar_client, registrar):
    """The actor column is blank for public traffic, and blank must read as something.

    REQ-F-005 makes verification public, so most real events will have no username. A
    column that renders empty for the commonest case looks like missing data.
    """
    record = make_record(registrar)
    make_event(record.certificate_id, actor="")

    response = registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id])
    )

    assert "anonymous" in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_a_record_with_no_attempts_says_so_rather_than_showing_an_empty_table(
    registrar_client, registrar
):
    record = make_record(registrar)

    response = registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id])
    )

    assert response.status_code == 200
    assert "No attempts recorded" in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_an_unknown_certificate_id_is_a_404_rather_than_an_empty_history(
    registrar_client,
):
    """An empty history and a missing record are different answers.

    A page that renders the first for the second tells a reader that an identifier this
    system never issued is a registered record nobody has checked.
    """
    response = registrar_client.get(
        reverse("qualifications:record_history", args=["QVS-NOPE-NOPE-NOPE-NOPE"])
    )

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_a_lower_case_certificate_id_in_the_url_still_resolves(
    registrar_client, registrar
):
    record = make_record(registrar)
    make_event(record.certificate_id)

    response = registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id.lower()])
    )

    assert response.status_code == 200
    assert "1 recorded attempt" in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_a_truncated_history_admits_it(registrar_client, registrar, monkeypatch):
    """A capped audit list that does not say it is capped is worse than a capped search
    list that does not, because what is missing reads as what never happened."""
    monkeypatch.setattr(audit, "MAX_HISTORY_EVENTS", 2)
    record = make_record(registrar)
    for _ in range(3):
        make_event(record.certificate_id)

    response = registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id])
    )

    assert response.status_code == 200
    assert "Showing the 2 most recent attempts" in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_viewing_the_history_writes_no_audit_event(registrar_client, registrar):
    """Reading the trail must not extend it.

    A trail that records its own inspection buries the events it exists to show. This is
    the same obligation tests/test_search.py pins for the search and detail pages: the
    guarantee in verification.py holds because verify() has a single caller, and this
    view is deliberately not one. If a later change makes this page verify, this test
    fails and the decision is taken again rather than inherited.
    """
    record = make_record(registrar)
    make_event(record.certificate_id)

    registrar_client.get(
        reverse("qualifications:record_history", args=[record.certificate_id])
    )

    assert AuditEvent.objects.count() == 1


@pytest.mark.integration
@pytest.mark.req("REQ-F-011")
@pytest.mark.django_db
def test_the_record_page_links_to_the_history(registrar_client, registrar):
    """The capability has to be reachable, not merely routed.

    REQ-F-009 and REQ-F-010 were built as one unit because a result list that links
    nowhere is not retrieval. The same argument applies here: a history page nobody can
    navigate to is a URL, not a feature.
    """
    record = make_record(registrar)
    history_url = reverse("qualifications:record_history", args=[record.certificate_id])

    response = registrar_client.get(
        reverse("qualifications:record_detail", args=[record.certificate_id])
    )

    assert history_url in response.content.decode()
