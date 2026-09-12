# qualifications/models.py
#
# REQ-F-003 - an authorised user can register a qualification record.
# REQ-F-007 - every verification attempt writes an audit event.
# REQ-F-008 - audit events are append-only; no update or delete path exists.
#
# The Qualification model owns three things the rest of the system depends on: the
# unique constraint on certificate_id, the exact mapping of fields that gets signed,
# and the ordering of work inside save() that makes a signature reproducible.
#
# The AuditEvent model owns one thing: a record of a verification attempt that cannot
# be changed once it exists.

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

# Deliberately wider than a real certificate ID. This column stores what somebody
# typed, not what the system issued, and what somebody typed can be anything at all -
# a pasted paragraph, a URL, an injection attempt. 64 leaves nearly three times the
# room a genuine ID needs while keeping a junk submission visible as junk rather than
# storing an unbounded string because a form field was unbounded.
SUBMITTED_CERTIFICATE_ID_MAX_LENGTH = 64

# VERIFIED, NOT FOUND and TAMPERED are at most nine characters. 16 leaves room without
# inviting the column to become a general-purpose note field.
OUTCOME_MAX_LENGTH = 16

# django.contrib.auth's own username limit. Matched rather than guessed, so a username
# that Django accepts can never fail to fit the audit row that records it.
USERNAME_MAX_LENGTH = 150


class AppendOnlyError(Exception):
    """Raised when something tries to change or remove an audit event.

    A dedicated exception rather than a bare RuntimeError or a ValidationError. It
    makes the guarantee greppable, it lets a test assert on the specific failure rather
    than on any exception at all, and it means a caller that genuinely wants to handle
    this case can do so without catching everything else in the same line.
    """


class AuditEventQuerySet(models.QuerySet):
    """A queryset that refuses to update or delete.

    This class is the whole reason REQ-F-008 is more than one guarded save(). Model
    save() and delete() are instance methods, and QuerySet.update() and
    QuerySet.delete() go straight to SQL without calling either of them. Guarding only
    the model would leave AuditEvent.objects.all().delete() working perfectly, which is
    precisely the operation the requirement exists to prevent.
    """

    def update(self, *args, **kwargs):
        raise AppendOnlyError(
            "Audit events are append-only; update() is not available (REQ-F-008)."
        )

    def delete(self, *args, **kwargs):
        raise AppendOnlyError(
            "Audit events are append-only; delete() is not available (REQ-F-008)."
        )


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


class AuditEvent(models.Model):
    """One verification attempt, recorded permanently.

    REQ-F-007 for the record, REQ-F-008 for the guarantee that it stays what it was.

    Every column is a plain value. There is no ForeignKey on this model at all, and
    that is the central design decision rather than an omission:

    - A NOT FOUND attempt has no qualification to point at. A nullable ForeignKey would
      therefore be null on exactly the events most worth auditing - the ones where
      somebody presented an ID this system has never issued.
    - Deleting a user would have to do something to the rows that referenced them.
      CASCADE destroys audit history, SET_NULL rewrites it, and PROTECT makes the audit
      trail a reason accounts cannot be closed. All three are wrong; rewriting an audit
      row contradicts REQ-F-008 in the model's own definition.
    - It is the same argument Qualification.canonical_fields() already makes for
      keeping issued_by outside the signed payload. Nothing here depends on a row in
      another table continuing to exist.

    REQ-F-011, when it arrives, joins on submitted_certificate_id as a string. That is
    also the correct join: the audit question is "what was presented", not "which
    record did it turn out to be".
    """

    occurred_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the verification was attempted.",
    )
    submitted_certificate_id = models.CharField(
        max_length=SUBMITTED_CERTIFICATE_ID_MAX_LENGTH,
        help_text="The certificate ID as submitted, after normalisation.",
    )
    outcome = models.CharField(
        max_length=OUTCOME_MAX_LENGTH,
        help_text="VERIFIED, NOT FOUND or TAMPERED.",
    )
    actor_username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        blank=True,
        help_text="The signed-in user, or blank for an anonymous attempt.",
    )
    remote_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="The address the attempt came from, where the request carried one.",
    )

    # No `choices` on outcome, deliberately. The three outcome strings are defined in
    # qualifications/verification.py, which imports this module - importing them back
    # here would close an import cycle. Moving the constants into models.py would
    # resolve it and would also move the vocabulary away from the module that decides
    # between the three, which is where a reader looks for it. The coupling is checked
    # by test instead of enforced by the column.

    objects = models.Manager.from_queryset(AuditEventQuerySet)()

    class Meta:
        ordering = ["-occurred_at"]
        verbose_name = "audit event"
        verbose_name_plural = "audit events"

    def __str__(self) -> str:
        when = f"{self.occurred_at:%Y-%m-%d %H:%M:%S}"
        return f"{when} {self.outcome} {self.submitted_certificate_id}"

    def save(self, *args, **kwargs) -> None:
        """Insert only. A second save on the same row is refused.

        `self.pk is not None` is the test for "this row already exists", and it is
        exact here because the primary key is an auto field assigned by the database on
        insert. A model that used a natural key would need a different check.
        """
        if self.pk is not None:
            raise AppendOnlyError(
                "Audit events are append-only; an existing event cannot be "
                "re-saved (REQ-F-008)."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Never. An audit trail with a delete path is a draft, not a trail."""
        raise AppendOnlyError(
            "Audit events are append-only; delete() is not available (REQ-F-008)."
        )
