from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = []

if not settings.IS_VERCEL:
    urlpatterns.append(path("admin/", admin.site.urls))

# Support both /api/plan-trip (local proxy) and /plan-trip (Vercel Services prefix).
urlpatterns += [
    path("api/", include("trips.urls")),
    path("", include("trips.urls")),
]
