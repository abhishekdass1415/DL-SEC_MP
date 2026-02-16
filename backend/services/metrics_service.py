import os
import json
import threading
from typing import Dict, Any
import logging

from .dataset_service import dataset_service
from config import Config

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Central service for tracking dataset and model performance metrics.

    This service is intentionally lightweight and in-memory. It can be
    extended later to persist metrics to a database or files.
    """

    def __init__(self) -> None:
        # Dataset / streaming metrics
        self.source_type = "dataset"  # 'dataset' | 'api' | 'mock'
        self.total_records = 0
        self.current_index = 0
        self.threats_detected = 0

        # Model performance metrics for CNN, LSTM, and CNN+LSTM
        # Values are in [0, 1] and will be rendered as percentages in the UI.
        self.model_metrics = {
            "cnn": {"accuracy": 0.90, "precision": 0.88, "recall": 0.89, "f1": 0.885},
            "lstm": {"accuracy": 0.93, "precision": 0.91, "recall": 0.92, "f1": 0.915},
            "cnn_lstm": {"accuracy": 0.95, "precision": 0.94, "recall": 0.95, "f1": 0.945},
        }

        # Training state
        self.training_in_progress = False
        self._lock = threading.Lock()

        # Try to load any persisted metrics from disk
        self._load_persisted_metrics()

    # ------------------------------------------------------------------
    # Dataset / streaming helpers
    # ------------------------------------------------------------------
    def on_dataset_loaded(self, total_records: int) -> None:
        """Call when a new dataset is loaded or uploaded."""
        with self._lock:
            self.source_type = "dataset"
            self.total_records = int(total_records or 0)
            self.current_index = 0
            self.threats_detected = 0
            logger.info(
                "MetricsService: dataset loaded (total_records=%s)", self.total_records
            )

    def on_stream_source_configured(self, source_type: str) -> None:
        """Call when the streaming source changes (dataset vs external API)."""
        with self._lock:
            if source_type not in ("dataset", "api", "mock"):
                source_type = "dataset"
            self.source_type = source_type
            # When switching sources we keep counters but reset index for new streams
            self.current_index = 0
            self.threats_detected = 0
            if source_type != "dataset":
                # For API / mock we don't know total upfront; grow with processed records
                self.total_records = 0
            logger.info("MetricsService: stream source set to %s", source_type)

    def on_record_processed(self, is_threat: bool) -> None:
        """
        Call whenever a single record has been processed by the model.
        This is used both for manual batch processing and streaming.
        """
        with self._lock:
            self.current_index += 1
            if is_threat:
                self.threats_detected += 1

            # For API / mock streams we don't know total in advance,
            # so we treat total_records as "records seen so far".
            if self.source_type in ("api", "mock"):
                self.total_records = max(self.total_records, self.current_index)

    def reset(self) -> None:
        """Reset streaming-related counters."""
        with self._lock:
            self.current_index = 0
            self.threats_detected = 0
            if self.source_type in ("api", "mock"):
                self.total_records = 0
            logger.info("MetricsService: counters reset")

    # ------------------------------------------------------------------
    # Model metrics helpers
    # ------------------------------------------------------------------
    def get_model_metrics(self) -> Dict[str, Dict[str, float]]:
        with self._lock:
            return self.model_metrics.copy()

    def update_model_metrics(self, metrics: Dict[str, Dict[str, float]]) -> None:
        with self._lock:
            self.model_metrics.update(metrics)
            self._persist_metrics()

    def start_training(self) -> bool:
        """Mark training as started. Returns False if a run is already in progress."""
        with self._lock:
            if self.training_in_progress:
                return False
            self.training_in_progress = True
            return True

    def finish_training(self, new_metrics: Dict[str, Dict[str, float]]) -> None:
        """Mark training as finished and update metrics."""
        with self._lock:
            self.training_in_progress = False
            if new_metrics:
                self.model_metrics.update(new_metrics)
                self._persist_metrics()

    # ------------------------------------------------------------------
    # Aggregate / API payload helpers
    # ------------------------------------------------------------------
    def get_dataset_metrics_payload(self) -> Dict[str, Any]:
        """
        Build the dataset / streaming section for the /api/metrics endpoint.
        This uses both the DatasetService (for ground-truth counts) and the
        in-memory counters for processed records.
        """
        with self._lock:
            # Base stats from dataset_service if a dataset is loaded
            ds_stats = dataset_service.get_dataset_stats()

            total_records = (
                int(ds_stats.get("total_records", 0))
                if isinstance(ds_stats, dict) and "total_records" in ds_stats
                else self.total_records
            )

            current_index = self.current_index
            threats_detected = self.threats_detected

            remaining = max(total_records - current_index, 0)

            return {
                "source": self.source_type,
                "totalRecords": total_records,
                "currentIndex": current_index,
                "threatsDetected": threats_detected,
                "remaining": remaining,
            }

    def get_full_metrics_payload(self) -> Dict[str, Any]:
        """Full payload used by /api/metrics."""
        with self._lock:
            dataset_metrics = self.get_dataset_metrics_payload()
            models = self.model_metrics.copy()
            training = self.training_in_progress

        return {
            "dataset": dataset_metrics,
            "models": models,
            "training": {"inProgress": training},
        }

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    @property
    def _metrics_file_path(self) -> str:
        models_dir = Config.MODELS_DIR
        os.makedirs(models_dir, exist_ok=True)
        return os.path.join(models_dir, "metrics.json")

    def _load_persisted_metrics(self) -> None:
        path = self._metrics_file_path
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            models = data.get("models")
            if isinstance(models, dict):
                self.model_metrics.update(models)
                logger.info("MetricsService: loaded persisted model metrics from %s", path)
        except Exception as exc:
            logger.warning("MetricsService: failed to load metrics file %s: %s", path, exc)

    def _persist_metrics(self) -> None:
        path = self._metrics_file_path
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"models": self.model_metrics}, f, indent=2)
            logger.info("MetricsService: persisted model metrics to %s", path)
        except Exception as exc:
            logger.warning("MetricsService: failed to persist metrics to %s: %s", path, exc)


# Global metrics service instance
metrics_service = MetricsService()


