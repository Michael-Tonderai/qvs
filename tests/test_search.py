# tests/test_search.py
#
# REQ-F-009 - an authenticated user can search records by certificate ID, holder name
#             or institution.
# REQ-F-010 - an authenticated user can retrieve the detail of a single record.
#
# EVERY TEST HERE IS MARKED `integration`, INCLUDING THE MATCHING-RULE TESTS, and that
# is deliberate rather than lazy. pyproject.toml defines `unit` as exercising one unit
# with no request cycle AND NO DATABASE. qualifications.search.find issues a query, so
# it cannot be a unit test under this project's own vocabulary however isolated it looks
# next to a view test. tests/test_verification.py made the same call for the same
# reason, which is why REQ-F-006 shows no unit tests in the traceability matrix.
#
# The separation search.py buys is still real and still worth having - the matching
# rules below are asserted without a client, a URL or a template anywhere near them -
# it just is not the separation the marker names.
#
# D-040 is under test here as much as the requirements are. Both pages sit behind
# authentication, and the anonymous tests are what stop that quietly regressing into the
# public record directory the original wording described.

from datetime import date

import pytest
from django.urls import reverse

from qualifications import search
from qualifications.models import AuditEvent, Qualification


def make_record(
    registrar,
    holder_name="Tendai Moyo",
    institution="Midlands State University",
    qualification_title="BSc Honours in Information Systems",
    award_date=date(2024, 11, 15),
):
    """Create a signed record. Defaults are overridden per test, not per field."""
    return Qualification.objects.create(
        holder_name=holder_name,
        institution=institution,
        qualification_title=qualification_title,
        award_date=award_date,
        issued_by=registrar,
    )


# --- Matching rules -----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_blank_query_matches_nothing(registrar):
    """An empty box is a question nobody asked, not a request for the whole table.

    This keeps D-040 true in the layer below the view. If a blank query returned
    everything, the search page would be a record directory whatever decorator sat on
    the view above it.
    """
    make_record(registrar)

    assert not search.find("").exists()
    assert not search.find("   ").exists()


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_matches_on_holder_name_case_insensitively(registrar):
    make_record(registrar, holder_name="Tendai Moyo")
    make_record(registrar, holder_name="Rutendo Chuma")

    results = search.find("tendai")

    assert [record.holder_name for record in results] == ["Tendai Moyo"]


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_matches_on_institution(registrar):
    make_record(registrar, institution="Midlands State University")
    make_record(registrar, institution="University of Zimbabwe")

    results = search.find("Midlands")

    assert [record.institution for record in results] == ["Midlands State University"]


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_matches_a_partial_certificate_id_typed_in_lower_case(registrar):
    """The realistic case: a fragment read off a photographed or damaged document.

    Lower case on purpose. The certificate ID arm runs the query through
    verification.normalise_certificate_id, so the search box and the verification box
    treat a typed identifier identically - the same string must not find a record in
    one and miss it in the other.
    """
    record = make_record(registrar)
    fragment = record.certificate_id[-4:].lower()

    assert list(search.find(fragment)) == [record]


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_a_term_matching_nothing_returns_nothing(registrar):
    make_record(registrar, holder_name="Tendai Moyo")

    assert not search.find("Farai").exists()


# --- Access control -----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_anonymous_search_is_redirected_to_login(client):
    """D-040 in one assertion.

    Built as REQ-F-009 was originally worded, this request would have returned results.
    """
    search_url = reverse("qualifications:search")

    response = client.get(search_url, {"q": "Moyo"})

    assert response.status_code == 302
    assert reverse("login") in response.url
    assert search_url in response.url


@pytest.mark.integration
@pytest.mark.req("REQ-F-010")
@pytest.mark.django_db
def test_anonymous_record_detail_is_redirected_to_login(client, registrar):
    """A record detail URL is not an unauthenticated lookup endpoint.

    `client` and `registrar` rather than `registrar_client`: the conftest fixture IS
    the client fixture with force_login applied, so asking for both would make this
    request authenticated while the test believed it was not.
    """
    record = make_record(registrar)
    detail_url = reverse("qualifications:record_detail", args=[record.certificate_id])

    response = client.get(detail_url)

    assert response.status_code == 302
    assert reverse("login") in response.url


