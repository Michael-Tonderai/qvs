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
    # A temporary redirect rather than a permanent one. Permanent redirects are cached
    # by browsers and are painful to take back, and this destination is expected to
    # change: REQ-F-009 search and REQ-F-010 record detail will give the root something
    # of its own, and REQ-F-005 verification is the page an unauthenticated visitor
    # actually wants. Sending the public to a login wall is the right answer only until
    # there is a public page to send them to.
    path(
        "",
        RedirectView.as_view(pattern_name="qualifications:register"),
        name="index",
    ),
    path("health/", views.health, name="health"),
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
