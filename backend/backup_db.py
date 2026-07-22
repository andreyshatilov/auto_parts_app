"""
Скрипт автономного резервного копіювання бази даних (backup_db.py).
Створює точну копію SQLite бази даних у папці backups/ з часовою міткою.
"""

import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "auto_parts.db")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

def perform_db_backup():
    if not os.path.exists(DB_PATH):
        print(f"⚠️ База даних {DB_PATH} ще не створена!")
        return

    os.makedirs(BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUPS_DIR, f"db_backup_{timestamp}.db")

    shutil.copy2(DB_PATH, backup_file)
    print(f"USPESHNO! Backup BD zberezheno u: {backup_file}")


if __name__ == "__main__":
    perform_db_backup()
