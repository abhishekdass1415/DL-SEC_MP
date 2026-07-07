#data_simulator.py
import random
import time
import threading
from datetime import datetime
from typing import Dict, Callable
import logging
import json
from urllib import request as urlrequest, error as urlerror

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSimulator:
    """Service for simulating or streaming real-time network traffic data.

    This class supports three modes:
      - Dataset: stream from the currently loaded dataset
      - API: poll an external API endpoint that returns JSON records
      - Mock: generate synthetic data for demo/testing
    """

    def __init__(self):
        self.is_running = False
        self.thread = None
        self.interval = 2.0  # seconds between data points
        self.callback = None
        self.use_dataset = False
        self.dataset_service = None

        # Extended streaming configuration
        self.source = "dataset"  # 'dataset' | 'api' | 'mock'
        self.api_url = None

    def set_dataset_service(self, dataset_service):
        """Set the dataset service to use for streaming real data"""
        self.dataset_service = dataset_service
        self.use_dataset = True

    def configure(self, source: str = "dataset", api_url: str = None, interval: float = None):
        """Configure the streaming source and optional API URL.

        This does not start or stop streaming; it only updates the
        configuration that will be used the next time streaming starts.
        """
        if source not in ("dataset", "api", "mock"):
            source = "dataset"

        self.source = source
        self.api_url = api_url
        if interval is not None:
            self.interval = float(interval)

        logger.info("DataSimulator configured: source=%s api_url=%s interval=%s",
                    self.source, self.api_url, self.interval)

    def generate_mock_data(self) -> Dict:
        """
        Generate mock network traffic data
        Returns:
            Dictionary with mock network traffic features
        """
        # Generate random IP addresses
        src_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        dst_ip = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # Generate random protocol
        protocols = ['tcp', 'udp', 'icmp']
        proto = random.choice(protocols)
        
        # Generate random service
        services = ['http', 'https', 'ftp', 'ssh', 'dns', 'smtp', 'unknown']
        service = random.choice(services)
        
        # Generate random state
        states = ['FIN', 'INT', 'CON', 'REQ', 'RST', 'ACC']
        state = random.choice(states)
        
        # Generate numerical features (realistic ranges)
        data = {
            'srcip': src_ip,
            'sport': random.randint(1024, 65535),
            'dstip': dst_ip,
            'dsport': random.randint(1, 65535),
            'proto': proto,
            'service': service,
            'state': state,
            'dur': round(random.uniform(0.0, 3600.0), 2),
            'sbytes': random.randint(0, 1000000),
            'dbytes': random.randint(0, 1000000),
            'sttl': random.randint(0, 255),
            'dttl': random.randint(0, 255),
            'sloss': random.randint(0, 100),
            'dloss': random.randint(0, 100),
            'service': service,
            'sload': round(random.uniform(0.0, 1000000.0), 2),
            'dload': round(random.uniform(0.0, 1000000.0), 2),
            'spkts': random.randint(1, 1000),
            'dpkts': random.randint(1, 1000),
            'swin': random.randint(0, 65535),
            'dwin': random.randint(0, 65535),
            'stcpb': random.randint(0, 1000000),
            'dtcpb': random.randint(0, 1000000),
            'smeansz': random.randint(0, 1500),
            'dmeansz': random.randint(0, 1500),
            'trans_depth': random.randint(0, 10),
            'res_bdy_len': random.randint(0, 10000),
            'sjit': round(random.uniform(0.0, 1000.0), 2),
            'djit': round(random.uniform(0.0, 1000.0), 2),
            'stime': datetime.utcnow().isoformat(),
            'ltime': datetime.utcnow().isoformat(),
            'sinpkt': round(random.uniform(0.0, 10.0), 4),
            'dinpkt': round(random.uniform(0.0, 10.0), 4),
            'tcprtt': round(random.uniform(0.0, 1.0), 4),
            'synack': round(random.uniform(0.0, 1.0), 4),
            'ackdat': round(random.uniform(0.0, 1.0), 4),
            'is_sm_ips_ports': random.randint(0, 1),
            'ct_state_ttl': random.randint(0, 10),
            'ct_flw_http_mthd': random.randint(0, 10),
            'is_ftp_login': random.randint(0, 1),
            'ct_ftp_cmd': random.randint(0, 10),
            'ct_srv_src': random.randint(0, 100),
            'ct_srv_dst': random.randint(0, 100),
            'ct_dst_ltm': random.randint(0, 100),
            'ct_src_ltm': random.randint(0, 100),
            'ct_src_dport_ltm': random.randint(0, 100),
            'ct_dst_sport_ltm': random.randint(0, 100),
            'ct_dst_src_ltm': random.randint(0, 100),
            'attack_cat': 'Normal' if random.random() > 0.3 else random.choice(['Fuzzers', 'Analysis', 'Backdoors', 'DoS', 'Exploits', 'Generic', 'Reconnaissance', 'Shellcode', 'Worms']),
            'label': 1 if random.random() > 0.7 else 0
        }
        
        return data

    def _fetch_api_record(self) -> Dict:
        """
        Fetch a single record from an external API.

        The external API is expected to return JSON that is either:
          - a single object representing one record, or
          - a list of objects, in which case the first one is used.
        """
        if not self.api_url:
            raise ValueError("API URL not configured for API streaming")

        try:
            with urlrequest.urlopen(self.api_url, timeout=5.0) as resp:
                content_type = resp.headers.get("Content-Type", "")
                body = resp.read().decode("utf-8")

            if "application/json" not in content_type and not body.strip().startswith(("{", "[")):
                raise ValueError("API response is not JSON")

            data = json.loads(body)
            if isinstance(data, list):
                if not data:
                    raise ValueError("API returned an empty list")
                return data[0]
            elif isinstance(data, dict):
                return data
            else:
                raise ValueError("Unsupported JSON structure from API")

        except (urlerror.URLError, urlerror.HTTPError, TimeoutError) as exc:
            logger.error("Error fetching data from external API %s: %s", self.api_url, exc)
            raise

    def start_streaming(
        self,
        callback: Callable,
        interval: float = 2.0,
        use_dataset: bool = False,
        source: str = None,
        api_url: str = None,
    ):
        """
        Start streaming data in real-time
        Args:
            callback: Function to call with each data point
            interval: Seconds between data points
            use_dataset: Whether to use dataset or generate mock data
        """
        if self.is_running:
            logger.warning("Streaming already in progress")
            return

        # Preserve previous configuration unless overridden
        if source:
            self.source = source
        else:
            # Backwards-compat: derive from use_dataset flag
            self.source = "dataset" if use_dataset else "mock"

        if api_url:
            self.api_url = api_url

        self.callback = callback
        self.interval = interval
        self.use_dataset = self.source == "dataset"
        self.is_running = True

        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()

        logger.info(
            "Data streaming started (interval=%ss, source=%s, api_url=%s)",
            interval,
            self.source,
            self.api_url,
        )

    def stop_streaming(self):
        """Stop streaming data"""
        if not self.is_running:
            return

        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5.0)

        logger.info("Data streaming stopped")

    def _stream_loop(self):
        """Internal loop for streaming data"""
        try:
            while self.is_running:
                if self.source == "dataset" and self.dataset_service:
                    # Get next record from dataset
                    record = self.dataset_service.get_next_record()
                    if record is None:
                        # End of dataset, reset or stop
                        logger.info("End of dataset reached")
                        self.is_running = False
                        break
                    data = record
                elif self.source == "api":
                    try:
                        data = self._fetch_api_record()
                    except Exception:
                        # If API fails, wait and continue or break based on policy
                        time.sleep(self.interval)
                        continue
                else:
                    # Generate mock data
                    data = self.generate_mock_data()

                # Call callback with data
                if self.callback:
                    try:
                        self.callback(data)
                    except Exception as e:
                        logger.error(f"Error in streaming callback: {str(e)}")

                # Wait for interval
                time.sleep(self.interval)

        except Exception as e:
            logger.error(f"Error in streaming loop: {str(e)}")
            self.is_running = False

    def get_status(self) -> Dict:
        """Get streaming status"""
        return {
            'is_running': self.is_running,
            'interval': self.interval,
            'use_dataset': self.use_dataset,
            'source': self.source,
            'api_url': self.api_url,
        }


# Global data simulator instance
data_simulator = DataSimulator()
