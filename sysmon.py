import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Adjust these imports based on your actual function names
from collector import collect_metrics     # assuming you have this function that returns the data dict
from display import print_dashboard, clear_screen
from alerting import collect_all_alerts

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'sysmon_alerts.log')   # more descriptive name

def setup_logs():
    """Ensure the logs/ directory exists and basic logging is ready."""
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)

    # Optional: touch the file so we know it exists (not strictly needed)
    # Path(LOG_FILE).touch(exist_ok=True)


def write_alert_log(level: str, message: str):
    """
    Append a single formatted entry to the log file.
    Format:  YYYY-MM-DD HH:MM:SS  [LEVEL]  message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp}  [{level.upper()}]  {message}\n"

    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        # Fallback: print to console if log file is not writable
        print(f"ERROR writing to log file: {e}", file=sys.stderr)
        print(entry.strip(), file=sys.stderr)


def main():
    # ────────────────────────────────────────────────
    # Persistent state for sustained alerts
    # ────────────────────────────────────────────────
    alert_state = {
        'cpu_high_since': None,
        # Add more keys here later if you implement other sustained checks
    }

    # ────────────────────────────────────────────────
    # Initialization
    # ────────────────────────────────────────────────
    setup_logs()
    print("Starting SYSMON... (Ctrl+C to stop)")
    time.sleep(1)  # small grace period so user can see message

    try:
        while True:
            # 1. Collect fresh metrics
            data = collect_metrics()   # returns dict with uptime_seconds, cpu_usage, memory_usage, etc.

            # 2. Update the dashboard (clears screen + redraws)
            print_dashboard(data)

            # 3. Check for alerts (pass state for sustained checks)
            alerts = collect_all_alerts(data, state=alert_state)

            # 4. Handle & log alerts
            if alerts:
                print("\n" + "═" * 10 + "  A L E R T S  " + "═" * 10)
                for level, message in alerts:
                    print(f"  {level.upper():8} : {message}")
                    write_alert_log(level, message)
                print("═" * 42)

            # 5. Sleep until next cycle
            # Refresh rate: 3–5 seconds is good balance between responsiveness and low overhead
            time.sleep(4)

    except KeyboardInterrupt:
        clear_screen()
        print("\nSYSMON stopped by user.")
    except Exception as e:
        clear_screen()
        print(f"\nUnexpected error: {e}")
        write_alert_log("ERROR", f"Main loop crashed: {e}")


if __name__ == '__main__':
    main()