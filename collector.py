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
    
   # Return the current overall system CPU utilization as a percentage (float).
    
    return psutil.cpu_percent(interval=1.0, percpu=False)


def get_memory_usage():
    
   # Return a dictionary with total memory, used memory, and percentage used.
    
    mem = psutil.virtual_memory()
    return {
        'total_bytes': mem.total,  
        'used_bytes': mem.used,  
        'percent': mem.percent  
    }


def get_storage():
    
   # Return disk usage stats for the root filesystem ('/').
  
    disk = psutil.disk_usage('/')
    return {
        'total_bytes': disk.total,
        'free_bytes':   disk.free,
        'percent_used': disk.percent,
    }


def get_top_processes(n=3):
    
   # Return a list of the top n processes sorted by current CPU usage (descending).
    
    processes = []

    for proc in psutil.process_iter(['pid', 'name']):
            try:
                cpu = proc.cpu_percent(interval=0.1) 
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
