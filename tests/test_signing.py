# tests/test_signing.py
#
# Unit tests for REQ-F-001 and REQ-F-002.
#
# No database, no request cycle, no fixtures beyond pytest-django's `settings`. Every
# test carries `unit` and a `req` marker so tools/traceability.py can generate the
# requirements traceability matrix from the suite rather than from a hand-maintained
# table (D-004).
#
# The signing key is set through the `settings` fixture rather than read from the
# environment. A test that depends on a shell variable passes on the machine that
# happened to export it and fails in CI, and the whole point of these tests is that
# they mean the same thing in both places.

import pytest
from django.core.exceptions import ImproperlyConfigured

from qualifications.signing import (
    CERTIFICATE_ID_ALPHABET,
    canonical_payload,
    new_certificate_id,
    sign,
    verify_signature,
)

TEST_KEY = "test-signing-key-not-used-anywhere-real"

SAMPLE = {
    "certificate_id": "QVS-2345-6789-ABCD-EFGH",
    "holder_name": "Tendai Moyo",
    "institution": "Midlands State University",
    "qualification": "BSc Information Systems",
    "awarded_on": "2024-11-15",
}


@pytest.fixture
def signing_key(settings):
    """Give every signing test a known key, independent of the shell."""
    settings.QVS_SIGNING_KEY = TEST_KEY
    return TEST_KEY


# --- REQ-F-001 ---------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.req("REQ-F-001")
def test_certificate_id_has_the_documented_shape():
    certificate_id = new_certificate_id()
    parts = certificate_id.split("-")

    assert parts[0] == "QVS"
    assert len(parts) == 5
    assert all(len(part) == 4 for part in parts[1:])


@pytest.mark.unit
@pytest.mark.req("REQ-F-001")
def test_certificate_id_uses_only_unambiguous_characters():
    """The exclusions are the requirement, not a formatting preference.

    A generator that quietly started emitting I, L, O, U, 0 or 1 would still look
    correct and would produce IDs that people mistype off a printed certificate.
    """
    body = new_certificate_id().replace("QVS-", "").replace("-", "")

    assert all(character in CERTIFICATE_ID_ALPHABET for character in body)
    assert not set(body) & set("ILOU01")


@pytest.mark.unit
@pytest.mark.req("REQ-F-001")
def test_certificate_ids_do_not_repeat():
    """Not a proof of uniqueness - a collision here would mean the entropy source is
    broken rather than that we were unlucky. At about 78 bits, 500 draws colliding is
    not a thing that happens by chance.
    """
    generated = {new_certificate_id() for _ in range(500)}

    assert len(generated) == 500


# --- REQ-F-002 ---------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_canonical_payload_ignores_field_order():
    reordered = dict(reversed(list(SAMPLE.items())))

    assert canonical_payload(SAMPLE) == canonical_payload(reordered)


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_canonical_payload_separates_fields_unambiguously():
    """A value containing the separator characters must not be able to impersonate a
    different set of fields. This is the forgery that needs no key.
    """
    honest = {"holder_name": "Tendai Moyo", "institution": "MSU"}
    crafted = {"holder_name": 'Tendai Moyo","institution":"MSU', "institution": ""}

    assert canonical_payload(honest) != canonical_payload(crafted)


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_signature_is_stable_for_the_same_fields(signing_key):
    assert sign(SAMPLE) == sign(dict(SAMPLE))


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_signature_changes_when_any_field_changes(signing_key):
    altered = dict(SAMPLE, holder_name="Tendai Moyoo")

    assert sign(SAMPLE) != sign(altered)


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_signature_changes_with_the_key(settings):
    settings.QVS_SIGNING_KEY = TEST_KEY
    under_first_key = sign(SAMPLE)

    settings.QVS_SIGNING_KEY = TEST_KEY + "-different"

    assert sign(SAMPLE) != under_first_key


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_verify_accepts_the_signature_it_issued(signing_key):
    assert verify_signature(SAMPLE, sign(SAMPLE)) is True


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_verify_rejects_a_signature_from_different_fields(signing_key):
    signature_for_other_record = sign(dict(SAMPLE, holder_name="Someone Else"))

    assert verify_signature(SAMPLE, signature_for_other_record) is False


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
@pytest.mark.parametrize("signature", ["", None])
def test_verify_rejects_a_missing_signature(signing_key, signature):
    """An unsigned record is tampered with, not malformed. REQ-F-005 has three answers
    and "raised an exception" is not one of them.
    """
    assert verify_signature(SAMPLE, signature) is False


@pytest.mark.unit
@pytest.mark.req("REQ-F-002")
def test_signing_without_a_key_fails_loudly(settings):
    settings.QVS_SIGNING_KEY = ""

    with pytest.raises(ImproperlyConfigured):
        sign(SAMPLE)
