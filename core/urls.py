from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("tableau-de-bord/", views.my_dashboard, name="my_dashboard"),
    path("guides/", views.guides, name="guides"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
