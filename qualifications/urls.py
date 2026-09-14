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
    # Still a temporary redirect, and REQ-F-012 registered that behaviour rather than
    # changing it. REQ-F-009 search and REQ-F-010 record detail have since landed and
    # did NOT take the root: both are behind login under D-040, and an anonymous
    # visitor sent to a signed-in page would arrive at a login form instead of at the
    # one thing this system offers them.
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
    # REQ-F-009. Same query-string shape as `verify` above and for the same reason:
    # `/search/` renders the form, `/search/?q=...` renders an answer, and the answer
    # is a URL somebody can send to a colleague.
    #
    # The URL name is `search` while the view is `search_records`, because
    # `qualifications.search` is the module the view delegates to and a view of that
    # name would shadow the import. Everything outside views.py refers to the name.
    path("search/", views.search_records, name="search"),
    # REQ-F-010. Keyed on the certificate ID rather than the primary key, the same
    # choice `register_done` makes above and for the same reason - a sequential pk in
    # an address tells a reader how many records exist and lets them walk the set.
    path(
        "records/<str:certificate_id>/",
        views.record_detail,
        name="record_detail",
    ),
    # REQ-F-011. Nested under the record rather than given a route of its own, because
    # the audit history this system offers is scoped to a record: there is no
    # `/history/` page listing the whole trail, and the URL should not imply one. The
    # address also reads as the question it answers - the history of this record.
    path(
        "records/<str:certificate_id>/history/",
        views.record_history,
        name="record_history",
    ),
]
