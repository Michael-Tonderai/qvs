# tests/test_authentication.py
#
# REQ-F-004 - an unauthenticated user cannot register or edit records.
#
# Every assertion here is about HTTP behaviour rather than about what a template
# renders. Hiding a link is not access control, and a test that checks for the absence
# of a button would pass against a system that happily accepts an anonymous POST.

import pytest
from django.test import Client
from django.urls import NoReverseMatch, reverse

from qualifications.models import Qualification
from tests.conftest import REGISTRAR_PASSWORD, REGISTRAR_USERNAME

VALID_SUBMISSION = {
    "holder_name": "Tendai Moyo",
    "institution": "Midlands State University",
    "qualification_title": "BSc Honours in Information Systems",
    "award_date": "2024-11-15",
}


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
@pytest.mark.django_db
def test_anonymous_get_is_redirected_to_login(client):
    """An anonymous visitor is sent to sign in, carrying where they were going.

    A redirect rather than a 403. Someone reaching the register page while signed out
    is far more likely to be a legitimate registrar than an attacker, and Django's
    built-in behaviour returns them to the page they wanted once they authenticate. A
    403 would be defensible but would need a reason; taking the framework default does
    not.
    """
    register_url = reverse("qualifications:register")

    response = client.get(register_url)

    assert response.status_code == 302
    assert reverse("login") in response.url
    assert register_url in response.url


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
@pytest.mark.django_db
def test_anonymous_post_creates_nothing(client):
    """The guard is on the view, so a direct POST never reaches the model.

    The assertion that carries the requirement. Everything else about REQ-F-004 is
    convenience; this is the line between a system with access control and a system
    with a hidden button.
    """
    response = client.post(reverse("qualifications:register"), data=VALID_SUBMISSION)

    assert response.status_code == 302
    assert not Qualification.objects.exists()


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
@pytest.mark.django_db
def test_the_confirmation_page_is_not_public(registrar_client):
    """The receipt is behind login too.

    REQ-F-005 owns the page that answers VERIFIED, NOT FOUND or TAMPERED for anyone
    holding a certificate ID. Leaving this one open would ship an unauthenticated
    record lookup ahead of the requirement that is supposed to define how lookups
    behave.

    The anonymous client is built here rather than taken from the `client` fixture, and
    that is load-bearing. `registrar_client` is the `client` fixture with force_login
    called on it, so a test asking for both receives the same object twice and the
    supposedly anonymous request arrives authenticated - which is how the first version
    of this test passed a signed-in browser off as a member of the public. A fresh
    Client cannot be aliased to anything.
    """
    registrar_client.post(reverse("qualifications:register"), data=VALID_SUBMISSION)
    certificate_id = Qualification.objects.get().certificate_id
    url = reverse(
        "qualifications:register_done",
        kwargs={"certificate_id": certificate_id},
    )

    response = Client().get(url)

    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
@pytest.mark.django_db
def test_a_signed_in_registrar_reaches_the_form(registrar_client):
    """The guard lets the right people through.

    Worth its own test: a view that refuses everyone also passes every test above.
    """
    response = registrar_client.get(reverse("qualifications:register"))

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
@pytest.mark.django_db
def test_signing_in_through_the_login_form_works(client, registrar):
    """The real login path, exercised once.

    Other tests use force_login so that a failure points at what they are testing. This
    one proves the route those tests take a shortcut around actually exists and works -
    LOGIN_URL resolves, the template renders, and a valid submission authenticates.
    """
    response = client.post(
        reverse("login"),
        data={"username": REGISTRAR_USERNAME, "password": REGISTRAR_PASSWORD},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.unit
@pytest.mark.req("REQ-F-004")
def test_no_edit_route_exists():
    """ "Cannot edit" is satisfied by absence, and absence is asserted.

    A qualification is signed at issue; altering one is what REQ-F-006 exists to
    detect, not something the system should offer. This test keeps that honest - if an
    edit view is ever added without a requirement behind it, the failure lands here
    rather than in a code review nobody has time for.
    """
    for name in ("qualifications:edit", "qualifications:update"):
        with pytest.raises(NoReverseMatch):
            reverse(name, kwargs={"certificate_id": "QVS-2345-6789-ABCD-EFGH"})
