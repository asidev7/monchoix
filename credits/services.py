"""Atomic credit ledger operations."""
from django.db import transaction

from .models import CreditTransaction


class InsufficientCredits(Exception):
    pass


@transaction.atomic
def consume_credits(user, amount, *, reason=""):
    """Debit `amount` credits atomically. Raises InsufficientCredits if too low.

    Locks the user row to avoid race conditions on concurrent generations.
    """
    from accounts.models import User

    if amount <= 0:
        raise ValueError("amount must be positive")
    locked = User.objects.select_for_update().get(pk=user.pk)
    if locked.credits < amount:
        raise InsufficientCredits(f"Solde insuffisant ({locked.credits} < {amount}).")
    locked.credits -= amount
    locked.save(update_fields=["credits"])
    tx = CreditTransaction.objects.create(
        user=locked,
        type=CreditTransaction.Type.CONSUMPTION,
        amount=-amount,
        balance_after=locked.credits,
        payment_status=CreditTransaction.PaymentStatus.PAID,
    )
    user.credits = locked.credits
    return tx


@transaction.atomic
def refund_credits(user, amount, *, reason=""):
    """Credit `amount` back to the user (e.g. failed report generation)."""
    from accounts.models import User

    if amount <= 0:
        raise ValueError("amount must be positive")
    locked = User.objects.select_for_update().get(pk=user.pk)
    locked.credits += amount
    locked.save(update_fields=["credits"])
    tx = CreditTransaction.objects.create(
        user=locked,
        type=CreditTransaction.Type.REFUND,
        amount=amount,
        balance_after=locked.credits,
        payment_status=CreditTransaction.PaymentStatus.PAID,
    )
    user.credits = locked.credits
    return tx


@transaction.atomic
def apply_purchase(tx):
    """Finalize a PAID purchase transaction, crediting the account once (idempotent)."""
    from accounts.models import User

    if tx.type != CreditTransaction.Type.PURCHASE:
        return tx
    if tx.payment_status == CreditTransaction.PaymentStatus.PAID and tx.balance_after:
        return tx  # already applied
    locked = User.objects.select_for_update().get(pk=tx.user_id)
    locked.credits += tx.amount
    locked.save(update_fields=["credits"])
    tx.payment_status = CreditTransaction.PaymentStatus.PAID
    tx.balance_after = locked.credits
    tx.save(update_fields=["payment_status", "balance_after"])
    return tx
