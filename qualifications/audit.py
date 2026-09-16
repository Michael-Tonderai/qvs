# qualifications/audit.py
#
# REQ-F-007 - every verification attempt writes an audit event.
# REQ-F-011 - an authorised user can view the audit history for a record.
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
#
# REQ-F-011 reads the trail this module writes, so the query lives here beside the
# write rather than in a module of its own. What an audit event means and how it is
# found are the same piece of knowledge, and splitting them would put the join key in
# one file and the reason for it in another.

from django.db.models import QuerySet
from django.http import HttpRequest

from qualifications.models import SUBMITTED_CERTIFICATE_ID_MAX_LENGTH, AuditEvent
from qualifications.verification import normalise_certificate_id

# The most events one history page will render.
#
# Same reasoning as search.MAX_RESULTS, and the same failure it closes: a certificate ID
# that has been checked by an automated caller thousands of times would otherwise render
# every one of those rows into a single page. A cap is one integer; pagination is a
# control surface no requirement asks for.
#
# Higher than the search cap on purpose. Fifty records matching one search term means
# the term was too broad, and narrowing it is the answer. A hundred verification
# attempts against one certificate is not a mistake by the person reading the page - it
# is what a popular credential looks like - so the cap is set where it stops being
# readable rather than where it stops being plausible.
MAX_HISTORY_EVENTS = 100


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


def history_for(certificate_id: str) -> QuerySet[AuditEvent]:
    """Return every recorded attempt that presented `certificate_id`, newest first.

    REQ-F-011. The join is on the submitted string, not on a foreign key, because
    D-032 gave AuditEvent no foreign keys at all - a NOT FOUND attempt has no
    qualification to point at, and nullable keys would be null on exactly the events
    most worth auditing. This function is where that decision is paid for and where it
    pays back: the query is one filter on an indexed-by-nothing CharField, and it
    returns attempts regardless of whether the record they named still exists.

    Exact match, not `icontains`. search.find matches fragments because a registrar has
    a partial string in their hand and does not know which field it belongs to. Here the
    caller is a page that already knows precisely which record it is showing, and a
    substring match would pull in the history of any other certificate whose ID happened
    to contain this one - mixing two records' audit trails on one page, which is the one
    thing an audit page must never do.

    Normalised first, so the stored form and the looked-up form cannot disagree.
    views.verify normalises before recording, so every event written by this system
    carries the canonical form; normalising here means a caller that passes a
    hand-typed identifier still finds them.

    WHAT THIS DOES NOT RETURN, and it is a real limitation rather than a technicality:
    attempts that presented an identifier this system never issued. Those events exist
    and are permanent, but they belong to no record, so no record's history page can
    show them. A page scoped to a record cannot be a complete view of the trail, and
    the report says so rather than leaving a reader to assume otherwise.

    Ordering is set explicitly here, by `-occurred_at` and then `-pk`, rather than
    inherited from AuditEvent.Meta. Meta orders by `-occurred_at` alone, and two events
    can carry the same timestamp. When they do, nothing decides between them and the
    database returns them in whatever order it likes - on SQLite, insertion order,
    which is oldest first and the reverse of what the history page promises. This was
    not hypothetical: tests/test_audit_history.py failed on the Windows development
    machine for exactly this reason while passing on Linux CI, whose clock is fine
    enough that two back-to-back writes rarely collide. The primary key is assigned in
    the order events are written, so it breaks a tie by write order. Set in the query
    rather than in Meta so that no migration is needed, and so that the guarantee sits
    beside the caller that depends on it.
    """
    events = AuditEvent.objects.filter(
        submitted_certificate_id=normalise_certificate_id(certificate_id)
    )
    return events.order_by("-occurred_at", "-pk")
