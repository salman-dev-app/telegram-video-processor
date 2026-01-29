import asyncio
from typing import List, Dict, Optional, Callable
from database import DatabaseManager
from video_processor import VideoProcessor
from channel_uploader import ChannelUploader
from config import MAX_CONCURRENT_PROCESSES
import logging
import time

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, db_manager: DatabaseManager, processor: VideoProcessor, uploader: ChannelUploader):
        self.db = db_manager
        self.processor = processor
        self.uploader = uploader
        self.active_workers = []
        self.running = False
        self.progress_callbacks = {}  # Store progress callbacks for jobs

    async def start_processing(self):
        """Start the queue processing loop"""
        self.running = True
        logger.info("Queue manager started")
        
        # Start worker tasks
        for i in range(MAX_CONCURRENT_PROCESSES):
            worker_task = asyncio.create_task(self.worker(i))
            self.active_workers.append(worker_task)
        
        logger.info(f"Started {MAX_CONCURRENT_PROCESSES} worker(s)")

    async def stop_processing(self):
        """Stop the queue processing"""
        self.running = False
        # Wait for all workers to finish
        for worker in self.active_workers:
            if not worker.done():
                worker.cancel()
        
        await asyncio.gather(*self.active_workers, return_exceptions=True)
        logger.info("Queue manager stopped")

    async def worker(self, worker_id: int):
        """Worker task that processes jobs from queue"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get pending job                pending_jobs = await self.db.get_pending_jobs()
                if not pending_jobs:
                    await asyncio.sleep(5)  # Wait before checking again
                    continue
                
                # Get first job
                job = pending_jobs[0]
                
                # Update status to processing
                await self.db.update_job_status(job['id'], 'processing', 0.0)
                
                logger.info(f"Worker {worker_id} processing job {job['id']}")
                
                # Process the job
                await self.process_job(job)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)

    async def process_job(self, job: Dict):
        """Process a single job with progress tracking"""
        try:
            # Update progress
            await self.db.update_job_status(job['id'], 'processing', 5.0)
            
            # Download original file
            original_path = f"temp_{job['file_id']}.mp4"
            
            # Simulate download progress
            await self.db.update_job_status(job['id'], 'processing', 10.0)
            
            # Define progress callback to update database
            async def progress_callback(progress: float):
                await self.db.update_job_status(job['id'], 'processing', progress)
                # Also store in memory for real-time updates if needed
                self.progress_callbacks[job['id']] = progress

            # Process video with progress tracking
            await self.db.update_job_status(job['id'], 'processing', 15.0)
            
            # Compress video
            compressed_paths = await self.processor.process_video_with_progress(
                original_path,
                job['target_resolution'],
                lambda p: asyncio.create_task(progress_callback(p))
            )            
            if not compressed_paths:
                raise Exception("No compressed files were created")
            
            # Update progress for upload
            await self.db.update_job_status(job['id'], 'processing', 85.0)
            
            # Upload to channel
            for compressed_path in compressed_paths:
                channel_message = await self.uploader.upload_to_channel(
                    compressed_path,
                    f"Processed: {job['original_filename']} - {job['target_resolution']}"
                )
            
            await self.db.update_job_status(job['id'], 'completed', 100.0)
            
            # Notify user
            await self.notify_user_completion(job['user_id'], channel_message, job)
            
            # Cleanup temp files
            import os
            if os.path.exists(original_path):
                os.remove(original_path)
            for compressed_path in compressed_paths:
                if os.path.exists(compressed_path):
                    os.remove(compressed_path)
            
            # Remove progress callback
            if job['id'] in self.progress_callbacks:
                del self.progress_callbacks[job['id']]
                
            logger.info(f"Job {job['id']} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing job {job['id']}: {e}")
            await self.db.update_job_status(job['id'], 'failed', 0.0, str(e))

    async def notify_user_completion(self, user_id: int, channel_message, job: Dict):
        """Notify user that their video is ready"""
        # This would send a message to the user via Pyrogram
        try:
            logger.info(f"Notified user {user_id} about completion of job {job['id']}")
        except Exception as e:
            logger.error(f"Error notifying user {user_id}: {e}")

    async def add_job(self, user_id: int, file_id: str, filename: str, size: int, resolution: str) -> int:
        """Add a job to the queue"""
        job_id = await self.db.add_to_queue(user_id, file_id, filename, size, resolution)
        logger.info(f"Added job {job_id} for user {user_id}")
        return job_id
    async def get_user_queue_position(self, user_id: int, job_id: int) -> tuple:
        """Get user's position in queue"""
        all_pending = await self.db.get_pending_jobs()
        user_jobs = [job for job in all_pending if job['user_id'] == user_id]
        
        # Find the position of the specific job
        position = None
        for i, job in enumerate(all_pending):
            if job['id'] == job_id:
                position = i + 1
                break
        
        return position, len(all_pending)

    async def get_job_progress(self, job_id: int) -> float:
        """Get progress for a specific job"""
        job = await self.db.get_job_by_id(job_id)
        if job:
            return job['progress']
        return 0.0
