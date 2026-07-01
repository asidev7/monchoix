from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profil/", views.profile_view, name="profile"),
    path("mes-rapports/", views.my_reports, name="my_reports"),
]
