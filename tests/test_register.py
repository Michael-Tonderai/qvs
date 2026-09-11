# tests/test_register.py
#
# REQ-F-003 through the request cycle - URL resolution, the form, the view, the model
# and the template together. tests/test_qualification_model.py proves the record is
# built correctly; these prove a registrar can actually cause one to exist.

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from qualifications import signing
from qualifications.models import Qualification

VALID_SUBMISSION = {
    "holder_name": "Tendai Moyo",
    "institution": "Midlands State University",
    "qualification_title": "BSc Honours in Information Systems",
    "award_date": "2024-11-15",
}


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_registrar_sees_the_register_form(registrar_client):
    """The form renders, and it does not offer the fields the system owns.

    Asserting the absence of the certificate ID and signature inputs, not just the
    presence of the form. Those two are editable=False on the model so ModelForm never
    builds them - this is the test that notices if that ever changes.
    """
    response = registrar_client.get(reverse("qualifications:register"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'name="holder_name"' in content
    assert 'name="certificate_id"' not in content
    assert 'name="signature"' not in content


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_registering_creates_a_signed_record(registrar_client, registrar):
    """The end that matters: a valid submission produces a verifiable record."""
    response = registrar_client.post(
        reverse("qualifications:register"), data=VALID_SUBMISSION
    )

    assert response.status_code == 302
    qualification = Qualification.objects.get()
    assert qualification.holder_name == "Tendai Moyo"
    assert qualification.issued_by == registrar
    assert signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    )


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_registering_redirects_to_a_page_showing_the_certificate_id(registrar_client):
    """Post, redirect, get - and the registrar lands on the identifier they need.

    The redirect is not decoration. Rendering the confirmation straight from the POST
    would mean a browser refresh re-submits the form and issues a second certificate
    for the same qualification.
    """
    response = registrar_client.post(
        reverse("qualifications:register"), data=VALID_SUBMISSION, follow=True
    )

    assert response.status_code == 200
    certificate_id = Qualification.objects.get().certificate_id
    assert certificate_id in response.content.decode()


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_a_future_award_date_is_refused(registrar_client):
    """The validation rule holds and nothing is stored when it fires.

    A week out, comfortably past the one day of tolerance the form allows for the gap
    between UTC and local time.
    """
    submission = dict(VALID_SUBMISSION)
    submission["award_date"] = (timezone.localdate() + timedelta(days=7)).isoformat()

    response = registrar_client.post(
        reverse("qualifications:register"), data=submission
    )

    assert response.status_code == 200
    assert not Qualification.objects.exists()
    assert "future" in response.content.decode().lower()


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_a_submission_cannot_dictate_its_own_certificate_id(registrar_client):
    """A crafted POST carrying a certificate ID and signature is ignored.

    The template does not offer these inputs, but a template is not a control. Anyone
    can add fields to a form before submitting it, so the guarantee has to hold against
    a request that was never rendered by this system.
    """
    submission = dict(VALID_SUBMISSION)
    submission["certificate_id"] = "QVS-AAAA-AAAA-AAAA-AAAA"
    submission["signature"] = "0" * 64

    registrar_client.post(reverse("qualifications:register"), data=submission)

    qualification = Qualification.objects.get()
    assert qualification.certificate_id != "QVS-AAAA-AAAA-AAAA-AAAA"
    assert qualification.signature != "0" * 64
    assert signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    )


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
@pytest.mark.django_db
def test_two_registrations_produce_two_records(registrar_client):
    """Registering twice does not overwrite the first record."""
    registrar_client.post(reverse("qualifications:register"), data=VALID_SUBMISSION)
    registrar_client.post(reverse("qualifications:register"), data=VALID_SUBMISSION)

    identifiers = set(Qualification.objects.values_list("certificate_id", flat=True))

    assert len(identifiers) == 2
