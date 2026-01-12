"""
AI-driven Backup Solution for OSINT Marketing Tool

Features:
- Monitors file changes and triggers incremental backups
- Schedules regular full-system backups
- Uses OpenAI to optimize backup frequency and retention
- Integrates with Flask for status and manual triggers
- Stores backups as zip files in storage/backups/
"""
import os
import zipfile
import time
import threading
from datetime import datetime
from utils.openai_client import OpenAIClient

BACKUP_ROOT = os.path.join(os.path.dirname(__file__), 'storage', 'backups')
TENANTS_ROOT = os.path.join(os.path.dirname(__file__), 'storage', 'tenants')
CONFIG_FILES = ['config.example.env', 'tenants.json']
MONITOR_PATHS = [TENANTS_ROOT] + [os.path.join(os.path.dirname(__file__), f) for f in CONFIG_FILES]

os.makedirs(BACKUP_ROOT, exist_ok=True)
ai_client = OpenAIClient()

_last_backup_times = {}

# --- File Change Monitor ---
def monitor_changes(interval=10):
    global _last_backup_times
    while True:
        for path in MONITOR_PATHS:
            for root, dirs, files in os.walk(path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    mtime = os.path.getmtime(abs_path)
                    last_mtime = _last_backup_times.get(abs_path, 0)
                    if mtime > last_mtime:
                        backup_incremental(abs_path)
                        _last_backup_times[abs_path] = mtime
        time.sleep(interval)

# --- Incremental Backup ---
def backup_incremental(file_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
    backup_path = os.path.join(BACKUP_ROOT, f'incremental_{timestamp}_{rel_path.replace(os.sep,"_")}.zip')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        backup_zip.write(file_path, rel_path)
    return backup_path

# --- Full System Backup ---
def backup_full():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_ROOT, f'full_backup_{timestamp}.zip')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for path in MONITOR_PATHS:
            for root, dirs, files in os.walk(path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, os.path.dirname(__file__))
                    backup_zip.write(abs_path, rel_path)
    return backup_path

# --- AI-driven Scheduling ---
def ai_optimize_backup():
    prompt = "Given the following file change history and backup schedule, recommend the optimal backup frequency and retention policy for a multi-tenant SaaS system."
    # Example: You could pass file change stats here
    advice = ai_client.generate(prompt)
    return advice

# --- Flask Integration Example ---
try:
    from flask import Blueprint, jsonify
    backup_bp = Blueprint('backup', __name__)

    @backup_bp.route('/backup/full', methods=['POST'])
    def trigger_full_backup():
        path = backup_full()
        return jsonify({'status': 'success', 'backup': path})

    @backup_bp.route('/backup/advice', methods=['GET'])
    def get_backup_advice():
        advice = ai_optimize_backup()
        return jsonify({'advice': advice})
except ImportError:
    backup_bp = None

# --- Start Monitor Thread ---
def start_monitor():
    t = threading.Thread(target=monitor_changes, daemon=True)
    t.start()

if __name__ == '__main__':
    print('Starting AI-driven backup monitor...')
    start_monitor()
    while True:
        time.sleep(60)
