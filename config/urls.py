# config/urls.py
#
# Project URL configuration. It routes and nothing else - every view lives in an app,
# so that a URL added here is always a deliberate act of wiring rather than a place
# code accumulates.

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # REQ-F-004. Django's own auth views, wired here rather than in the qualifications
    # app: signing in is not part of the qualification domain, and D-001 chose Django
    # partly so that authentication is a requirement satisfied rather than
    # implemented. Unnamespaced, because settings.LOGIN_URL refers to "login" and the
    # framework's own redirects expect to find it under that bare name.
    #
    # django.contrib.auth.urls is deliberately not included wholesale. It brings five
    # password-reset routes that need mail configured; they would render and then fail
    # at send, which is a worse answer than not offering them.
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # Mounted at the root rather than under a prefix: the qualifications app is the
    # system, not a section of it.
    path("", include("qualifications.urls")),
]
