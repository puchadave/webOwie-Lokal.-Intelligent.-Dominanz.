"""
Backup Solution for OSINT Marketing Tool

Features:
- Backup tenant data from storage/tenants/
- Optionally backup config files (e.g., .env, tenants.json)
- Manual backup trigger via CLI or Flask route
- Stores backups as zip files in storage/backups/
"""
import os
import zipfile
from datetime import datetime

BACKUP_ROOT = os.path.join(os.path.dirname(__file__), 'storage', 'backups')
TENANTS_ROOT = os.path.join(os.path.dirname(__file__), 'storage', 'tenants')
CONFIG_FILES = ['config.example.env', 'tenants.json']

os.makedirs(BACKUP_ROOT, exist_ok=True)

def backup_tenants():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_ROOT, f'tenants_backup_{timestamp}.zip')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for root, dirs, files in os.walk(TENANTS_ROOT):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, TENANTS_ROOT)
                backup_zip.write(abs_path, os.path.join('tenants', rel_path))
    return backup_path

def backup_config():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_ROOT, f'config_backup_{timestamp}.zip')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for config_file in CONFIG_FILES:
            abs_path = os.path.join(os.path.dirname(__file__), config_file)
            if os.path.exists(abs_path):
                backup_zip.write(abs_path, config_file)
    return backup_path

def backup_all():
    tenants_zip = backup_tenants()
    config_zip = backup_config()
    return {'tenants': tenants_zip, 'config': config_zip}

if __name__ == '__main__':
    print('Starting backup...')
    result = backup_all()
    print('Backup completed:')
    print(result)
