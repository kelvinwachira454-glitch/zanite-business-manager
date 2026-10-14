from config import Config
from utils.backup import backup_database

if __name__ == "__main__":
    path = backup_database(Config.BACKUP_SOURCE_PATH, Config.BACKUP_DIR, Config.BACKUP_RETENTION_COUNT)
    print(f"Backup created: {path}")