import time
import os
import sys
import psutil
from pathlib import Path
from datetime import datetime

from collector import collect_metrics    
from display import print_dashboard, clear_screen
from alerting import collect_all_alerts

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'sysmon_alerts.log')  

def setup_logs():
    # Ensure the logs/ directory exists and basic logging is ready.
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)



def write_alert_log(level: str, message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp}  [{level.upper()}]  {message}\n"

    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        print(f"ERROR writing to log file: {e}", file=sys.stderr)
        print(entry.strip(), file=sys.stderr)


def main():
    alert_state = {
        'cpu_high_since': None,
    }

    # Initialization
    setup_logs()
    print("Starting SYSMON... (Ctrl+C to stop)")
    # Prime psutil cpu measurements so first reading is accurate
    psutil.cpu_percent(interval=None)
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    time.sleep(1)  # single one second wait, only happens once

    try:
        while True:
            # 1. Collect fresh metrics
            data = collect_metrics()  

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
