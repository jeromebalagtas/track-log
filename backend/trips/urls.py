from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health, name="health"),
    path("health/", views.health, name="health-slash"),
    path("plan-trip", views.plan_trip, name="plan-trip"),
    path("plan-trip/", views.plan_trip, name="plan-trip-slash"),
]
