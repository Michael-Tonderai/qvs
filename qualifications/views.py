# qualifications/views.py

from django.http import HttpRequest, JsonResponse


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
