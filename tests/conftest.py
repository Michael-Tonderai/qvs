# tests/conftest.py
#
# Shared fixtures. A registrar is needed by every test that touches the register view,
# and building one inline in each test would put the same four lines in three files and
# make a change to the user model a find-and-replace.

import pytest

REGISTRAR_USERNAME = "registrar"

# A throwaway password for tests only. It is not a secret in any meaningful sense - it
# exists so Django's authentication machinery has something to hash - and it never
# leaves this repository or reaches a running deployment. REQ-N-002 concerns keys and
# credentials that grant access to something; this grants access to a database created
# and destroyed inside a single test run.
REGISTRAR_PASSWORD = "test-only-not-a-real-credential"


@pytest.fixture
def registrar(django_user_model):
    """A user who is allowed to register qualifications.

    "Authorised" in REQ-F-004 means authenticated. There is no registrar role and no
    permission check, because no requirement asks for one and CLAUDE.md Section 8
    fences role hierarchies. If that distinction is ever needed it becomes a new
    requirement, and this fixture is where it will show up first.
    """
    return django_user_model.objects.create_user(
        username=REGISTRAR_USERNAME,
        password=REGISTRAR_PASSWORD,
    )


@pytest.fixture
def registrar_client(client, registrar):
    """A test client already signed in as the registrar.

    force_login rather than posting to the login form. The tests that use this fixture
    are about registering qualifications, and routing them through a login round trip
    would make them fail for a second, unrelated reason. tests/test_authentication.py
    exercises the real login path, once, where that is the thing under test.

    HAZARD, and it has already cost one debugging round: this fixture IS the `client`
    fixture, with force_login called on it. A test that asks for both `client` and
    `registrar_client` receives the same object twice, and the request it believes is
    anonymous arrives authenticated. That failure is silent in the general case - the
    test passes while asserting nothing - and it only surfaced here because the
    assertion happened to be about a redirect status.

    Build a fresh `django.test.Client()` when a test needs a genuinely anonymous
    browser alongside a signed-in one. REQ-F-005 adds public verification tests, which
    is exactly the shape that walks into this.
    """
    client.force_login(registrar)
    return client
