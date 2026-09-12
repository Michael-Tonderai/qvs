# qualifications/management/commands/seed_demo.py
#
# Creates the demonstration registrar and demonstration records that make the deployed
# system usable by someone who has never seen it before.
#
# WHY THIS EXISTS AT ALL. Under D-036 the free instance has no persistent disk and no
# shell. The database is empty on every container start and resets on every restart
# and redeploy, so there is no moment at which a human could create a user by hand and
# expect it to still be there. Seeding therefore cannot be a one-time setup step; it
# has to happen on every boot, which is why this is a management command called from
# tools/docker-entrypoint.sh rather than something run once from a terminal.
#
# WHY NOT A DATA MIGRATION, which would run on `migrate` with no entrypoint change: a
# migration applies everywhere the schema applies, so demonstration data would land in
# the test database, in the local database and in any future real deployment, and the
# only way back out would be a second migration. A command is opt-in at the point of
# call, and its opt-in is visible in the entrypoint rather than buried in a migration
# directory nobody reads after it is written.
#
# THE SWITCH AND THE CREDENTIAL ARE THE SAME VARIABLE. QVS_DEMO_PASSWORD absent means
# do nothing. That is deliberate: a separate QVS_SEED_DEMO flag would be a second
# setting that can disagree with the first, and a seed that runs without a password to
# set is not a state worth having. It is the same argument D-012 and D-018 make for
# removing an exception rather than managing one - there is no configuration in which
# this command half-runs.
#
# REQ-N-002 has no exception for demonstration credentials. The password is read from
# the environment and appears in no tracked file. render.yaml declares the variable
# with `sync: false`, so the platform holds the value and the repository never sees it.

import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from qualifications.models import Qualification

PASSWORD_VARIABLE = "QVS_DEMO_PASSWORD"

# A plain, active, non-staff user. The register view is guarded by login_required and
# nothing more (REQ-F-004), so this account holds exactly the rights needed to
# demonstrate registration and none beyond it. Staff or superuser would additionally
# open the Django admin to anyone holding this password on a public URL, which is a
# real exposure bought for no demonstrable benefit - the admin is not part of what the
# video shows.
DEMO_USERNAME = "registrar"

# D-037. One record carries a fixed identifier so that the technical report, the
# slides and the video script can name a certificate ID that survives a restart. It is
# drawn from signing.CERTIFICATE_ID_ALPHABET and matches the issued format exactly, so
# it is a legal ID rather than a special-cased string the verification path has to know
# about - and it reads as a fixture rather than passing itself off as an issued
# credential.
FIXED_CERTIFICATE_ID = "QVS-TEST-CASE-2345-6789"

# The other two take system-issued random identifiers. Showing all three on the same
# instance means the normal issuing path is visible beside the fixed one, so the fixed
# ID cannot be mistaken for how this system names records.
DEMO_RECORDS = (
    {
        "certificate_id": FIXED_CERTIFICATE_ID,
        "holder_name": "Tendai Marimo",
        "institution": "Midlands State University",
        "qualification_title": "Master of Commerce in Information Systems Management",
        "award_date": date(2024, 11, 22),
    },
    {
        "certificate_id": "",
        "holder_name": "Rutendo Chikafu",
        "institution": "University of Zimbabwe",
        "qualification_title": "Bachelor of Science Honours in Computer Science",
        "award_date": date(2023, 6, 15),
    },
    {
        "certificate_id": "",
        "holder_name": "Farai Nyathi",
        "institution": "Harare Polytechnic",
        "qualification_title": "National Diploma in Accountancy",
        "award_date": date(2022, 9, 30),
    },
)


class Command(BaseCommand):
    help = (
        "Create the demonstration registrar and demonstration qualification records. "
        f"Does nothing unless {PASSWORD_VARIABLE} is set."
    )

    def handle(self, *args, **options) -> None:
        password = os.environ.get(PASSWORD_VARIABLE, "").strip()
        if not password:
            # Not an error, and deliberately not raised as one. CI runs migrations, and
            # a developer runs them locally, and neither wants demonstration data. A
            # command that failed here would make the entrypoint's guard load-bearing
            # for the ordinary case rather than for the exceptional one.
            self.stdout.write(
                f"{PASSWORD_VARIABLE} is not set - skipping demonstration seed."
            )
            return

        with transaction.atomic():
            user, user_created = self._ensure_registrar(password)
            created_records = self._ensure_records(user)

        if user_created:
            self.stdout.write(f"Created demonstration registrar '{DEMO_USERNAME}'.")
        else:
            self.stdout.write(
                f"Demonstration registrar '{DEMO_USERNAME}' already present."
            )

        if created_records:
            for qualification in created_records:
                self.stdout.write(
                    f"Created {qualification.certificate_id} "
                    f"({qualification.holder_name})."
                )
        else:
            self.stdout.write("Demonstration records already present.")

        # Printed on every run, created or not, because the container log is the only
        # place anyone can read this back from a platform with no shell. The fixed ID
        # is the one to type on camera.
        self.stdout.write(f"Verify this ID on the public page: {FIXED_CERTIFICATE_ID}")

    def _ensure_registrar(self, password: str) -> tuple[object, bool]:
        """Return the demonstration registrar, creating it if it is absent.

        The password is reconciled rather than merely set once. On the ephemeral disk
        this account is always newly created, so the branch below rarely fires - but on
        any instance that does keep its database, rotating the value in the platform
        dashboard and restarting is the only mechanism available for changing this
        password, and an account that ignored the new value would silently keep the old
        one. check_password rather than a blind set_password on every run, so a run
        that changes nothing really does change nothing.
        """
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )

        if created or not user.check_password(password):
            user.set_password(password)
            user.save(update_fields=["password"])

        return user, created

    def _ensure_records(self, user) -> list[Qualification]:
        """Create any demonstration record that is not already present.

        Idempotency is keyed differently for the two kinds of record, and it has to be.
        The fixed record is identified by its certificate ID, which is the whole point
        of it having one. The others cannot be, because their IDs are minted at save
        time and are different on every boot - so they are identified by the three
        substantive fields a registrar would have typed. That is a weaker key, and it
        is the correct one: two records differing only in award date are two different
        qualifications, but for seed data the holder, the institution and the title are
        enough to say "this fixture already exists".

        Records are created one at a time through save() rather than bulk_create.
        bulk_create does not call save(), so it would insert rows with no certificate
        ID, no issued_at and no signature - three empty columns that would then verify
        as TAMPERED. D-029 documents the ordering inside save() that this depends on.
        """
        created: list[Qualification] = []

        for record in DEMO_RECORDS:
            fields = dict(record)
            certificate_id = fields.pop("certificate_id")

            if certificate_id:
                if Qualification.objects.filter(certificate_id=certificate_id).exists():
                    continue
            elif Qualification.objects.filter(
                holder_name=fields["holder_name"],
                institution=fields["institution"],
                qualification_title=fields["qualification_title"],
            ).exists():
                continue

            qualification = Qualification(
                certificate_id=certificate_id,
                issued_by=user,
                **fields,
            )
            # save() mints an identifier only when the field is empty, so supplying one
            # needs no special path and no model change. The signature is computed over
            # whichever ID is in place by the time it runs, so the fixed record is
            # signed exactly as a registered one would be and is just as tamper-evident.
            qualification.save()
            created.append(qualification)

        return created
