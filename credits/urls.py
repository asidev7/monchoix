from django.urls import path

from . import views

app_name = "credits"

urlpatterns = [
    path("credits/", views.packs, name="packs"),
    path("credits/checkout/<int:pack_id>/", views.checkout, name="checkout"),
    path("mes-credits/", views.my_credits, name="my_credits"),
    path("webhooks/fedapay/", views.fedapay_webhook, name="fedapay_webhook"),
]