# --- The search page ----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_search_page_with_no_query_reports_nothing_either_way(registrar_client):
    """Three states, not two. Arriving at the page is not a search that failed."""
    response = registrar_client.get(reverse("qualifications:search"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'name="q"' in content
    assert "No records match" not in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_search_lists_matches_and_links_to_each_record(registrar_client, registrar):
    """A result list whose rows link nowhere is not a retrieval capability.

    This assertion is the join between REQ-F-009 and REQ-F-010, and it is why the two
    were built as one unit of work rather than two.
    """
    record = make_record(registrar, holder_name="Tendai Moyo")
    make_record(registrar, holder_name="Rutendo Chuma")
    detail_url = reverse("qualifications:record_detail", args=[record.certificate_id])

    response = registrar_client.get(reverse("qualifications:search"), {"q": "Moyo"})

    assert response.status_code == 200
    content = response.content.decode()
    assert record.certificate_id in content
    assert "Rutendo Chuma" not in content
    assert detail_url in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_search_with_no_matches_says_so(registrar_client, registrar):
    make_record(registrar, holder_name="Tendai Moyo")

    response = registrar_client.get(reverse("qualifications:search"), {"q": "Farai"})

    assert response.status_code == 200
    assert "No records match" in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-009")
@pytest.mark.django_db
def test_a_truncated_result_set_admits_it(registrar_client, registrar, monkeypatch):
    """A capped list that does not say it is capped is worse than no search at all.

    MAX_RESULTS is monkeypatched rather than exercised at its real value of 50, because
    creating fifty-one signed records to assert one sentence of copy would put fifty-one
    HMAC computations into every future run of this suite for no extra coverage. The
    view reads the attribute at call time, so patching it takes the same branch.
    """
    monkeypatch.setattr(search, "MAX_RESULTS", 2)
    for index in range(3):
        make_record(registrar, holder_name=f"Tendai Moyo {index}")

    response = registrar_client.get(reverse("qualifications:search"), {"q": "Moyo"})

    assert response.status_code == 200
    assert "Showing the first 2 matches" in response.content.decode()


# --- The record detail page ---------------------------------------------------------


@pytest.mark.integration
@pytest.mark.req("REQ-F-010")
@pytest.mark.django_db
def test_record_detail_shows_the_registered_fields(registrar_client, registrar):
    record = make_record(registrar)

    response = registrar_client.get(
        reverse("qualifications:record_detail", args=[record.certificate_id])
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert record.certificate_id in content
    assert record.holder_name in content
    assert record.institution in content
    assert record.signature in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-010")
@pytest.mark.django_db
def test_an_unknown_certificate_id_is_a_404(registrar_client):
    response = registrar_client.get(
        reverse("qualifications:record_detail", args=["QVS-NOPE-NOPE-NOPE-NOPE"])
    )

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.req("REQ-F-010")
@pytest.mark.django_db
def test_a_lower_case_certificate_id_in_the_url_still_resolves(
    registrar_client, registrar
):
    """A false negative is the failure this system can least afford.

    Links the application generates already carry the canonical form. This is for the
    address bar, where somebody has retyped an identifier by hand.
    """
    record = make_record(registrar)

    response = registrar_client.get(
        reverse("qualifications:record_detail", args=[record.certificate_id.lower()])
    )

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.req("REQ-F-010")
@pytest.mark.django_db
def test_neither_page_writes_an_audit_event(registrar_client, registrar):
    """Retrieval is not verification, and the audit trail keeps its meaning.

    verification.py guarantees that every verification attempt is audited only because
    its single caller writes the event. Neither page here calls it. If a later change
    makes the detail page verify, this test fails and the obligation is re-decided
    rather than silently inherited - which is the whole point of pinning it.
    """
    record = make_record(registrar)

    registrar_client.get(reverse("qualifications:search"), {"q": "Moyo"})
    registrar_client.get(
        reverse("qualifications:record_detail", args=[record.certificate_id])
    )

    assert not AuditEvent.objects.exists()
