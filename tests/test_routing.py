# tests/test_routing.py
#
# The root redirect. It serves no requirement, so these tests carry no req marker -
# they will not appear in the traceability matrix, and they should not. It is a defect
# fix: the front door of the system answered 404, which a visitor and a marker both hit
# before anything else.
#
# Deliberately kept out of test_register.py. That module is about registering
# qualifications; this is about a URL configuration, and merging the two would make the
# next person hunt for a routing assertion inside a feature suite.

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.integration
def test_root_redirects_to_register():
    """The empty path resolves and sends the visitor somewhere real.

    A fresh Client rather than the `client` fixture, and no database. The redirect is
    resolved by the URL configuration before any view runs, so this test needs neither.
    """
    response = Client().get("/")

    assert response.status_code == 302
    assert response.url == reverse("qualifications:register")


@pytest.mark.integration
def test_the_root_redirect_is_temporary():
    """302, not 301, and the distinction is not pedantry.

    A permanent redirect is cached by the browser and survives a change to the server,
    so taking one back means asking every visitor who ever hit it to clear their cache.
    This destination is expected to change - REQ-F-009 and REQ-F-010 will give the root
    a page of its own, and REQ-F-005 verification is what an unauthenticated visitor
    actually wants. Sending the public to a login wall is right only until there is a
    public page to send them to.
    """
    response = Client().get("/")

    assert response.status_code == 302


@pytest.mark.integration
@pytest.mark.django_db
def test_an_anonymous_visitor_to_the_root_ends_at_login():
    """Following the chain: root, register, login.

    The two hops matter together. The redirect is not an authentication bypass - it
    lands on a guarded view, and an anonymous visitor is passed straight on to the
    login page rather than being shown a form they cannot use.
    """
    response = Client().get("/", follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[-1][0].startswith(reverse("login"))
