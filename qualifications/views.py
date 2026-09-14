# qualifications/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from qualifications import audit, search, verification
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


@login_required
def search_records(request: HttpRequest) -> HttpResponse:
    """Search registered records by certificate ID, holder name or institution.

    REQ-F-009. Behind login under D-040, and that decision is the whole character of
    this view. Built as the register originally worded it - "any user" - this would be
    a public index of who holds which qualification, which defeats the non-guessable
    certificate ID REQ-F-001 pays entropy for and removes the holder from the consent
    chain that makes REQ-F-005 defensible in the first place. Verification is checking
    a credential you were handed. This is not.

    Named `search_records` rather than `search` because `qualifications.search` is the
    module it delegates to, and a view of the same name would shadow the import. The URL
    name stays `search`, which is what templates and tests refer to.

    GET with the query in the query string, matching views.verify. A search reads and
    changes nothing, so the result is bookmarkable and a refresh re-runs it rather than
    resubmitting a form.

    No audit event. REQ-F-007 records verification attempts, and a search is not one -
    nothing here asks whether a record is authentic and nothing here answers. Widening
    the audit trail to cover reads would change what an audit event means without a
    requirement asking, and would make the trail's central question - what was presented
    for verification, and what did the system say - harder to answer rather than easier.

    An empty query renders the form and no results, and is explicitly not a search that
    found nothing. The distinction is visible on screen because the alternative tells
    everyone arriving at the page for the first time that their search failed.
    """
    query = request.GET.get("q", "").strip()

    results = None
    truncated = False

    if query:
        # One row beyond the cap, so a full page can be told from a truncated one
        # without a second COUNT query. The extra row is dropped before rendering; its
        # only job is to answer "is there more than this".
        matches = list(search.find(query)[: search.MAX_RESULTS + 1])
        truncated = len(matches) > search.MAX_RESULTS
        results = matches[: search.MAX_RESULTS]

    return render(
        request,
        "qualifications/search.html",
        {
            "query": query,
            "results": results,
            "truncated": truncated,
            "max_results": search.MAX_RESULTS,
        },
    )


@login_required
def record_detail(request: HttpRequest, certificate_id: str) -> HttpResponse:
    """Show the full detail of one registered record.

    REQ-F-010. Behind login under D-040, for the same reason as the search page above:
    an unauthenticated record-lookup endpoint is exactly what REQ-F-005 is not.

    This view does NOT verify the record, and that is deliberate rather than an
    omission. verification.py states that "every verification attempt is audited" holds
    because its only caller writes the event, and a second caller inherits that
    obligation - so calling verify() here would either break the invariant or widen the
    audit trail to cover internal browsing. The page instead links to the public
    verification page for this certificate ID, which is the shape register_done.html
    already takes. Verification happens in one place in this system, and stays there.

    The certificate ID from the URL is normalised before lookup, so a hand-typed or
    lower-cased address resolves rather than 404ing. Links generated by the application
    already carry the canonical form; this is for the address bar. A false negative -
    telling someone a record does not exist when it does - is the failure this system
    can least afford, and normalisation is the cheapest place to remove one.
    """
    qualification = get_object_or_404(
        Qualification,
        certificate_id=verification.normalise_certificate_id(certificate_id),
    )
    return render(
        request,
        "qualifications/record_detail.html",
        {"qualification": qualification},
    )
