#report.py
from flask import Blueprint, jsonify, send_file, current_app
import io
import logging

from services.report_service import generate_pdf_report

logger = logging.getLogger(__name__)

report_bp = Blueprint("report", __name__)


@report_bp.route("/generate", methods=["POST"])
def generate_report():
    """
    Generate a PDF report with current system metrics and threat summary.

    Returns a downloadable PDF file.
    """
    try:
        pdf_bytes, filename = generate_pdf_report(current_app)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        logger.error("Error generating report PDF: %s", exc, exc_info=True)
        return jsonify({"error": "Failed to generate report"}), 500

