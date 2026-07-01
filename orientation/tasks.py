import logging

from celery import shared_task
from django.utils import timezone

from credits import services as credit_services

from . import agent, pdf
from .models import OrientationReport, OrientationSession

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_report(self, session_id):
    """Run the agent pipeline for a session. Credits already debited by the caller.

    On failure the credits are refunded and the session marked FAILED.
    """
    session = OrientationSession.objects.select_related("user").get(pk=session_id)
    session.status = OrientationSession.Status.GENERATING
    session.save(update_fields=["status"])

    def on_progress(msg):
        OrientationSession.objects.filter(pk=session_id).update(progress_message=msg)

    try:
        data = agent.generate_report_data(session.answers, on_progress=on_progress)
    except Exception as exc:
        logger.exception("Report generation failed for session %s", session_id)
        # Refund the credits spent on this failed generation.
        if session.credits_spent:
            credit_services.refund_credits(session.user, session.credits_spent, reason="Échec génération")
        session.status = OrientationSession.Status.FAILED
        session.error = str(exc)[:1000]
        session.progress_message = "La génération a échoué. Vos crédits ont été remboursés."
        session.save(update_fields=["status", "error", "progress_message"])
        return {"ok": False, "error": str(exc)}

    report, _ = OrientationReport.objects.update_or_create(
        session=session,
        defaults={
            "profile_score": int(data.get("profile_score", 0) or 0),
            "top_filieres": data.get("top_filieres", []),
            "top_universities": data.get("top_universities", []),
            "career_outlooks": data.get("debouches", []),
            "average_salary": data.get("salaire_moyen", []),
            "skills_to_develop": data.get("competences_a_developper", []),
            "personalized_advice": data.get("conseils_personnalises", ""),
            "career_plan": data.get("plan_de_carriere", []),
            "sources": data.get("sources", []),
        },
    )

    on_progress("Génération du PDF…")
    try:
        pdf.build_report_pdf(report)
    except Exception:  # pragma: no cover - PDF is best-effort
        logger.exception("PDF build failed for report %s", report.pk)

    session.status = OrientationSession.Status.COMPLETED
    session.completed_at = timezone.now()
    session.progress_message = "Rapport prêt !"
    session.save(update_fields=["status", "completed_at", "progress_message"])
    return {"ok": True, "report_id": report.pk}
