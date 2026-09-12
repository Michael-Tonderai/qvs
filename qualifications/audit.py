# qualifications/audit.py
#
# REQ-F-007 - every verification attempt writes an audit event.
#
# This module exists to keep two things apart that would otherwise be tangled in the
# view. models.py knows nothing about HTTP, and verification.py is documented as
# answerable without a request cycle. Pulling request-scoped facts out of an
# HttpRequest is neither of those jobs, so it gets its own small module rather than
# four lines wedged into views.verify().
#
# It is also the module a second caller would reach for. If verification ever grows an
# API or a management command, the audit write is already a function rather than a
# fragment of a view.

from django.http import HttpRequest

from qualifications.models import SUBMITTED_CERTIFICATE_ID_MAX_LENGTH, AuditEvent


def actor_username(request: HttpRequest) -> str:
    """Return the signed-in username, or an empty string for the public.

    Empty string rather than None. The column is a CharField and Django's convention
    for "no text here" in a CharField is blank, not null - two ways to say absent in
    one column is one way too many.

    getattr rather than request.user directly, so that a request built without the
    authentication middleware records an anonymous attempt instead of raising. An
    audit trail that can refuse to write is worse than one that writes less.
    """
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return user.get_username()
    return ""


def remote_address(request: HttpRequest) -> str | None:
    """Return the address the request arrived from, or None if it carried none.

    REMOTE_ADDR only. X-Forwarded-For is deliberately NOT consulted, and this is worth
    a paragraph in the report rather than a line of code.

    Under D-026 this system deploys behind a managed container service, so REMOTE_ADDR
    will be the platform's proxy rather than the person verifying a certificate. The
    fix for that is to trust X-Forwarded-For - but a header is trivially forged by any
    client, so trusting it without a configured list of trusted proxies means the audit
    trail records whatever the caller felt like claiming. An audit trail that can be
    dictated by the subject of the audit is worse than no address at all, because it
    looks like evidence.

    Recording the proxy address honestly is the smaller error, and it is the one that
    does not mislead a reader. Configuring trusted proxies is the correct fix and it
    belongs with the deployment work, not here.
    """
    address = request.META.get("REMOTE_ADDR")
    return address or None


def record_attempt(
    request: HttpRequest,
    submitted_certificate_id: str,
    outcome: str,
) -> AuditEvent:
    """Write one audit event for one verification attempt.

    The certificate ID is truncated to the column width rather than left to fail. What
    arrives here is whatever was typed into a public form, and a caller pasting a
    kilobyte of text is a thing that happens; the audit value of the record is in the
    fact that an attempt was made and roughly what was presented, so a database error
    on an over-long string would lose the event to protect a field width. See
    SUBMITTED_CERTIFICATE_ID_MAX_LENGTH for why the column is wider than a real ID.

    Returns the event so that a caller - in practice a test - can assert on what was
    written without going back to the database for it.
    """
    return AuditEvent.objects.create(
        submitted_certificate_id=submitted_certificate_id[
            :SUBMITTED_CERTIFICATE_ID_MAX_LENGTH
        ],
        outcome=outcome,
        actor_username=actor_username(request),
        remote_address=remote_address(request),
    )
