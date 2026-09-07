# config/urls.py
#
# Project URL configuration. It routes and nothing else - every view lives in an app,
# so that a URL added here is always a deliberate act of wiring rather than a place
# code accumulates.

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Mounted at the root rather than under a prefix: the qualifications app is the
    # system, not a section of it.
    path("", include("qualifications.urls")),
]
