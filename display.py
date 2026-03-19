import os
import psutil
import time
import sys
from datetime import datetime

# For colors
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

    class Dummy:
        RED = ""
        GREEN = ""
        YELLOW = ""
        WHITE = ""
        RESET_ALL = ""
    Fore = dummy()
    Style = dummy()

def clear_screen():
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()

def seconds_to_human_uptime(seconds: float) -> str:
    if seconds < 0:
        return "???"

    total_sec = int(seconds)
    days, rem = divmod(total_sec, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    if not parts:  
        parts.append(f"{seconds}s")

    return " ".join(parts)


def print_dashboard(data: dict):

    clear_screen()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header
    print("═" * 42)
    print(f"{' SYSMON - Linux Monitor ':^42}")
    print("═" * 42)
    print(f"  {now}")
    print()

    # Basic system info
    uptime_str = seconds_to_human_uptime(data.get('uptime_seconds', 0))

    cpu = data.get('cpu_usage', 0.0)
    cpu_color = Fore.YELLOW if cpu > 80 else Fore.GREEN if cpu < 40 else Fore.WHITE

    mem = data.get('memory_usage', {})
    mem_used = mem.get('used_bytes', 0) / (1024**3)
    mem_total = mem.get('total_bytes', 0) / (1024**3)
    mem_pct = mem.get('percent', 0)
    mem_color = Fore.RED if mem_pct > 90 else Fore.YELLOW if mem_pct > 75 else Fore.GREEN

    disk = data.get('storage', {})
    disk_free_gb = disk.get('free_bytes', 0) / (1024 ** 3)
    disk_used_pct = disk.get('percent_used', 0)
    disk_color = Fore.RED if disk_used_pct > 90 else Fore.YELLOW if disk_used_pct > 80 else Fore.GREEN

    if COLOR:
        print(f"{'OS       :':<12} Linux")
        print(f"{'Uptime   :':<12} {uptime_str}")
        print(f"{'CPU Usage:':<12} {cpu_color}{cpu:5.1f}%{Style.RESET_ALL}")
        print(f"{'Memory   :':<12} {mem_color}{mem_used:4.1f} / {mem_total:4.1f} GB  ({mem_pct:4.1f}%){Style.RESET_ALL}")
        print(f"{'Storage  :':<12} {disk_color}{disk_free:5.1f} GB free  ({disk_used_pct:5.1f}% used){Style.RESET_ALL}")
    else:
        print(f"{'OS       :':<12} Linux")
        print(f"{'Uptime   :':<12} {uptime_str}")
        print(f"{'CPU Usage:':<12} {cpu:5.1f}%")
        print(f"{'Memory   :':<12} {mem_used:4.1f} / {mem_total:4.1f} GB  ({mem_pct:4.1f}%)")
        print(f"{'Storage  :':<12} {disk_free:5.1f} GB free  ({disk_used_pct:5.1f}% used)")

    print()
    print("TOP PROCESSES".center(42))
    print("─" * 42)

    top_procs = data.get('top_processes', [])
    if not top_procs:
        print("  (no processes found)".center(42))
    else:
        print(f"{'PID':>6}  {'NAME':<24}  {'CPU%':>6}")
        print("─" * 42)

        for proc in top_procs[:8]:  
            cpu = proc.get('cpu_percent', 0.0)
            original_name = proc.get('name', '???')
            if len(original_name) > 23:
                name = original_name[:22] + "..."
            else:
                name = original_name
            print(f"{proc['pid']:>6}  {name:<24}  {cpu:>6.1f}%")

    print("═" * 42)


# Standalone test
if __name__ == "__main__":
    test_data = {
        'uptime_seconds': 2 * 86400 + 4 * 3600 + 13 * 60 + 42,
        'cpu_usage': 42.3,
        'memory_usage': {
            'total_bytes': 16 * 1024 ** 3,
            'used_bytes': 6.1 * 1024 ** 3,
            'percent': 38.2
        },
        'storage': {
            'free_bytes': 2 * 10000,
            'percent_used': 61.0
        },
        'top_processes': [
            {'pid': 1234, 'name': 'chrome', 'cpu_percent': 18.2},
            {'pid': 5678, 'name': 'python3', 'cpu_percent': 9.4},
            {'pid': 91011, 'name': 'code', 'cpu_percent': 3.1},
            {'pid': 4242, 'name': 'firefox', 'cpu_percent': 2.8},
        ]
    }

    try:
        while True:
            print_dashboard(test_data)
            time.sleep(3)
    except KeyboardInterrupt:
        clear_screen()
        print("Stopped.")
