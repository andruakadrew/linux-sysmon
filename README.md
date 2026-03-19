# Linux System Monitoring Tool

This project examines the Linux system in real time using tools built in Python.
Critical information like high CPU utilization, exhausted memory, and uptime are
presented and monitored. I built this project to expand my knowledge about the
Linux file system, specifically /proc, and to learn how to retrieve system
information and display it in a readable terminal format using Python.

---

## Features

- Real-time terminal dashboard that refreshes every 4 seconds
- Displays OS info, uptime, CPU usage, memory usage, storage, and top 3 processes
- Alerts for critical system conditions
- Writes all alerts to a log file automatically

---

## Alert Thresholds

| Metric       | Condition                          | Level    |
|--------------|------------------------------------|----------|
| CPU Usage    | Above 90% sustained for 3+ seconds | Critical |
| Storage      | Less than 1 GB free                | Critical |
| Uptime       | Exceeds 1 day                      | Warning  |
| Memory       | Above 95%                          | Critical |
| Memory       | Above 85%                          | Warning  |

---

## Project Structure
```
sysmon/
├── README.md
├── requirements.txt
├── .gitignore
├── sysmon.py        
├── collector.py     
├── display.py       
├── alerting.py      
└── logs/            
```

---

## Requirements

- Linux operating system
- Python 3.10 or higher (developed on Python 3.14 in PyCharm)
- pip packages listed in `requirements.txt`

---

## Installation

### Prerequisites
- Linux based operating system
- Python 3.10 or higher
- Git installed on your system

---

### Step 1 — Clone the repository
```bash
git clone https://github.com/andruakadrew/linux-sysmon.git
cd linux_sysmon
```

---

### Step 2 — Create a virtual environment
```bash
python3 -m venv venv
```

---

### Step 3 — Activate the virtual environment
```bash
source venv/bin/activate
```

---

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

---

### Step 5 — Run the program
```bash
python sysmon.py
```

---

### Step 6 — Stop the program
Press `Ctrl+C` to stop the dashboard at any time.

---

### Checking alert logs
Alert logs are written automatically to the `logs/` folder when any threshold is breached. To view them:
```bash
cat logs/sysmon_alerts.log
```

To search for a specific alert type:
```bash
grep "CRITICAL" logs/sysmon_alerts.log
grep "WARNING" logs/sysmon_alerts.log
```

---

## Usage
```bash
python sysmon.py
```

The dashboard will launch in your terminal and refresh every 4 seconds.
Press `Ctrl+C` to stop.

Alert logs are written to `logs/sysmon_alerts.log` automatically when
any threshold is breached.

---

## Log Format

Each alert entry in the log file follows this format:
```
YYYY-MM-DD HH:MM:SS  [LEVEL]  message
```

Example:
```
2024-03-17 14:32:08  [CRITICAL]  CRITICAL: CPU sustained at 93.2% for 3+ seconds
2024-03-17 14:33:45  [WARNING]   WARNING: System uptime 1.2 days (≥ 1 day)
```

---

## Dependencies

- [psutil](https://pypi.org/project/psutil/) — system and process utilities
- [colorama](https://pypi.org/project/colorama/) — terminal color support

---

*Developed on Python 3.14 / PyCharm / Linux*
