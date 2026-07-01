from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class CreditPack(models.Model):
    """A purchasable pack of credits, configurable from the admin."""

    name = models.CharField(max_length=120)
    credits = models.PositiveIntegerField()
    price_xof = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(settings.MIN_PACK_PRICE_XOF)],
        help_text=f"Prix en FCFA (min {settings.MIN_PACK_PRICE_XOF}).",
    )
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "price_xof")

    def __str__(self):
        return f"{self.name} — {self.credits} crédits / {self.price_xof:.0f} FCFA"


class CreditTransaction(models.Model):
    class Type(models.TextChoices):
        SIGNUP_BONUS = "SIGNUP_BONUS", "Bonus d'inscription"
        PURCHASE = "PURCHASE", "Achat"
        CONSUMPTION = "CONSUMPTION", "Consommation"
        REFUND = "REFUND", "Remboursement"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "En attente"
        PAID = "PAID", "Payé"
        FAILED = "FAILED", "Échoué"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.IntegerField(help_text="Positif = crédit, négatif = débit.")
    balance_after = models.IntegerField(default=0)
    pack = models.ForeignKey(CreditPack, on_delete=models.SET_NULL, null=True, blank=True)
    fedapay_transaction_id = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PAID
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_type_display()} {self.amount:+d} ({self.user})"
