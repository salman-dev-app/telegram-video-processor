import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from video_processor import VideoProcessor
from channel_uploader import ChannelUploader
from utils import get_video_info, format_bytes, format_duration, format_queue_position, ensure_temp_dir
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, UPLOAD_CHANNEL_ID, REQUIRE_AUTHENTICATION
from database import DatabaseManager
from auth_manager import AuthManager
from queue_manager import QueueManager
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, app: Client, db_manager: DatabaseManager, auth_manager: AuthManager, queue_manager: QueueManager):
        self.app = app
        self.db = db_manager
        self.auth = auth_manager
        self.queue = queue_manager
        self.processor = VideoProcessor()
        self.uploader = ChannelUploader(app, UPLOAD_CHANNEL_ID)
        self.active_progress_messages = {}  # Track progress messages

    async def start_command(self, client: Client, message: Message):
        """Handle /start command"""
        # Register user
        user_data = {
            'id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await self.db.add_user(user_data)

        # Check authorization
        auth_status = await self.auth.get_authorization_status(message.from_user.id)
        
        welcome_text = f"""
🎬 **Advanced Video Queue Processor Bot**

🤖 **Features:**
• Queue-based processing (no waiting in line)
• Multi-resolution compression (1080p, 720p, 480p, 360p)
• Large video support (up to 2GB)
• Memory-efficient processing
• Channel-based storage
• Automatic delivery when complete• **Real-time progress updates: Processed 0% → 100%**

{auth_status['message']}

📝 **How it works:**
1. Send any video file to the bot
2. Job gets added to queue
3. Bot processes with live progress updates
4. Bot automatically sends processed video when done

💡 **Commands:**
• /start - Show this message
• /help - Get help
• /info - Get video information
• /queue - Check your position in queue
• /jobs - View your recent jobs
• /progress - Check progress of your current jobs

🔧 **Supported Formats:** MP4, AVI, MOV, MKV, WMV, FLV, WEBM
        """
        await message.reply_text(welcome_text, disable_web_page_preview=True)

    async def progress_command(self, client: Client, message: Message):
        """Handle /progress command - show progress of current jobs"""
        user_jobs = await self.db.get_user_jobs(message.from_user.id)
        
        active_jobs = [job for job in user_jobs if job['status'] in ['processing', 'pending'] and job['progress'] < 100]
        
        if not active_jobs:
            await message.reply_text("📊 No active jobs in progress. Send a video to start processing!")
            return
        
        response = "📊 Your active jobs:\n\n"
        for job in active_jobs:
            progress_bar = "█" * int(job['progress']/5) + "░" * (20 - int(job['progress']/5))
            response += f"Job #{job['id']}: {job['target_resolution']}\n"
            response += f"Status: {job['status']}\n"
            response += f"Progress: [{progress_bar}] {job['progress']:.1f}%\n"
            response += f"Created: {job['created_at']}\n\n"
        
        await message.reply_text(response)

    async def help_command(self, client: Client, message: Message):
        """Handle /help command"""
        help_text = """
📚 **Help - Video Queue Processor Bot**

**How It Works:**
1. Upload video to bot
2. Job enters processing queue3. Bot processes with live progress (0% → 100%)
4. Bot automatically delivers processed video
5. No need to wait around!

**Progress Tracking:**
• Real-time percentage updates
• Visual progress bars
• Live status updates
• Progress command to check current jobs

**Queue System:**
• Jobs processed in order received
• Limited concurrent processing
• Automatic notifications when complete

**Supported Formats:** MP4, AVI, MOV, MKV, WMV, FLV, WEBM

**Compression Options:**
• 1080p: Full HD, highest quality
• 720p: HD, good balance
• 480p: SD, smaller file
• 360p: Low quality, smallest file

**Commands:**
• /progress - Check current job progress
• /queue - Check your position in processing queue
• /jobs - View your recent processing jobs

**Limitations:**
• Max file size: 2GB
• Max duration: 1 hour
• Queue limit: 5 jobs per user
        """
        await message.reply_text(help_text)

    async def queue_command(self, client: Client, message: Message):
        """Handle /queue command - show user's position in queue"""
        pending_jobs = await self.db.get_pending_jobs()
        user_jobs = [job for job in pending_jobs if job['user_id'] == message.from_user.id]
        
        if not user_jobs:
            await message.reply_text("📋 Your queue is empty. Send a video to start processing!")
            return
        
        response = "📋 Your jobs in queue:\n\n"
        for job in user_jobs:
            # Find position
            position = None
            for i, pending_job in enumerate(pending_jobs):
                if pending_job['id'] == job['id']:                    position = i + 1
                    break
            
            progress_bar = "█" * int(job['progress']/5) + "░" * (20 - int(job['progress']/5))
            response += f"Job #{job['id']}: {job['target_resolution']}\n"
            response += f"Status: {job['status']}\n"
            response += f"Progress: [{progress_bar}] {job['progress']:.1f}%\n"
            response += f"Position: {position}/{len(pending_jobs)}\n\n"
        
        await message.reply_text(response)

    async def jobs_command(self, client: Client, message: Message):
        """Handle /jobs command - show user's recent jobs"""
        user_jobs = await self.db.get_user_jobs(message.from_user.id)
        
        if not user_jobs:
            await message.reply_text("📋 You have no processing jobs yet. Send a video to start!")
            return
        
        response = "📋 Your recent jobs:\n\n"
        for job in user_jobs[:10]:  # Show last 10 jobs
            progress_bar = "█" * int(job['progress']/5) + "░" * (20 - int(job['progress']/5))
            response += f"Job #{job['id']}: {job['target_resolution']}\n"
            response += f"Status: {job['status']}\n"
            response += f"Progress: [{progress_bar}] {job['progress']:.1f}%\n"
            response += f"Created: {job['created_at']}\n"
            if job['completed_at']:
                response += f"Completed: {job['completed_at']}\n"
            response += "\n"
        
        await message.reply_text(response)

    async def handle_video(self, client: Client, message: Message):
        """Handle incoming video messages"""
        # Check authorization
        if REQUIRE_AUTHENTICATION:
            auth_status = await self.auth.get_authorization_status(message.from_user.id)
            if not auth_status['authorized']:
                await message.reply_text(auth_status['message'])
                return

        if not (message.video or message.document):
            return

        # Register user if not already registered
        user_data = {
            'id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name        }
        await self.db.add_user(user_data)

        # Determine if it's a video or document
        if message.video:
            file_id = message.video.file_id
            file_size = message.video.file_size
            mime_type = message.video.mime_type
            original_filename = f"video_{file_id}.mp4"
        elif message.document and message.document.mime_type.startswith('video'):
            file_id = message.document.file_id
            file_size = message.document.file_size
            mime_type = message.document.mime_type
            original_filename = message.document.file_name or f"video_{file_id}.mp4"
        else:
            return

        # Validate file size
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(f"❌ File too large! Maximum size: {format_bytes(MAX_FILE_SIZE)}")
            return

        # Validate file format
        ext = mime_type.split('/')[-1] if '/' in mime_type else 'unknown'
        if ext not in SUPPORTED_FORMATS:
            await message.reply_text(f"❌ Unsupported format: {ext}\nSupported: {', '.join(SUPPORTED_FORMATS)}")
            return

        # Check queue limit per user
        user_queue_count = await self.db.get_user_queue_count(message.from_user.id)
        if user_queue_count >= config.QUEUE_LIMIT_PER_USER:
            await message.reply_text(f"❌ Queue limit reached! You can have max {config.QUEUE_LIMIT_PER_USER} jobs in queue.")
            return

        # Show options for resolution
        keyboard = [
            [
                InlineKeyboardButton("1080p", callback_data="queue_1080p"),
                InlineKeyboardButton("720p", callback_data="queue_720p")
            ],
            [
                InlineKeyboardButton("480p", callback_data="queue_480p"),
                InlineKeyboardButton("360p", callback_data="queue_360p")
            ],
            [
                InlineKeyboardButton("All Resolutions", callback_data="queue_all")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
                await message.reply_text(
            f"🎯 Choose compression resolution for your video:\n\n"
            f"📁 File: {original_filename}\n"
            f"📦 Size: {format_bytes(file_size)}\n\n"
            f"Select an option below:",
            reply_markup=reply_markup
        )

    async def process_video_selection(self, client: Client, callback_query):
        """Handle compression selection and add to queue"""
        data = callback_query.data
        message = callback_query.message
        original_message = callback_query.message.reply_to_message
        
        if not original_message or not (original_message.video or original_message.document):
            await callback_query.answer("❌ No video found!", show_alert=True)
            return

        # Get file info
        if original_message.video:
            file_id = original_message.video.file_id
            file_size = original_message.video.file_size
            mime_type = original_message.video.mime_type
            original_filename = f"video_{file_id}.mp4"
        else:
            file_id = original_message.document.file_id
            file_size = original_message.document.file_size
            mime_type = original_message.document.mime_type
            original_filename = original_message.document.file_name or f"video_{file_id}.mp4"

        # Validate file format
        ext = mime_type.split('/')[-1] if '/' in mime_type else 'mp4'
        if ext not in SUPPORTED_FORMATS:
            await callback_query.answer(f"❌ Unsupported format: {ext}", show_alert=True)
            return

        # Determine target resolution
        if data == "queue_all":
            target_resolution = "all"
        else:
            target_resolution = data.replace("queue_", "")

        try:
            if target_resolution == "all":
                # Add separate jobs for each resolution
                job_ids = []
                for res_name in config.RESOLUTIONS.keys():
                    job_id = await self.queue.add_job(
                        original_message.from_user.id,
                        file_id,                        original_filename,
                        file_size,
                        res_name
                    )
                    job_ids.append(job_id)
                
                await callback_query.answer(f"✅ Added {len(job_ids)} jobs to queue!", show_alert=True)
                
                # Send confirmation message
                await original_message.reply_text(
                    f"✅ Added {len(job_ids)} jobs to queue!\n"
                    f"Each resolution will be processed separately.\n"
                    f"Use /progress to check status."
                )
            else:
                # Add single job
                job_id = await self.queue.add_job(
                    original_message.from_user.id,
                    file_id,
                    original_filename,
                    file_size,
                    target_resolution
                )
                
                # Get position in queue
                position, total = await self.queue.get_user_queue_position(original_message.from_user.id, job_id)
                
                # Send progress message
                progress_msg = await original_message.reply_text(
                    f"✅ Added to queue! Position: {position}/{total}\n"
                    f"🎯 Starting processing: 0% complete\n"
                    f"📊 Progress: [░░░░░░░░░░░░░░░░░░░░] 0.0%\n"
                    f"You'll receive the processed video automatically when ready."
                )
                
                # Store progress message ID for updates
                self.active_progress_messages[job_id] = progress_msg.id
                
                # Update progress periodically
                await self.monitor_progress(job_id, original_message.from_user.id, progress_msg.id)
                
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            await callback_query.answer(f"❌ Error adding to queue: {str(e)}", show_alert=True)

    async def monitor_progress(self, job_id: int, user_id: int, progress_msg_id: int):
        """Monitor and update progress message"""
        try:
            while True:
                job = await self.db.get_job_by_id(job_id)                if not job:
                    break
                
                if job['status'] == 'completed':
                    # Update final progress message
                    await self.app.edit_message_text(
                        chat_id=user_id,
                        message_id=progress_msg_id,
                        text=(
                            f"✅ Processing completed!\n"
                            f"🎯 Status: 100% complete\n"
                            f"📊 Progress: [████████████████████] 100.0%\n"
                            f"Your video will be delivered shortly."
                        )
                    )
                    break
                elif job['status'] == 'failed':
                    await self.app.edit_message_text(
                        chat_id=user_id,
                        message_id=progress_msg_id,
                        text=(
                            f"❌ Processing failed!\n"
                            f"Error: {job['error_message']}\n"
                            f"Please try again."
                        )
                    )
                    break
                else:
                    # Update progress bar
                    progress = job['progress']
                    progress_bar = "█" * int(progress/5) + "░" * (20 - int(progress/5))
                    
                    await self.app.edit_message_text(
                        chat_id=user_id,
                        message_id=progress_msg_id,
                        text=(
                            f"🎯 Processing: {progress:.1f}% complete\n"
                            f"📊 Progress: [{progress_bar}] {progress:.1f}%\n"
                            f"Status: {job['status']}\n"
                            f"Resolution: {job['target_resolution']}"
                        )
                    )
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except Exception as e:
            logger.error(f"Error monitoring progress: {e}")

    async def info_command(self, client: Client, message: Message):
        """Handle /info command - get video info without processing"""        if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
            await message.reply_text("❌ Reply to a video message to get its information.")
            return

        video_msg = message.reply_to_message
        if video_msg.video:
            file_id = video_msg.video.file_id
            file_size = video_msg.video.file_size
            mime_type = video_msg.video.mime_type
        elif video_msg.document:
            file_id = video_msg.document.file_id
            file_size = video_msg.document.file_size
            mime_type = video_msg.document.mime_type
        else:
            await message.reply_text("❌ This doesn't appear to be a video file.")
            return

        # Validate file type
        ext = mime_type.split('/')[-1] if '/' in mime_type else 'unknown'
        if ext not in SUPPORTED_FORMATS:
            await message.reply_text(f"❌ Unsupported format: {ext}\nSupported: {', '.join(SUPPORTED_FORMATS)}")
            return

        # Download file temporarily
        temp_path = self.processor.temp_dir / f"temp_info_{file_id}.{ext}"
        try:
            await message.reply_text("🔍 Analyzing video...")
            await video_msg.download(str(temp_path))
            
            # Get video info
            info = get_video_info(str(temp_path))
            
            info_text = f"""
📊 **Video Information**

📁 File Size: {format_bytes(file_size)}
⏱️ Duration: {format_duration(info.get('duration', 0))}
📏 Resolution: {info.get('width', 'Unknown')} x {info.get('height', 'Unknown')}
🎞️ Codec: {info.get('codec', 'Unknown')}
📊 Bit Rate: {info.get('bit_rate', 'Unknown')}
            """
            await message.reply_text(info_text)
            
        except Exception as e:
            await message.reply_text(f"❌ Error analyzing video: {str(e)}")
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
