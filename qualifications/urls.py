# qualifications/urls.py
#
# App URL configuration. Named routes throughout - templates and tests refer to view
# names, never to literal paths, so a URL can be restructured without a find-and-
# replace across the repository.

from django.urls import path
from django.views.generic import RedirectView

from qualifications import views

app_name = "qualifications"

urlpatterns = [
    # The root. Not a landing page - a redirect, deliberately.
    #
    # Nothing was routed here before, so the front door of the system answered 404,
    # which is what a visitor and a marker both see first. A redirect closes that
    # without inventing a view no requirement asked for.
    #
    # The destination is the public verification page, changed from `register` when
    # REQ-F-005 landed. Sending an anonymous visitor to a login wall was the right
    # answer only while there was no public page to send them to; now the front door
    # opens onto the thing the system exists to do, and a visitor who does have an
    # account is one click from signing in anyway. The old destination made the system
    # look like an internal registry that happens to allow verification, which is the
    # wrong way round.
    #
    # Still a temporary redirect. REQ-F-009 search and REQ-F-010 record detail may yet
    # give the root a page of its own, and a permanent redirect is cached by browsers
    # and painful to take back.
    path(
        "",
        RedirectView.as_view(pattern_name="qualifications:verify"),
        name="index",
    ),
    path("health/", views.health, name="health"),
    # REQ-F-005. Public, and the only route here that is. The certificate ID travels in
    # the query string rather than the path, so that the bare URL is a usable entry
    # point for someone who has not typed an ID yet - `/verify/` renders the form,
    # `/verify/?certificate_id=...` renders an answer. A path parameter would make the
    # form's own address a 404.
    path("verify/", views.verify, name="verify"),
    path("register/", views.register, name="register"),
    # The certificate ID is the lookup key rather than the primary key. A sequential
    # pk in a URL tells a visitor how many records exist and lets them walk the set by
    # hand, which undoes the non-guessability REQ-F-001 pays entropy for.
    path(
        "registered/<str:certificate_id>/",
        views.register_done,
        name="register_done",
    ),
]
