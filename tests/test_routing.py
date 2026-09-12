# tests/test_routing.py
#
# The root redirect. It serves no requirement, so these tests carry no req marker -
# they will not appear in the traceability matrix, and they should not.
#
# That stays true now that the root points at the verification page. The redirect is
# convenience, not capability: REQ-F-005 is satisfied by /verify/ itself, and marking
# these tests would let the matrix count a URL configuration as evidence that the
# system can verify a qualification. It cannot. Delete the redirect and REQ-F-005 is
# still met; delete the view and no redirect saves it.
#
# Deliberately kept out of test_register.py and test_verification.py. Those modules are
# about capabilities; this one is about wiring, and merging them would make the next
# person hunt for a routing assertion inside a feature suite.

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.integration
def test_root_redirects_to_verification():
    """The empty path resolves and sends the visitor somewhere real.

    The destination changed from the register page when REQ-F-005 landed. The front
    door of a verification service should open onto verification: most people arriving
    at the root hold a certificate and no account, and the register page answered them
    with a login form for credentials they will never have.

    A fresh Client rather than the `client` fixture, and no database. The redirect is
    resolved by the URL configuration before any view runs, so this test needs neither.
    """
    response = Client().get("/")

    assert response.status_code == 302
    assert response.url == reverse("qualifications:verify")


@pytest.mark.integration
def test_the_root_redirect_is_temporary():
    """302, not 301, and the distinction is not pedantry.

    A permanent redirect is cached by the browser and survives a change to the server,
    so taking one back means asking every visitor who ever hit it to clear their cache.
    This destination has already changed once - it pointed at the register page until
    REQ-F-005 gave the public something better - and REQ-F-009 search and REQ-F-010
    record detail may yet give the root a page of its own. A destination with a history
    of moving is exactly the kind that must not be cached permanently.
    """
    response = Client().get("/")

    assert response.status_code == 302


@pytest.mark.integration
def test_an_anonymous_visitor_to_the_root_reaches_a_usable_page():
    """Following the chain: root, verification form, done. No login wall.

    This assertion inverted when the destination changed, and the inversion is the
    point. Previously an anonymous visitor was passed root, register, login and landed
    on a form they could not use without an account. Now they land on the page that
    answers the question they came with.

    Asserting the absence of the login redirect as well as the presence of the form,
    because a chain that merely ends in a 200 would also be satisfied by a login page
    rendering successfully.
    """
    response = Client().get("/", follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse("qualifications:verify")
    assert reverse("login") not in response.redirect_chain[-1][0]
    assert b"Verify a qualification" in response.content
