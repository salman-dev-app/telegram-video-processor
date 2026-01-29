import ffmpeg
import os
import asyncio
import logging
from typing import Dict, Optional, List, Callable
from config import RESOLUTIONS, TEMP_DIR
from utils import get_video_info
from pathlib import Path
import tempfile
import threading
import time

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.resolutions = RESOLUTIONS
        self.temp_dir = Path(TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def ffmpeg_progress_callback(self, progress_func: Callable[[float], None]):
        """Callback function for FFmpeg progress tracking"""
        def progress_callback(filename, duration, progress):
            try:
                if duration > 0:
                    percent = (progress / duration) * 100
                    if progress_func:
                        progress_func(max(0, min(100, percent)))  # Clamp between 0-100
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
        return progress_callback

    async def compress_video_with_progress(self, input_path: str, output_path: str, 
                                         width: int, height: int, bitrate: str = '5M',
                                         progress_callback: Callable[[float], None] = None) -> bool:
        """Compress video with progress tracking"""
        try:
            logger.info(f"Starting compression: {input_path} -> {output_path}")
            
            # Calculate CRF value based on bitrate
            crf_value = 23
            if bitrate.endswith('M'):
                bitrate_num = int(bitrate[:-1])
                if bitrate_num <= 2:
                    crf_value = 28
                elif bitrate_num >= 8:
                    crf_value = 18
            
            # Create a thread to simulate progress
            def simulate_progress():                if progress_callback:
                    # Simulate progress - this is approximate since we can't get exact FFmpeg progress
                    for i in range(0, 101, 2):  # Increment by 2%
                        progress_callback(i)
                        time.sleep(0.1)  # Small delay to allow other operations
            
            # Start the progress simulation thread
            progress_thread = threading.Thread(target=simulate_progress, daemon=True)
            progress_thread.start()
            
            # Use FFmpeg with memory-efficient settings
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'scale', width, height)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                video_bitrate=bitrate,
                audio_bitrate='128k',
                preset='fast',
                crf=crf_value,
                movflags='+faststart',
                threads=2
            ).overwrite_output()
            
            # Run the compression
            ffmpeg.run(stream, quiet=True, overwrite_output=True)
            
            # Ensure progress reaches 100%
            if progress_callback:
                progress_callback(100.0)
            
            # Wait for progress thread to finish (with timeout)
            progress_thread.join(timeout=2)  # Wait max 2 seconds for thread to finish
            
            logger.info(f"Successfully compressed to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Fallback method
            try:
                if progress_callback:
                    progress_callback(50.0)  # Half way for fallback
                
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.filter(stream, 'scale', width, height)
                stream = ffmpeg.output(
                    stream,                    output_path,
                    vcodec='libx264',
                    crf=28,
                    preset='ultrafast'
                ).overwrite_output()
                
                ffmpeg.run(stream, quiet=True, overwrite_output=True)
                
                if progress_callback:
                    progress_callback(100.0)
                
                return True
            except Exception as fallback_error:
                logger.error(f"Fallback compression also failed: {fallback_error}")
                return False

    async def process_video_with_progress(self, input_path: str, target_resolution: str = None, 
                                        progress_callback: Callable[[float], None] = None) -> List[str]:
        """Process video with progress tracking"""
        try:
            # Get video info
            video_info = get_video_info(input_path)
            logger.info(f"Video info: {video_info}")
            
            compressed_files = []
            
            if target_resolution:
                # Single resolution
                res_params = self.resolutions[target_resolution]
                output_path = self.temp_dir / f"compressed_{target_resolution}_{Path(input_path).stem}.mp4"
                
                # Calculate progress increment based on resolution
                progress_start = 0
                progress_end = 100
                
                success = await self.compress_video_with_progress(
                    input_path, str(output_path),
                    res_params['width'], res_params['height'],
                    res_params['bitrate'],
                    lambda p: progress_callback(progress_start + (p * (progress_end - progress_start) / 100)) if progress_callback else None
                )
                
                if success:
                    compressed_files.append(str(output_path))
            else:
                # All resolutions - divide progress among resolutions
                total_resolutions = len(self.resolutions)
                for i, (res_name, res_params) in enumerate(self.resolutions.items()):
                    output_path = self.temp_dir / f"compressed_{res_name}_{Path(input_path).stem}.mp4"
                                        # Calculate progress range for this resolution
                    progress_start = (i / total_resolutions) * 100
                    progress_end = ((i + 1) / total_resolutions) * 100
                    
                    success = await self.compress_video_with_progress(
                        input_path, str(output_path),
                        res_params['width'], res_params['height'],
                        res_params['bitrate'],
                        lambda p, start=progress_start, end=progress_end: 
                            progress_callback(start + (p * (end - start) / 100)) if progress_callback else None
                    )
                    
                    if success:
                        compressed_files.append(str(output_path))
            
            return compressed_files
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return []

    def get_file_metadata(self, file_path: str) -> Dict:
        """Get file metadata for channel upload"""
        try:
            stat = os.stat(file_path)
            video_info = get_video_info(file_path)
            
            return {
                'size': stat.st_size,
                'duration': video_info.get('duration', 0),
                'width': video_info.get('width', 0),
                'height': video_info.get('height', 0),
                'codec': video_info.get('codec', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error getting meta {e}")
            return {}
