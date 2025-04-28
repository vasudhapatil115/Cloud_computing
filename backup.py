import shutil
import os

CLOUD_FOLDER = 'cloud_storage'
os.makedirs(CLOUD_FOLDER, exist_ok=True)

def backup_file(filepath):
    filename = os.path.basename(filepath)
    shutil.copy(filepath, os.path.join(CLOUD_FOLDER, filename))
