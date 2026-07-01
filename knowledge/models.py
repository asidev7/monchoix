from django.conf import settings
from django.db import models

try:
    from pgvector.django import VectorField

    HAS_PGVECTOR = True
except Exception:  # pragma: no cover - fallback when pgvector missing
    VectorField = None
    HAS_PGVECTOR = False


class KnowledgeDocument(models.Model):
    """A reference document used by the RAG pipeline (filières, universities, bourses...)."""

    class Category(models.TextChoices):
        FILIERES = "FILIERES", "Filières"
        UNIVERSITES = "UNIVERSITES", "Universités"
        BOURSES = "BOURSES", "Bourses"
        DEBOUCHES = "DEBOUCHES", "Débouchés"
        AUTRE = "AUTRE", "Autre"

    title = models.CharField(max_length=255)
    source = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.AUTRE)
    pdf_file = models.FileField(
        upload_to="knowledge_pdfs/", blank=True, null=True,
        help_text="PDF de référence — son texte est extrait automatiquement à l'enregistrement.",
    )
    content = models.TextField(blank=True, help_text="Rempli automatiquement depuis le PDF, ou saisi à la main.")
    country_scope = models.CharField(max_length=80, blank=True, help_text="Pays/zone concerné, ou vide = global.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if HAS_PGVECTOR:
        embedding = VectorField(dimensions=settings.EMBEDDING_DIM, null=True, blank=True)
    else:  # pragma: no cover
        embedding = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
