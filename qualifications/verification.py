# qualifications/verification.py
#
# REQ-F-005 - any user can verify a record by certificate ID.
# REQ-F-006 - a record altered after issue fails verification.
#
# The verification decision lives here rather than in the view, for the same reason
# signing.py is a plain module: a view can only be tested through a request cycle, and
# the question "is this record authentic" deserves to be answerable without one.
#
# Unlike signing.py this module does touch the ORM, so it is not database-free. The
# separation it buys is still worth having - the rule that decides between three
# outcomes is readable in one screen, with no HTTP, no template and no form around it.

from dataclasses import dataclass

from qualifications import signing
from qualifications.models import Qualification

# The three outcomes REQ-F-005 names, as constants rather than bare strings scattered
# through view, template and tests. A misspelling becomes an ImportError here instead
# of a branch that silently never matches.
VERIFIED = "VERIFIED"
NOT_FOUND = "NOT FOUND"
TAMPERED = "TAMPERED"


@dataclass(frozen=True)
class VerificationResult:
    """The answer to one verification attempt.

    `qualification` is populated only when the outcome is VERIFIED. That is a deliberate
    constraint rather than an oversight, and it is the reason this is a small object
    instead of a two-tuple.

    A tampered record still has fields in the database. Rendering them - even under a
    red heading - would put unverified data on screen in the exact layout a genuine
    record uses, and a reader who skims would carry away a holder name and a
    qualification title that the system has just finished refusing to vouch for. By
    attaching the record only on VERIFIED, the template is not trusted to remember
    that: there is nothing to render.

    Frozen because a verification result is a statement about a moment, and nothing
    downstream has any business editing it.
    """

    outcome: str
    qualification: Qualification | None = None

    # Templates cannot compare against an imported constant without a custom tag, so
    # the comparison is exposed as properties. The alternative is string literals in
    # the template, which is a second place the word "TAMPERED" has to be spelled
    # correctly and no test would catch a typo in the branch that never fires.
    @property
    def is_verified(self) -> bool:
        return self.outcome == VERIFIED

    @property
    def is_not_found(self) -> bool:
        return self.outcome == NOT_FOUND

    @property
    def is_tampered(self) -> bool:
        return self.outcome == TAMPERED


def normalise_certificate_id(raw: str) -> str:
    """Return a certificate ID in the form the database stores it.

    Uppercased, with all whitespace removed. Both cases are real: a holder reads an ID
    off a printed certificate and types it in lower case, or pastes it out of an email
    client that wrapped a line in the middle.

    This is the same concern that shaped the alphabet in signing.py. The excluded
    characters exist because a misread ID turns a genuine record into NOT FOUND, and a
    false negative is the one failure this system cannot afford to be casual about.
    Case and stray spaces are the cheapest instance of that problem to fix.

    What this deliberately does NOT do is repair a malformed ID: it does not insert
    missing hyphens, and it does not map look-alike characters onto the alphabet.
    Crockford base32 would normally fold O onto 0 and I onto 1, but signing.py excludes
    0 and 1 as well, so there is no correct target to fold them onto - a typed O is
    simply not a character any issued ID contains. Guessing at a repair risks
    normalising one valid ID into another, and quietly verifying the wrong record is
    far worse than answering NOT FOUND to a mistyped one.
    """
    return "".join(raw.split()).upper()


def verify(certificate_id: str) -> VerificationResult:
    """Decide whether the record behind `certificate_id` is authentic.

    Three outcomes, in the order they can be determined:

    NOT FOUND   - no record carries this ID. Also the answer for a blank ID, so the
                  function stays total; the view avoids calling it in that case,
                  because an empty form box is a question nobody asked rather than a
                  certificate that failed.
    TAMPERED    - the record exists, and its stored fields no longer produce its
                  stored signature. REQ-F-006 in one line.
    VERIFIED    - the record exists and re-signing its canonical fields reproduces the
                  signature it was issued with.

    The signature is recomputed on every call rather than cached, and it is compared
    with hmac.compare_digest inside signing.verify_signature rather than with ==. Both
    choices are in signing.py for reasons documented there; this module simply does not
    undo them.

    Note what is NOT here: no audit write. REQ-F-007 gives every verification attempt
    a trail, and it deliberately did not land in this function. An audit event needs
    facts that only a request carries - who was signed in, and where the attempt came
    from - and this module exists precisely so the authenticity question can be
    answered without a request cycle. qualifications/views.py verify() performs the
    write through qualifications/audit.py, so this stays a pure decision and every
    unit test of it stays free of a database write.

    The cost is stated in the pull request for issue #18 rather than hidden: "every
    attempt is audited" holds because the only caller does it, not because this
    function enforces it. A second caller would carry the same obligation.
    """
    if not certificate_id:
        return VerificationResult(NOT_FOUND)

    try:
        qualification = Qualification.objects.get(certificate_id=certificate_id)
    except Qualification.DoesNotExist:
        return VerificationResult(NOT_FOUND)

    if signing.verify_signature(
        qualification.canonical_fields(), qualification.signature
    ):
        return VerificationResult(VERIFIED, qualification)

    return VerificationResult(TAMPERED)
