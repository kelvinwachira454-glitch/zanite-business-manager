import os
import glob
import sqlite3
from datetime import datetime


def backup_database(db_path, backup_dir, retention=14):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest_path = os.path.join(backup_dir, f"business_{timestamp}.db")

    source_conn = sqlite3.connect(db_path)
    dest_conn = sqlite3.connect(dest_path)
    with dest_conn:
        source_conn.backup(dest_conn)
    source_conn.close()
    dest_conn.close()

    _prune_old_backups(backup_dir, retention)
    return dest_path


def _prune_old_backups(backup_dir, retention):
    backups = sorted(glob.glob(os.path.join(backup_dir, "business_*.db")))
    excess = len(backups) - retention
    for old_file in backups[:max(0, excess)]:
        os.remove(old_file)