# qualifications/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

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
    verification page - REQ-F-005 owns that, and it will answer VERIFIED, NOT FOUND or
    TAMPERED for anyone holding a certificate ID. Leaving this one open would quietly
    ship an unauthenticated record-lookup endpoint that no requirement asked for.
    """
    qualification = get_object_or_404(Qualification, certificate_id=certificate_id)
    return render(
        request,
        "qualifications/register_done.html",
        {"qualification": qualification},
    )
