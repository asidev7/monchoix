from django.contrib import admin

from .models import CreditPack, CreditTransaction


@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ("name", "credits", "price_xof", "active", "order")
    list_editable = ("credits", "price_xof", "active", "order")
    list_filter = ("active",)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "type", "amount", "balance_after", "payment_status", "fedapay_transaction_id")
    list_filter = ("type", "payment_status", "created_at")
    search_fields = ("user__email", "fedapay_transaction_id")
    readonly_fields = [f.name for f in CreditTransaction._meta.fields]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False
