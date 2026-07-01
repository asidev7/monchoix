def credits_balance(request):
    """Expose the credit balance to every template (header counter)."""
    if request.user.is_authenticated:
        return {"user_credits": request.user.credits}
    return {"user_credits": None}
