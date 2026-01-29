import os
from dotenv import load_dotenv

load_dotenv()

# TELEGRAM API CONFIGURATION
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
SESSION_NAME = os.getenv('SESSION_NAME', 'vps_video_processor')

# CHANNEL CONFIGURATION
UPLOAD_CHANNEL_ID = os.getenv('UPLOAD_CHANNEL_ID')

# USER ACCESS CONFIGURATION
AUTHORIZED_USERS = os.getenv('AUTHORIZED_USERS', '').split(',')
ADMIN_USERS = os.getenv('ADMIN_USERS', '').split(',')
REQUIRE_AUTHENTICATION = os.getenv('REQUIRE_AUTHENTICATION', 'true').lower() == 'true'

# PROCESSING CONFIGURATION
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024))  # 2GB
MAX_DURATION = int(os.getenv('MAX_DURATION', 3600))  # 1 hour
MAX_CONCURRENT_PROCESSES = int(os.getenv('MAX_CONCURRENT_PROCESSES', 2))

# QUEUE CONFIGURATION
QUEUE_LIMIT_PER_USER = int(os.getenv('QUEUE_LIMIT_PER_USER', 5))

# RESOLUTION SETTINGS
RESOLUTIONS = {
    '1080p': {'width': 1920, 'height': 1080, 'bitrate': '8M'},
    '720p': {'width': 1280, 'height': 720, 'bitrate': '5M'},
    '480p': {'width': 854, 'height': 480, 'bitrate': '3M'},
    '360p': {'width': 640, 'height': 360, 'bitrate': '1.5M'}
}

SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp']
TEMP_DIR = os.getenv('TEMP_DIR', './temp')
DATABASE_PATH = os.getenv('DATABASE_PATH', './database.db')
