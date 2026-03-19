# alerting.py
"""
Stateless alerting logic for the Linux monitoring project.
All functions are pure: they take data and thresholds → return alert info.
No side effects, no state (except where explicitly passed for sustained checks).
"""

import time
from typing import Dict, Any, List, Tuple


def check_high_cpu_usage(
    data: Dict[str, Any],
    state: Dict[str, Any],
    threshold: float = 90.0,
    sustain_seconds: float = 3.0
) -> Tuple[str, str]:
    """
    Returns (level, message) or ("", "") if no alert.
    Uses state['cpu_high_since'] to track duration of high usage.
    """
    cpu = data.get('cpu_usage', 0.0)

    now = time.time()

    if cpu >= threshold:
        if state.get('cpu_high_since') is None:
            state['cpu_high_since'] = now
        elif now - state.get('cpu_high_since', 0) >= sustain_seconds:
            return "critical", f"CRITICAL: CPU sustained at {cpu:.1f}% for {sustain_seconds:.0f}+ seconds"
    else:
        # Reset when below threshold
        state['cpu_high_since'] = None

    return "", ""


def check_high_memory_usage(
    data: Dict[str, Any],
    warning_threshold: float = 85.0,
    critical_threshold: float = 95.0
) -> Tuple[str, str]:
    """
    Returns (level, message) or ("", "") if no alert.
    """
    mem = data.get('memory_usage', {}) or data.get('memory', {})
    percent = mem.get('percent', 0.0)

    if percent >= critical_threshold:
        return "critical", f"CRITICAL: Memory usage {percent:.1f}% (≥ {critical_threshold}%)"
    if percent >= warning_threshold:
        return "warning", f"WARNING: Memory usage {percent:.1f}% (≥ {warning_threshold}%)"

    return "", ""


def check_low_disk_space(
    data: Dict[str, Any],
    warning_free_gb: float = 10.0,
    critical_free_gb: float = 5.0
) -> Tuple[str, str]:
    """
    Returns (level, message) or ("", "") if no alert.
    """
    disk = data.get('storage', {})
    free_bytes = disk.get('free_bytes', 0)
    free_gb = free_bytes / (1024 ** 3)

    if free_gb <= critical_free_gb:
        return "critical", f"CRITICAL: Only {free_gb:.1f} GB free on root filesystem"
    if free_gb <= warning_free_gb:
        return "warning", f"WARNING: Only {free_gb:.1f} GB free on root filesystem"

    return "", ""


def check_uptime(
    data: Dict[str, Any],
    max_days_warning: int = 1,
    max_days_critical: int = 30      # optional – can be adjusted or removed
) -> Tuple[str, str]:
    """
    Alert if system uptime exceeds 1 day (as per spec).
    Returns (level, message) or ("", "") if no alert.
    """
    uptime_seconds = data.get('uptime_seconds', 0.0)
    uptime_days = uptime_seconds / 86400.0

    if uptime_days >= max_days_critical:
        return "critical", f"CRITICAL: System uptime {uptime_days:.1f} days (≥ {max_days_critical} days)"
    if uptime_days >= max_days_warning:
        return "warning", f"WARNING: System uptime {uptime_days:.1f} days (≥ {max_days_warning} day)"

    return "", ""


def get_top_process_alerts(
    data: Dict[str, Any],
    cpu_single_process_critical: float = 90.0
) -> List[str]:
    """
    Returns list of warning strings for suspicious individual processes.
    """
    alerts = []
    for proc in data.get('top_processes', [])[:3]:
        cpu = proc.get('cpu_percent', 0.0)
        if cpu >= cpu_single_process_critical:
            name = proc.get('name', 'unknown')[:30]
            pid = proc.get('pid', '?')
            alerts.append(f"High CPU process: {name} ({cpu:.1f}%) – PID {pid}")
    return alerts


def collect_all_alerts(
    data: Dict[str, Any],
    state: Dict[str, Any] | None = None,
) -> List[Tuple[str, str]]:
    """
    Main entry point for collecting all current alerts.
    state is required for sustained checks (e.g. CPU), optional otherwise.
    """
    if state is None:
        state = {}

    alerts: List[Tuple[str, str]] = []

    # Sustained checks (need state)
    sustained_checks = [
        check_high_cpu_usage,
        # add more sustained checks here later if needed
    ]
    for check_func in sustained_checks:
        level, msg = check_func(data, state)
        if level:
            alerts.append((level, msg))

    # Instant / stateless checks
    instant_checks = [
        check_high_memory_usage,
        check_low_disk_space,
        check_uptime,           # ← newly added
    ]
    for check_func in instant_checks:
        level, msg = check_func(data)
        if level:
            alerts.append((level, msg))

    # Per-process alerts (optional, can be noisy)
    for msg in get_top_process_alerts(data):
        alerts.append(("warning", msg))

    return alerts