import subprocess
import json
import os
import asyncio
from typing import Dict, Optional
import logging
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

def get_video_info(file_path: str) -> Dict:
    """Get video information using ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path
        ], capture_output=True, text=True, check=True)
        
        info = json.loads(result.stdout)
        video_stream = next((stream for stream in info['streams'] if stream['codec_type'] == 'video'), None)
        
        return {
            'duration': float(info['format'].get('duration', 0)),
            'size': int(info['format'].get('size', 0)),
            'width': int(video_stream['width']) if video_stream else 0,
            'height': int(video_stream['height']) if video_stream else 0,
            'codec': video_stream.get('codec_name', 'unknown'),
            'bit_rate': info['format'].get('bit_rate', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {}

def format_bytes(bytes_value: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

def format_duration(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

async def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def ensure_temp_dir():
    """Ensure temp directory exists"""
    Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)

async def clean_temp_files():
    """Clean up temporary files"""
    temp_path = Path(config.TEMP_DIR)
    for file_path in temp_path.glob('*'):
        try:
            file_path.unlink()
        except Exception as e:
            logger.error(f"Error deleting temp file {file_path}: {e}")

def format_queue_position(position: int, total: int) -> str:
    """Format queue position display"""
    return f"Position: {position}/{total} in queue"
