from mcprotocol import SecureServer
import psutil
import time
from typing import Dict, Any
from dataclasses import dataclass
import logging
from datetime import datetime
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Data class to store system performance metrics"""
    cpu_percent: float
    memory_percent: float 
    memory_available: int
    memory_total: int
    disk_usage: Dict[str, float]
    network_sent: int
    network_received: int
    timestamp: datetime

class PerformanceMonitor(SecureServer):
    """Enhanced system performance monitoring class"""
    
    def __init__(self):
        super().__init__()
        self._metrics_history = []
        self._max_history_size = 1000
        
    def _get_disk_metrics(self) -> Dict[str, float]:
        """Collect disk usage metrics for all partitions"""
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = usage.percent
            except Exception as e:
                logger.error(f"Failed to get disk usage for {partition.mountpoint}: {e}")
        return disk_usage

    def _collect_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        try:
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=memory.percent,
                memory_available=memory.available,
                memory_total=memory.total,
                disk_usage=self._get_disk_metrics(),
                network_sent=network.bytes_sent,
                network_received=network.bytes_recv,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            raise

    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in history with size limit"""
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history.pop(0)

    @endpoint('/v1/system/monitor')
    def monitor_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced endpoint for system monitoring
        Returns current system metrics and basic statistical analysis
        """
        try:
            # Collect current metrics
            current_metrics = self._collect_metrics()
            self._store_metrics(current_metrics)
            
            # Calculate averages from history
            if self._metrics_history:
                avg_cpu = sum(m.cpu_percent for m in self._metrics_history) / len(self._metrics_history)
                avg_memory = sum(m.memory_percent for m in self._metrics_history) / len(self._metrics_history)
            else:
                avg_cpu = avg_memory = 0

            return {
                "current": {
                    "cpu": current_metrics.cpu_percent,
                    "memory": {
                        "percent": current_metrics.memory_percent,
                        "available": current_metrics.memory_available,
                        "total": current_metrics.memory_total
                    },
                    "disk": current_metrics.disk_usage,
                    "network": {
                        "bytes_sent": current_metrics.network_sent,
                        "bytes_received": current_metrics.network_received
                    },
                    "timestamp": current_metrics.timestamp.isoformat()
                },
                "statistics": {
                    "avg_cpu_percent": round(avg_cpu, 2),
                    "avg_memory_percent": round(avg_memory, 2),
                    "samples_count": len(self._metrics_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in monitor_performance: {e}")
            return {
                "error": str(e),
                "status": "error"
            }

    @endpoint('/v1/system/monitor/history')
    def get_metrics_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Endpoint to retrieve historical metrics"""
        try:
            limit = params.get('limit', 100)
            history = self._metrics_history[-limit:]
            
            return {
                "history": [
                    {
                        "cpu": m.cpu_percent,
                        "memory": m.memory_percent,
                        "timestamp": m.timestamp.isoformat()
                    } for m in history
                ],
                "total_samples": len(self._metrics_history)
            }
        except Exception as e:
            logger.error(f"Error in get_metrics_history: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
