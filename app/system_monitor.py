"""
System Monitor - Extended system diagnostics
CPU, Memory, Disk, Network, Temperatures, Processes
"""
import psutil
import socket
import platform
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class SystemStats(BaseModel):
    """System statistics model"""
    timestamp: str
    hostname: str
    uptime: float
    os_type: str
    os_version: str
    kernel_version: str
    cpu_model: str

    # CPU
    cpu_percent: float
    cpu_count: int
    cpu_freq: Optional[float] = None
    load_avg: List[float]

    # Memory
    memory_total: int
    memory_used: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

    # Disk
    disk_usage: List[Dict]

    # Network
    network_io: Dict[str, Dict]
    active_connections: int

    # Temperatures (if available)
    temperatures: Dict[str, float] = {}

    # Top processes
    top_processes: List[Dict]


class SystemMonitor:
    """Monitor system statistics"""

    def __init__(self):
        self.boot_time = psutil.boot_time()
        self._last_net_io = psutil.net_io_counters(pernic=True)

    async def get_stats(self) -> SystemStats:
        """Get current system statistics"""

        # System info
        os_type = platform.system()
        os_version = platform.version()
        kernel_version = platform.release()

        # CPU model
        cpu_model = "Unknown"
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_model = line.split(':')[1].strip()
                        break
        except:
            cpu_model = platform.processor() or "Unknown"

        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        try:
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else None
        except:
            cpu_freq = None
        load_avg = list(psutil.getloadavg())

        # Memory
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk usage
        disk_usage = []
        for partition in psutil.disk_partitions():
            if partition.fstype:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue

        # Network I/O
        net_io = self._get_network_io()

        # Active connections
        active_connections = len(psutil.net_connections(kind='inet'))

        # Temperatures
        temperatures = self._get_temperatures()

        # Top processes by CPU
        top_processes = self._get_top_processes()

        # Uptime
        uptime = datetime.now().timestamp() - self.boot_time

        return SystemStats(
            timestamp=datetime.now().isoformat(),
            hostname=socket.gethostname(),
            uptime=uptime,
            os_type=os_type,
            os_version=os_version,
            kernel_version=kernel_version,
            cpu_model=cpu_model,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_freq=cpu_freq,
            load_avg=load_avg,
            memory_total=mem.total,
            memory_used=mem.used,
            memory_percent=mem.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent,
            disk_usage=disk_usage,
            network_io=net_io,
            active_connections=active_connections,
            temperatures=temperatures,
            top_processes=top_processes
        )

    def _get_network_io(self) -> Dict[str, Dict]:
        """Get network I/O by interface with rate calculation"""
        current_net_io = psutil.net_io_counters(pernic=True)
        net_io = {}

        for interface, stats in current_net_io.items():
            # Skip loopback
            if interface == 'lo':
                continue

            net_io[interface] = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errors_in': stats.errin,
                'errors_out': stats.errout,
                'drops_in': stats.dropin,
                'drops_out': stats.dropout
            }

        self._last_net_io = current_net_io
        return net_io

    def _get_temperatures(self) -> Dict[str, float]:
        """Get system temperatures if available"""
        temps = {}
        try:
            temps_dict = psutil.sensors_temperatures()
            if temps_dict:
                for name, entries in temps_dict.items():
                    for entry in entries:
                        key = f"{name}_{entry.label}" if entry.label else name
                        temps[key] = entry.current
        except (AttributeError, OSError):
            # Temperature sensors not available on this system
            pass
        return temps

    def _get_top_processes(self, limit: int = 10) -> List[Dict]:
        """Get top processes by CPU usage"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                info['cpu_percent'] = info.get('cpu_percent', 0.0) or 0.0
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        return processes[:limit]
