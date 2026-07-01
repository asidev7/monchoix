"""Render an OrientationReport to a PDF file (WeasyPrint)."""
import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def build_report_pdf(report):
    """Render the report to PDF and store it on report.pdf_file. Returns bool success."""
    try:
        from weasyprint import HTML
    except Exception as exc:  # pragma: no cover
        logger.warning("WeasyPrint unavailable: %s", exc)
        return False

    html = render_to_string("orientation/report_pdf.html", {"report": report, "session": report.session})
    buffer = BytesIO()
    HTML(string=html).write_pdf(buffer)
    report.pdf_file.save(f"rapport-{report.pk}.pdf", ContentFile(buffer.getvalue()), save=True)
    return True
