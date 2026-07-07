#report_service.py
import io
from typing import Tuple
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from database.models import Threat, Alert, Prediction
from database.db import db
from services.metrics_service import metrics_service


def generate_pdf_report(app) -> Tuple[bytes, str]:
    """
    Generate a PDF report summarizing system state, threats, and model metrics.

    Returns (pdf_bytes, filename).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Header
    story.append(Paragraph("DL-SEC Cybersecurity Report", styles["Title"]))
    story.append(Paragraph(f"Generated at: {now}", styles["Normal"]))
    story.append(Spacer(1, 16))

    # Metrics
    with app.app_context():
        payload = metrics_service.get_full_metrics_payload(app=app)
        dataset = payload.get("dataset", {})
        models = payload.get("models", {})

        story.append(Paragraph("System Health & Dataset Metrics", styles["Heading2"]))
        ds_table_data = [
            ["Total Records", str(dataset.get("totalRecords", 0))],
            ["Processed Records", str(dataset.get("currentIndex", 0))],
            ["Threats Detected", str(dataset.get("threatsDetected", 0))],
            ["Remaining Records", str(dataset.get("remaining", 0))],
            ["Source Type", dataset.get("source", "-")],
        ]
        ds_table = Table(ds_table_data, hAlign="LEFT")
        ds_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(ds_table)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Model Metrics", styles["Heading2"]))
        model_rows = [["Model", "Accuracy", "Precision", "Recall", "F1 Score"]]
        for key, label in (("cnn", "CNN"), ("lstm", "LSTM"), ("cnn_lstm", "CNN-LSTM")):
            m = models.get(key, {}) or {}
            model_rows.append(
                [
                    label,
                    f"{m.get('accuracy', 0):.3f}",
                    f"{m.get('precision', 0):.3f}",
                    f"{m.get('recall', 0):.3f}",
                    f"{m.get('f1', 0):.3f}",
                ]
            )
        model_table = Table(model_rows, hAlign="LEFT")
        model_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(model_table)
        story.append(Spacer(1, 16))

        # Threats & alerts
        story.append(Paragraph("Detected Threats (Top 10)", styles["Heading2"]))
        threats = (
            Threat.query.order_by(Threat.timestamp.desc())
            .limit(10)
            .all()
        )
        if threats:
            threat_rows = [["Time", "Type", "Severity", "Source IP", "Confidence"]]
            for t in threats:
                threat_rows.append(
                    [
                        t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        t.threat_type,
                        t.severity,
                        t.source_ip or "-",
                        f"{t.confidence:.3f}",
                    ]
                )
            threat_table = Table(threat_rows, hAlign="LEFT")
            threat_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(threat_table)
        else:
            story.append(Paragraph("No threats recorded.", styles["Normal"]))
        story.append(Spacer(1, 16))

        # Top risky IPs (simple aggregation based on threats)
        story.append(Paragraph("Top Risky Source IPs", styles["Heading2"]))
        if threats:
            counts = {}
            for t in threats:
                key = t.source_ip or "-"
                counts[key] = counts.get(key, 0) + 1
            sorted_ips = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
            ip_rows = [["Source IP", "Threat Count"]]
            for ip, count in sorted_ips:
                ip_rows.append([ip, str(count)])
            ip_table = Table(ip_rows, hAlign="LEFT")
            ip_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(ip_table)
        else:
            story.append(Paragraph("No high-risk IPs identified.", styles["Normal"]))
        story.append(Spacer(1, 16))

        # Top attack types (last 24 hours, based on predictions)
        story.append(Paragraph("Top Attack Types (Last 24 Hours)", styles["Heading2"]))
        now_dt = datetime.utcnow()
        window_start = now_dt - timedelta(hours=24)

        preds = (
            Prediction.query
            .filter(Prediction.is_threat.is_(True), Prediction.timestamp >= window_start)
            .all()
        )
        if preds:
            type_counts = {}
            for p in preds:
                key = p.attack_type or "Unknown"
                type_counts[key] = type_counts.get(key, 0) + 1
            sorted_types = sorted(type_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
            type_rows = [["Attack Type", "Count"]]
            for name, count in sorted_types:
                type_rows.append([name, str(count)])
            type_table = Table(type_rows, hAlign="LEFT")
            type_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(type_table)
        else:
            story.append(Paragraph("No attack types recorded in the last 24 hours.", styles["Normal"]))
        story.append(Spacer(1, 16))

        # Threat trend (last 24 hours, hour buckets)
        story.append(Paragraph("Threat Trend (Last 24 Hours)", styles["Heading2"]))
        if preds:
            buckets = {}
            for p in preds:
                hour = p.timestamp.replace(minute=0, second=0, microsecond=0)
                buckets[hour] = buckets.get(hour, 0) + 1
            trend_rows = [["Hour (UTC)", "Threats"]]
            for ts, count in sorted(buckets.items(), key=lambda kv: kv[0]):
                trend_rows.append([ts.strftime("%Y-%m-%d %H:00"), str(count)])
            trend_table = Table(trend_rows, hAlign="LEFT")
            trend_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(trend_table)
        else:
            story.append(Paragraph("No recent threat activity detected.", styles["Normal"]))
        story.append(Spacer(1, 16))

        # Recommended mitigation (static guidance for now)
        story.append(Paragraph("Recommended Mitigation Steps", styles["Heading2"]))
        recommendations = [
            "- Enable automated blocking for critical and high severity threats.",
            "- Monitor repeated connection attempts from the same IPs (possible brute-force).",
            "- Regularly retrain the detection model with recent traffic data.",
            "- Review firewall and IDS rules based on detected attack types.",
        ]
        for rec in recommendations:
            story.append(Paragraph(rec, styles["Normal"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f"dl-sec-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.pdf"
    return pdf_bytes, filename

