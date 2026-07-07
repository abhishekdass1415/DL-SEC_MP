#streaming_service.py
import logging
import threading
from typing import Optional, Dict, Any

from services.data_simulator import data_simulator
from services.dataset_service import dataset_service
from services.model_service import model_service
from services.metrics_service import metrics_service
from services.action_service import action_service

from database.db import db
from database.models import Threat, Alert, StreamingSession, Prediction


logger = logging.getLogger(__name__)

# Will be injected by app.py (same pattern as routes/* modules)
socketio = None


class StreamingService:
    """
    Central streaming engine that:
    - reads records (dataset / api / mock) using DataSimulator
    - runs inference
    - stores Threats + Alerts
    - updates MetricsService
    - emits SocketIO events for live dashboard updates
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_session_id: Optional[int] = None
        self._active_source: str = "dataset"

    def start(
        self,
        app,
        interval: float = 2.0,
        source: str = "dataset",
        api_url: Optional[str] = None,
        session_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            if data_simulator.is_running:
                return {"success": False, "error": "Streaming already running"}
            self._active_session_id = session_id
            self._active_source = source or "dataset"

        # Configure simulator and metrics source
        data_simulator.configure(source=self._active_source, api_url=api_url, interval=interval)
        metrics_service.on_stream_source_configured(self._active_source)

        # Ensure dataset service is set if streaming from dataset
        if self._active_source == "dataset":
            data_simulator.set_dataset_service(dataset_service)

        def on_record(record: Dict[str, Any]) -> None:
            # Background thread callback – must use app context for DB and current_app
            try:
                with app.app_context():
                    self._handle_record(app, record)
            except Exception as exc:
                logger.error("Streaming record handler failed: %s", exc, exc_info=True)

        data_simulator.start_streaming(
            on_record,
            interval=interval,
            use_dataset=self._active_source == "dataset",
            source=self._active_source,
            api_url=api_url,
        )

        # Mark session as streaming if provided
        if session_id is not None:
            try:
                sess = StreamingSession.query.get(int(session_id))
                if sess:
                    sess.status = "streaming"
                    db.session.commit()
            except Exception as exc:
                logger.error("Failed to mark session streaming: %s", exc, exc_info=True)
                db.session.rollback()

        return {
            "success": True,
            "message": "Streaming started",
            "interval": interval,
            "source": self._active_source,
            "api_url": api_url,
            "session_id": session_id,
        }

    def pause(self) -> Dict[str, Any]:
        data_simulator.stop_streaming()
        # Update session state if present
        sid = self._active_session_id
        if sid is not None:
            try:
                sess = StreamingSession.query.get(int(sid))
                if sess:
                    sess.status = "paused"
                    db.session.commit()
            except Exception:
                db.session.rollback()
        return {"success": True, "message": "Streaming paused"}

    def reset(self) -> Dict[str, Any]:
        data_simulator.stop_streaming()
        dataset_service.reset_stream()
        metrics_service.reset()

        sid = self._active_session_id
        if sid is not None:
            try:
                sess = StreamingSession.query.get(int(sid))
                if sess:
                    sess.processed_records = 0
                    sess.status = "ready"
                    db.session.commit()
            except Exception:
                db.session.rollback()

        return {"success": True, "message": "Streaming reset"}

    def status(self) -> Dict[str, Any]:
        base = data_simulator.get_status()
        base["session_id"] = self._active_session_id
        return base

    # -------------------------
    # Internal helpers
    # -------------------------
    def _handle_record(self, app, record_data: Dict[str, Any]) -> None:
        prediction = model_service.predict(record_data)
        is_threat = bool(prediction.get("is_threat"))

        # Update metrics first (counts all processed records)
        metrics_service.on_record_processed(is_threat=is_threat)

        # Update streaming session progress (counts all processed records)
        sid = self._active_session_id
        sess = None
        if sid is not None:
            try:
                sess = StreamingSession.query.get(int(sid))
                if sess:
                    sess.processed_records = int(sess.processed_records or 0) + 1
                    sess.status = "streaming"
            except Exception as exc:
                logger.error("Failed to update StreamingSession progress: %s", exc, exc_info=True)

        # Create Threat + Alert when malicious
        threat = None
        if is_threat:
            threat = Threat(
                threat_type=prediction.get("threat_type", "Unknown"),
                severity=prediction.get("severity", "Low"),
                source_ip=record_data.get("srcip", record_data.get("source_ip", "Unknown")),
                destination_ip=record_data.get("dstip", record_data.get("destination_ip", "Unknown")),
                confidence=float(prediction.get("confidence", 0.0) or 0.0),
                details=record_data,
                status="active",
            )
            db.session.add(threat)
            db.session.flush()

            alert = Alert(
                attack_type=threat.threat_type,
                severity=threat.severity,
                source_ip=threat.source_ip,
                destination_ip=threat.destination_ip,
                confidence=threat.confidence,
                threat_id=threat.id,
            )
            db.session.add(alert)

            # Also create prediction row linked to this threat
            pred_row = Prediction(
                source_type=self._active_source,
                session_id=sess.id if sess is not None else None,
                threat_id=threat.id,
                is_threat=True,
                label="attack",
                severity=prediction.get("severity"),
                attack_type=prediction.get("threat_type"),
                confidence=float(prediction.get("confidence", 0.0) or 0.0),
                raw_score=float(prediction.get("raw_prediction", 0.0) or 0.0),
                source_ip=threat.source_ip,
                destination_ip=threat.destination_ip,
            )
            db.session.add(pred_row)

            db.session.commit()

            actions = action_service.generate_actions(threat)

            if socketio:
                socketio.emit(
                    "new_threat",
                    {
                        "threat": threat.to_dict(),
                        "actions": [a.to_dict() for a in actions],
                        "prediction": prediction,
                    },
                )
                socketio.emit("alert", alert.to_dict())
        else:
            # Normal activity: store prediction without threat_id
            pred_row = Prediction(
                source_type=self._active_source,
                session_id=sess.id if sess is not None else None,
                threat_id=None,
                is_threat=False,
                label="benign",
                severity=prediction.get("severity"),
                attack_type=prediction.get("threat_type"),
                confidence=float(prediction.get("confidence", 0.0) or 0.0),
                raw_score=float(prediction.get("raw_prediction", 0.0) or 0.0),
                source_ip=record_data.get("srcip", record_data.get("source_ip", "Unknown")),
                destination_ip=record_data.get("dstip", record_data.get("destination_ip", "Unknown")),
            )
            db.session.add(pred_row)

            db.session.commit()

            # Normal activity is still useful for UI live feed
            if socketio:
                socketio.emit("normal_activity", {"record": record_data, "prediction": prediction})

        # Commit session progress if it was updated (may already be committed above)
        if sess is not None:
            try:
                # Mark completion if we reached total (dataset mode)
                if sess.total_records and sess.processed_records >= sess.total_records:
                    sess.status = "completed"
                db.session.commit()
            except Exception:
                db.session.rollback()

        # Push updated unified metrics for dashboard
        if socketio:
            try:
                payload = metrics_service.get_full_metrics_payload(app=app)
                socketio.emit("metrics_update", payload)
            except Exception as exc:
                logger.error("Failed to emit metrics_update: %s", exc, exc_info=True)


streaming_service = StreamingService()

