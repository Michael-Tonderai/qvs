# tests/test_seed_demo.py
#
# Tests for the demonstration seed (issue #22, D-037).
#
# The command exists to make the deployed instance usable by someone who has never
# seen it, on a platform whose database is empty at every boot. Three properties have
# to hold, and each of them fails silently if it does not:
#
#   - It does nothing at all without QVS_DEMO_PASSWORD, or demonstration data appears
#     in CI and in the local database.
#   - Running it twice creates nothing the second time, because it runs on every
#     container start and a platform restart must not multiply the records.
#   - The fixed-ID record is genuinely signed, or the one certificate ID we print in
#     the report verifies as TAMPERED in front of an assessor.
#
# All of these are integration tests. The command is a database-touching entry point
# and there is nothing useful left of it once the database is taken away.

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from qualifications import signing, verification
from qualifications.management.commands.seed_demo import (
    DEMO_RECORDS,
    DEMO_USERNAME,
    FIXED_CERTIFICATE_ID,
    PASSWORD_VARIABLE,
)
from qualifications.models import Qualification

DEMO_PASSWORD = "seed-test-only-not-a-real-credential"


@pytest.fixture
def seeded(db, monkeypatch):
    """Run the command once with the password variable set.

    monkeypatch rather than os.environ assignment, so the variable is removed again
    whatever the test does. A leaked QVS_DEMO_PASSWORD would make the skip-path test
    pass for the wrong reason depending on test ordering, which is the kind of failure
    that only appears when somebody runs the suite with -p no:randomly six weeks later.
    """
    monkeypatch.setenv(PASSWORD_VARIABLE, DEMO_PASSWORD)
    call_command("seed_demo")


@pytest.mark.integration
@pytest.mark.req("REQ-N-002")
def test_seed_does_nothing_without_the_password_variable(db, monkeypatch):
    """No variable, no user, no records, no error.

    This is the property that keeps demonstration data out of CI and off the
    development machine, and it is also why there is no second QVS_SEED_DEMO flag: the
    credential and the switch are one variable, so there is no configuration in which
    the command half-runs.

    What this does NOT prove, stated rather than implied: REQ-N-002 is about secrets
    reaching the repository, and no test can establish that. What it establishes is
    narrower and still worth having - the command has no literal password fallback, so
    there is no value for anyone to commit.
    """
    monkeypatch.delenv(PASSWORD_VARIABLE, raising=False)

    call_command("seed_demo")

    assert not get_user_model().objects.filter(username=DEMO_USERNAME).exists()
    assert Qualification.objects.count() == 0


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
def test_seed_creates_the_registrar_and_every_record(seeded):
    """One registrar and one record per entry in DEMO_RECORDS."""
    user = get_user_model().objects.get(username=DEMO_USERNAME)

    assert user.is_active
    assert Qualification.objects.count() == len(DEMO_RECORDS)
    assert set(Qualification.objects.values_list("issued_by", flat=True)) == {user.pk}


@pytest.mark.integration
@pytest.mark.req("REQ-F-004")
def test_the_registrar_can_authenticate_with_the_supplied_password(seeded):
    """The password in the environment is the password the account holds.

    The deployed account is only reachable through the login form, and a registrar
    whose password does not match what was put in the platform dashboard is a demo
    that cannot be demonstrated. It also pins the non-staff decision: this account is
    for registering qualifications, not for reaching the Django admin on a public URL.
    """
    user = get_user_model().objects.get(username=DEMO_USERNAME)

    assert user.check_password(DEMO_PASSWORD)
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.integration
@pytest.mark.req("REQ-F-003")
def test_running_the_seed_twice_creates_nothing_the_second_time(seeded):
    """Idempotent, because the entrypoint calls it on every container start.

    The two kinds of record are keyed differently and both keys are exercised here:
    the fixed record by its certificate ID, the others by holder, institution and
    title. A regression in either would show up as a growing record count on a platform
    that happened to keep its database between restarts.
    """
    before = Qualification.objects.count()
    before_ids = set(Qualification.objects.values_list("certificate_id", flat=True))

    call_command("seed_demo")

    assert Qualification.objects.count() == before
    assert set(Qualification.objects.values_list("certificate_id", flat=True)) == (
        before_ids
    )
    assert get_user_model().objects.filter(username=DEMO_USERNAME).count() == 1


@pytest.mark.integration
@pytest.mark.req("REQ-F-005")
def test_the_fixed_record_verifies_through_the_public_path(seeded):
    """The one certificate ID that goes into the report actually verifies.

    Through verification.verify rather than by re-signing inline, because the assessor
    will reach this record through the public page and that page is what this has to
    predict. A fixed identifier changes nothing about the signature - D-029's ordering
    inside save() signs whichever ID is in place - and this test is what makes that
    claim checkable rather than argued.
    """
    result = verification.verify(FIXED_CERTIFICATE_ID)

    assert result.is_verified
    assert result.qualification is not None
    assert result.qualification.certificate_id == FIXED_CERTIFICATE_ID


@pytest.mark.unit
@pytest.mark.req("REQ-F-001")
def test_the_fixed_certificate_id_is_a_legal_issued_identifier():
    """The fixed ID is in the format and the alphabet this system issues.

    D-037 accepts a guessable identifier for one demonstration record. It does not
    accept an identifier the system could never have produced: a string containing O
    or 1 would be visibly foreign beside a real one, and normalise_certificate_id
    deliberately does not repair look-alike characters, so a typed O would simply never
    match.

    No database, so this one is a unit test - it is a statement about a constant.
    """
    prefix, *groups = FIXED_CERTIFICATE_ID.split("-")

    assert prefix == signing.CERTIFICATE_ID_PREFIX
    assert len(groups) == signing.CERTIFICATE_ID_GROUPS
    assert all(len(group) == signing.CERTIFICATE_ID_GROUP_SIZE for group in groups)
    assert set("".join(groups)) <= set(signing.CERTIFICATE_ID_ALPHABET)
    assert FIXED_CERTIFICATE_ID == verification.normalise_certificate_id(
        FIXED_CERTIFICATE_ID
    )
