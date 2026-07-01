from django.contrib import admin

from .models import BacSerie, OrientationReport, OrientationSession, Subject


@admin.register(BacSerie)
class BacSerieAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "order")
    list_editable = ("order",)
    search_fields = ("code", "label")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    filter_horizontal = ("series",)


@admin.register(OrientationSession)
class OrientationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "credits_spent", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("answers", "created_at", "completed_at")
    date_hierarchy = "created_at"


@admin.register(OrientationReport)
class OrientationReportAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "profile_score", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("session__user__email",)
