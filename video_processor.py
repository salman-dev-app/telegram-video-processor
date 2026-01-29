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
                preset='medium',
                crf=crf_value,
                movflags='+faststart',
                threads=2            ).overwrite_output()
            
            # Run the compression
            ffmpeg.run(stream, quiet=True, overwrite_output=True)
            
            # Report 100% completion
            if progress_callback:
                progress_callback(100.0)
            
            logger.info(f"Successfully compressed to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
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
                
                success = await self.compress_video_with_progress(
                    input_path, str(output_path),
                    res_params['width'], res_params['height'],
                    res_params['bitrate'],
                    progress_callback
                )
                
                if success:
                    compressed_files.append(str(output_path))
            else:
                # All resolutions
                total_resolutions = len(self.resolutions)
                for i, (res_name, res_params) in enumerate(self.resolutions.items()):
                    output_path = self.temp_dir / f"compressed_{res_name}_{Path(input_path).stem}.mp4"
                    
                    # Calculate progress for this resolution
                    base_progress = (i / total_resolutions) * 100
                    next_progress = ((i + 1) / total_resolutions) * 100
                                        def res_progress_callback(p, base=base_progress, next=next_progress):
                        if progress_callback:
                            calculated = base + (p * (next - base) / 100)
                            progress_callback(calculated)
                    
                    success = await self.compress_video_with_progress(
                        input_path, str(output_path),
                        res_params['width'], res_params['height'],
                        res_params['bitrate'],
                        res_progress_callback
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
