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
]
