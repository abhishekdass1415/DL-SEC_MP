#analytics.py
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import logging

from database.models import Prediction

logger = logging.getLogger(__name__)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/summary", methods=["GET"])
def analytics_summary():
    """
    High-level analytics for ThreatAnalytics charts.

    Returns:
      {
        "byType": [{ "name": "DDoS", "value": 10 }, ...],
        "overTime": [{ "time": "...", "threats": 5 }, ...]
      }
    """
    try:
        # Last 24h window
        now = datetime.utcnow()
        window_start = now - timedelta(hours=24)

        preds = (
            Prediction.query
            .filter(Prediction.timestamp >= window_start)
            .order_by(Prediction.timestamp.asc())
            .all()
        )

        # Threat distribution by attack_type (only is_threat=True)
        type_counts = {}
        # Threats over time: bucket by hour
        time_buckets = {}

        for p in preds:
            if p.is_threat:
                key = p.attack_type or "Unknown"
                type_counts[key] = type_counts.get(key, 0) + 1

                hour = p.timestamp.replace(minute=0, second=0, microsecond=0)
                time_buckets[hour] = time_buckets.get(hour, 0) + 1

        by_type = [{"name": name, "value": value} for name, value in type_counts.items()]
        if not by_type:
            by_type = [{"name": "No Data", "value": 1}]

        over_time = [
            {"time": ts.isoformat(), "threats": count}
            for ts, count in sorted(time_buckets.items(), key=lambda kv: kv[0])
        ]

        return jsonify({"byType": by_type, "overTime": over_time}), 200
    except Exception as exc:
        logger.error("Error building analytics summary: %s", exc, exc_info=True)
        return jsonify({"error": "Failed to build analytics summary"}), 500

