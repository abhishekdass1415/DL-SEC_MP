from flask import Blueprint, request, jsonify
import logging

from services.streaming_service import streaming_service

logger = logging.getLogger(__name__)

stream_bp = Blueprint("stream", __name__)


@stream_bp.route("/start", methods=["POST"])
def start_stream():
    """
    Phase 3 spec endpoint.
    Delegates to existing /api/dataset/stream/start implementation via the same simulator.
    """
    try:
        data = request.get_json() or {}
        interval = data.get("interval", 2.0)
        source = data.get("source", "dataset")
        api_url = data.get("api_url") or data.get("apiUrl")
        session_id = data.get("session_id")

        from flask import current_app
        app_obj = current_app._get_current_object()
        result = streaming_service.start(
            app=app_obj,
            interval=interval,
            source=source,
            api_url=api_url,
            session_id=session_id,
        )
        if not result.get("success"):
            return jsonify(result), 409
        return jsonify(result), 200
    except Exception as exc:
        logger.error("Error configuring stream: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@stream_bp.route("/pause", methods=["POST"])
def pause_stream():
    """Pause streaming (stop without resetting dataset index)."""
    try:
        return jsonify(streaming_service.pause()), 200
    except Exception as exc:
        logger.error("Error pausing stream: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@stream_bp.route("/reset", methods=["POST"])
def reset_stream():
    """Reset stream progress and metrics."""
    try:
        return jsonify(streaming_service.reset()), 200
    except Exception as exc:
        logger.error("Error resetting stream: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@stream_bp.route("/status", methods=["GET"])
def stream_status():
    try:
        return jsonify(streaming_service.status()), 200
    except Exception as exc:
        logger.error("Error reading stream status: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500

