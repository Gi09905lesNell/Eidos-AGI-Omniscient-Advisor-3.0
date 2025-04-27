from mcprotocol import SecureServer
import psutil

class PerformanceMonitor(SecureServer):
    @endpoint('/v1/system/monitor')
    def monitor_performance(self, params):
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "network": psutil.net_io_counters().bytes_sent
        }