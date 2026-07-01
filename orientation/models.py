from django.conf import settings
from django.db import models


class BacSerie(models.Model):
    """A Baccalauréat track (série), e.g. C, D, G2..."""

    code = models.CharField(max_length=8, unique=True)
    label = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "code")

    def __str__(self):
        return f"{self.code} — {self.label}"


class Subject(models.Model):
    """A school subject (matière), attached to one or more séries."""

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    series = models.ManyToManyField(BacSerie, related_name="subjects", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class OrientationSession(models.Model):
    """One chatbot questionnaire run."""

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        GENERATING = "GENERATING", "Génération en cours"
        COMPLETED = "COMPLETED", "Terminé"
        FAILED = "FAILED", "Échoué"

    class Mode(models.TextChoices):
        CHATBOT = "CHATBOT", "Questionnaire"
        EXPRESS = "EXPRESS", "Express (description libre)"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions")
    answers = models.JSONField(default=dict, blank=True)
    mode = models.CharField(max_length=8, choices=Mode.choices, default=Mode.CHATBOT)
    transcript_file = models.FileField(upload_to="transcripts/", blank=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.IN_PROGRESS)
    credits_spent = models.PositiveIntegerField(default=0)
    progress_message = models.CharField(max_length=160, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Session #{self.pk} — {self.user} ({self.get_status_display()})"


class OrientationReport(models.Model):
    session = models.OneToOneField(OrientationSession, on_delete=models.CASCADE, related_name="report")
    profile_score = models.PositiveSmallIntegerField(default=0)
    top_filieres = models.JSONField(default=list, blank=True)
    top_universities = models.JSONField(default=list, blank=True)
    career_outlooks = models.JSONField(default=list, blank=True)
    average_salary = models.JSONField(default=list, blank=True)
    skills_to_develop = models.JSONField(default=list, blank=True)
    personalized_advice = models.TextField(blank=True)
    career_plan = models.JSONField(default=list, blank=True)
    sources = models.JSONField(default=list, blank=True)
    pdf_file = models.FileField(upload_to="reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rapport #{self.pk} (score {self.profile_score})"
