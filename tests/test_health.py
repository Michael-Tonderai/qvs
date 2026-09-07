# tests/test_health.py
#
# The first test. Its job is not to prove the health endpoint is interesting - it is
# to prove the whole toolchain is wired: pytest finds the tests, pytest-django loads
# config.settings, the URL configuration resolves, the view returns, and coverage
# measures it. If this passes, every later test failure is about the code under test.

import pytest
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.req("REQ-N-003")
def test_health_endpoint_reports_ok(client):
    """The health endpoint answers 200 with a JSON ok status.

    Integration rather than unit: it goes through URL resolution, middleware and the
    response cycle, not just the view callable. That is the part worth proving today.
    """
    response = client.get(reverse("qualifications:health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "qvs"}


@pytest.mark.unit
@pytest.mark.req("REQ-N-003")
def test_health_url_is_reversible():
    """The route is registered under its namespaced name.

    Templates and tests refer to view names rather than literal paths, so this is the
    assumption everything else rests on. It fails loudly if the namespace is ever
    dropped from qualifications/urls.py.
    """
    assert reverse("qualifications:health") == "/health/"
