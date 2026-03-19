import psutil
import os
import time



def get_uptime():
    """
    Read /proc/uptime directly and return system uptime in seconds as a float.
    Returns 0.0 if reading fails.
    """
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return uptime_seconds
    except (IOError, IndexError, ValueError):
        return 0.0


def get_cpu_usage():
    """
    Return the current overall system CPU utilization as a percentage (float).
    Uses psutil.cpu_percent() with a short interval for a meaningful value.
    """
    # interval=1 gives a reasonably accurate measurement over 1 second
    # interval=0 returns the value since last call (good for repeated polling)
    # For first call or one-shot use, interval > 0 is better
    return psutil.cpu_percent(interval=1.0, percpu=False)


def get_memory_usage():
    """
    Return a dictionary with total memory, used memory, and percentage used.
    All memory values are in bytes (as returned by psutil).
    """
    mem = psutil.virtual_memory()
    return {
        'total_bytes': mem.total,  # in bytes
        'used_bytes': mem.used,  # in bytes (actual in-use RAM)
        'percent': mem.percent  # already calculated percentage
    }


def get_storage():
    """
    Return disk usage stats for the root filesystem ('/').
    Returns free space in GB and percentage used.
    """
    disk = psutil.disk_usage('/')
    return {
        'total_bytes': disk.total,
        'free_bytes':   disk.free,
        'percent_used': disk.percent,
    }


def get_top_processes(n=3):
    """
    Return a list of the top n processes sorted by current CPU usage (descending).
    Each process is represented as a dict with: pid, name, cpu_percent.

    Note: cpu_percent values may be 0.0 on the very first call unless an interval is used.
    """
    processes = []

    # We iterate over all processes and collect the attributes we need
    # Collect + measure in one go (slower but very simple)
    for proc in psutil.process_iter(['pid', 'name']):
            try:
                cpu = proc.cpu_percent(interval=0.1)  # small per-process interval
                processes.append({
                    'pid': proc.pid,
                    'name': proc.name() or '<unknown>',
                    'cpu_percent': cpu
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
    return processes[:n]

def collect_metrics():
    return {
        'uptime_seconds': get_uptime(),
        'cpu_usage':      get_cpu_usage(),
        'memory_usage':   get_memory_usage(),
        'storage':        get_storage(),
        'top_processes':  get_top_processes(n=3),
    }