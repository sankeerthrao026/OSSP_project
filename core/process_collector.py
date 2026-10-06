import psutil
import time
import pandas as pd
from datetime import datetime

class ProcessCollector:
    def __init__(self):
        # We need a small interval for cpu_percent to be meaningful, but
        # psutil.cpu_percent with interval=None will return > 0 after the first call.
        # We'll just call it once per process per update.
        pass

    def collect_system_metrics(self):
        """Collects global system metrics."""
        vm = psutil.virtual_memory()
        metrics = {
            "os_name": psutil.os.name,
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_usage_percent": psutil.cpu_percent(interval=None),
            "total_memory_gb": vm.total / (1024**3),
            "available_memory_gb": vm.available / (1024**3),
            "memory_usage_percent": vm.percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        return metrics

    def collect_processes(self):
        """Collects metrics for all running processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'num_threads', 'create_time']):
            try:
                p_info = proc.info
                
                # Try to get extra info which might throw AccessDenied
                try:
                    io_counters = proc.io_counters()
                    read_bytes = io_counters.read_bytes
                    write_bytes = io_counters.write_bytes
                    read_count = io_counters.read_count
                    write_count = io_counters.write_count
                except (psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                    read_bytes = 0
                    write_bytes = 0
                    read_count = 0
                    write_count = 0
                
                try:
                    child_count = len(proc.children())
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    child_count = 0
                    
                # Calculate process age
                try:
                    create_time = p_info.get('create_time')
                    if create_time:
                        process_age = time.time() - create_time
                    else:
                        process_age = 0
                except (TypeError, ValueError):
                    process_age = 0
                    
                processes.append({
                    "pid": p_info['pid'],
                    "name": p_info['name'],
                    "status": p_info['status'],
                    "cpu_percent": p_info['cpu_percent'] if p_info['cpu_percent'] is not None else 0.0,
                    "memory_percent": p_info['memory_percent'] if p_info['memory_percent'] is not None else 0.0,
                    "num_threads": p_info['num_threads'] if p_info['num_threads'] is not None else 0,
                    "read_bytes": read_bytes,
                    "write_bytes": write_bytes,
                    "read_count": read_count,
                    "write_count": write_count,
                    "process_age_seconds": process_age,
                    "child_count": child_count,
                    "timestamp": time.time()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return pd.DataFrame(processes)
