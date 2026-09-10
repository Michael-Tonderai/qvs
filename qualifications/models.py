# qualifications/models.py
#
# REQ-F-003 - an authorised user can register a qualification record.
#
# The model owns three things the rest of the system depends on: the unique constraint
# on certificate_id, the exact mapping of fields that gets signed, and the ordering of
# work inside save() that makes a signature reproducible.

from django.conf import settings
from django.db import models
from django.utils import timezone

from qualifications import signing

# "QVS" + 4 groups of 4 characters + 4 hyphens. 23 characters. Written as a literal
# rather than derived from signing.py's constants because a migration must record a
# fixed column width - a max_length computed at import time would change silently when
# the constants change, and the mismatch would surface as a database error at issue
# rather than as a failing test. tests/test_qualification_model.py asserts the two
# agree, so the coupling is checked rather than assumed.
CERTIFICATE_ID_MAX_LENGTH = 23

# HMAC-SHA256 rendered as hex is always 64 characters.
SIGNATURE_MAX_LENGTH = 64


class Qualification(models.Model):
    """A qualification record, signed at the moment it is issued.

    Three fields are `editable=False`: certificate_id, issued_at and signature. That is
    not cosmetic. It keeps them out of every ModelForm built from this model, so there
    is no code path where a submitted form supplies its own certificate ID or its own
    signature. A registrar can state what the qualification is; only the system states
    what it is called and whether it is authentic.
    """

    certificate_id = models.CharField(
        max_length=CERTIFICATE_ID_MAX_LENGTH,
        unique=True,
        editable=False,
        help_text="System-issued identifier, formatted QVS-XXXX-XXXX-XXXX-XXXX.",
    )
    holder_name = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    qualification_title = models.CharField(max_length=200)
    award_date = models.DateField(
        help_text="The date the qualification was awarded by the institution.",
    )
    issued_at = models.DateTimeField(
        editable=False,
        help_text="When this record was registered in QVS. Covered by the signature.",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_qualifications",
        editable=False,
    )
    signature = models.CharField(max_length=SIGNATURE_MAX_LENGTH, editable=False)

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "qualification"
        verbose_name_plural = "qualifications"

    def __str__(self) -> str:
        return f"{self.certificate_id} - {self.holder_name}"

    def save(self, *args, **kwargs) -> None:
        """Populate the issued fields, in the one order that produces a valid record.

        certificate_id first, because it is signed. issued_at second, set explicitly
        with timezone.now() rather than left to auto_now_add, because auto_now_add
        assigns its value as the row is written and a value that does not exist yet
        cannot be signed. The signature last, over the two of them and the four
        substantive fields.

        The alternative was to leave issued_at outside the signature. That is simpler
        and it makes a backdated issue timestamp undetectable, which in a credential
        system is a hole worth one line of code to close.

        Each assignment is guarded, so re-saving an existing record does not mint a new
        identifier or re-sign it under today's field values. Re-signing on save is the
        subtle failure: it would make tampering self-healing, and REQ-F-006 would never
        fire.
        """
        if not self.certificate_id:
            self.certificate_id = signing.new_certificate_id()
        if self.issued_at is None:
            self.issued_at = timezone.now()
        if not self.signature:
            self.signature = signing.sign(self.canonical_fields())
        super().save(*args, **kwargs)

    def canonical_fields(self) -> dict[str, str]:
        """Return the exact mapping that is signed and re-checked at verification.

        Every value is a string before it reaches signing.canonical_payload(). That is
        the whole point of this method existing rather than the caller assembling a
        dictionary.

        canonical_payload() carries `default=str`, which serialises any type instead of
        raising. It makes the function total, and it makes one failure mode possible: a
        date object at issue and a string read back from the database would serialise
        to different bytes, and a valid record would report as TAMPERED. A false
        accusation of forgery is the worst error this system can make - worse than
        missing a real one, because it destroys trust in every honest record too.

        Normalising here means `default=str` is never reached in practice. ISO 8601 for
        both temporal fields: unambiguous, sorts correctly, and round-trips exactly.

        issued_by is deliberately outside. Who registered a record is audit
        information, and REQ-F-007 gives it a proper trail; folding it into the
        signature would mean a record could never survive the deletion of a user
        account. Nothing in the signature depends on a row in another table.
        """
        return {
            "certificate_id": self.certificate_id,
            "holder_name": self.holder_name,
            "institution": self.institution,
            "qualification_title": self.qualification_title,
            "award_date": self.award_date.isoformat(),
            "issued_at": self.issued_at.isoformat(),
        }
