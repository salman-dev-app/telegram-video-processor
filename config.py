import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
SESSION_NAME = os.getenv('SESSION_NAME', 'video_processor')

# Channel Configuration
UPLOAD_CHANNEL_ID = os.getenv('UPLOAD_CHANNEL_ID')  # Private channel for storing processed videos

# User Access Configuration
AUTHORIZED_USERS = os.getenv('AUTHORIZED_USERS', '').split(',')  # Comma-separated user IDs
ADMIN_USERS = os.getenv('ADMIN_USERS', '').split(',')  # Admin user IDs
REQUIRE_AUTHENTICATION = os.getenv('REQUIRE_AUTHENTICATION', 'true').lower() == 'true'

# Processing Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024))  # 2GB
MAX_DURATION = int(os.getenv('MAX_DURATION', 3600))  # 1 hour in seconds
MAX_CONCURRENT_PROCESSES = int(os.getenv('MAX_CONCURRENT_PROCESSES', 2))  # Max parallel processing

# Queue Configuration
QUEUE_LIMIT_PER_USER = int(os.getenv('QUEUE_LIMIT_PER_USER', 5))  # Max items per user in queue

# Resolution Settings
RESOLUTIONS = {
    '1080p': {'width': 1920, 'height': 1080, 'bitrate': '8M'},
    '720p': {'width': 1280, 'height': 720, 'bitrate': '5M'},
    '480p': {'width': 854, 'height': 480, 'bitrate': '3M'},
    '360p': {'width': 640, 'height': 360, 'bitrate': '1.5M'}
}

# Supported formats
SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp']

# Processing settings
TEMP_DIR = os.getenv('TEMP_DIR', './temp')
DATABASE_PATH = os.getenv('DATABASE_PATH', './database.db')
