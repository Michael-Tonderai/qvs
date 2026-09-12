# qualifications/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from qualifications import audit, verification
from qualifications.forms import QualificationForm
from qualifications.models import Qualification


def health(request: HttpRequest) -> JsonResponse:
    """Liveness probe for the container and the pipeline.

    Deliberately touches nothing - no database query, no template render, no session.
    It answers exactly one question: is the WSGI application up and routing? A health
    check that also queries the database answers two questions at once and then cannot
    say which one failed, which is the opposite of useful at three in the morning.

    Database readiness gets its own check when there is a database worth checking.

    Serves REQ-N-003 - the system starts from a single `docker compose up` with no
    manual steps, and this is the endpoint that proves it started.
    """
    return JsonResponse({"status": "ok", "service": "qvs"})


def verify(request: HttpRequest) -> HttpResponse:
    """Verify a qualification by certificate ID.

    REQ-F-005 for the capability, REQ-F-006 for the guarantee that an altered record
    cannot pass through it, REQ-F-007 for the trail every attempt leaves behind.

    Public, and that is the requirement rather than an oversight. No login_required
    decorator, no permission check. An employer holding a certificate handed to them by
    a candidate has no account here and should not need one; a verification service
    that only serves its own members verifies nothing worth verifying.

    GET rather than POST, with the ID in the query string. Verification reads and
    changes nothing, so GET is the honest method: the result is bookmarkable and
    shareable, a refresh re-checks rather than resubmitting, and there is no CSRF token
    to manage on a page that anonymous users must reach. REQ-F-007 has since added an
    audit write, so this is no longer a pure read - and the question was revisited
    rather than assumed. GET stands: an audit trail is a side effect of answering, not
    a change to what was asked about, and switching to POST would put a CSRF token on
    the one page in this system that people with no account have to be able to use.

    Every outcome returns 200, including NOT FOUND. The status code describes what
    happened to the request, and the request succeeded - the service was asked a
    question and answered it. A 404 would say the verification page does not exist,
    which is false and which makes an answered question look like a broken link. It
    would also hand an automated caller a way to sort real IDs from invented ones by
    status alone, without reading a single response body.
    """
    submitted = verification.normalise_certificate_id(
        request.GET.get("certificate_id", "")
    )

    # A blank box is not a failed verification. Rendering NOT FOUND for someone who has
    # not typed anything yet - which includes everyone arriving at the page for the
    # first time - would announce a problem where there is none. It is also not a
    # verification attempt, so there is nothing for REQ-F-007 to record.
    result = verification.verify(submitted) if submitted else None

    # REQ-F-007. Unconditional on the outcome and unconditional on who is asking: a
    # trail that recorded only failures could never show that a certificate had been
    # checked and found good, and one that recorded only signed-in users would cover
    # none of the public traffic this page exists to serve. A repeated attempt writes
    # its own event - an audit trail that deduplicates has stopped being a record of
    # what happened and become a summary of it.
    if result is not None:
        audit.record_attempt(request, submitted, result.outcome)

    return render(
        request,
        "qualifications/verify.html",
        {"submitted": submitted, "result": result},
    )


@login_required
def register(request: HttpRequest) -> HttpResponse:
    """Register a qualification record.

    REQ-F-003 for the capability, REQ-F-004 for the guard. The decorator is the guard -
    not a hidden link in a template, because hiding a control is not access control and
    an anonymous POST straight to this URL has to fail on its own merits.

    issued_by is set from request.user here rather than anywhere the form can reach.
    The registrar's identity is something the request proves, never something the
    request body claims.

    Redirect after a successful POST rather than rendering the confirmation directly,
    so that a browser refresh on the confirmation page cannot issue a second
    certificate for the same submission.
    """
    if request.method == "POST":
        form = QualificationForm(request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.issued_by = request.user
            qualification.save()
            return redirect(
                "qualifications:register_done",
                certificate_id=qualification.certificate_id,
            )
    else:
        form = QualificationForm()

    return render(request, "qualifications/register.html", {"form": form})


@login_required
def register_done(request: HttpRequest, certificate_id: str) -> HttpResponse:
    """Show the certificate ID that was just issued.

    Behind login on purpose. This is a receipt for the registrar, not the public
    verification page - REQ-F-005 owns that, and it answers VERIFIED, NOT FOUND or
    TAMPERED for anyone holding a certificate ID. Leaving this one open would quietly
    ship an unauthenticated record-lookup endpoint that no requirement asked for.
    """
    qualification = get_object_or_404(Qualification, certificate_id=certificate_id)
    return render(
        request,
        "qualifications/register_done.html",
        {"qualification": qualification},
    )
