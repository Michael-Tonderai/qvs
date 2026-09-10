# qualifications/urls.py
#
# App URL configuration. Named routes throughout - templates and tests refer to view
# names, never to literal paths, so a URL can be restructured without a find-and-
# replace across the repository.

from django.urls import path

from qualifications import views

app_name = "qualifications"

urlpatterns = [
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
