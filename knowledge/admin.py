from django.contrib import admin, messages

from . import services
from .models import KnowledgeDocument


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "country_scope", "has_pdf", "has_embedding", "updated_at")
    list_filter = ("category", "country_scope")
    search_fields = ("title", "content", "source")
    actions = ["reindex_selected"]
    exclude = ("embedding",)

    @admin.display(boolean=True, description="PDF")
    def has_pdf(self, obj):
        return bool(obj.pdf_file)

    @admin.display(boolean=True, description="Indexé")
    def has_embedding(self, obj):
        return obj.embedding is not None

    def save_model(self, request, obj, form, change):
        """On save: extract the PDF text (if any), then re-index for RAG."""
        super().save_model(request, obj, form, change)
        if obj.pdf_file and (not obj.content or "pdf_file" in form.changed_data):
            text = services.extract_pdf_text(obj.pdf_file)
            if text:
                obj.content = text
                obj.save(update_fields=["content"])
                self.message_user(
                    request, f"Texte extrait du PDF ({len(text)} caractères).", messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    "Impossible d'extraire le texte du PDF (scanné ou protégé ?).",
                    messages.WARNING,
                )
        if services.index_document(obj):
            self.message_user(request, "Document indexé pour la recherche IA.", messages.SUCCESS)

    @admin.action(description="Ré-indexer (recalculer les embeddings)")
    def reindex_selected(self, request, queryset):
        done = sum(services.index_document(doc) for doc in queryset)
        self.message_user(request, f"{done} document(s) ré-indexé(s).", messages.SUCCESS)
