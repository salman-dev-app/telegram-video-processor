import os
import logging
from pyrogram import Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME, UPLOAD_CHANNEL_ID
from database import DatabaseManager
from auth_manager import AuthManager
from queue_manager import QueueManager
from handlers import MessageHandlers
from utils import check_ffmpeg, ensure_temp_dir
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    # Check prerequisites
    if not await check_ffmpeg():
        logger.error("FFmpeg is not installed or not in PATH. Please install FFmpeg first.")
        return

    # Validate configuration
    if not API_ID or not API_HASH or not BOT_TOKEN or not UPLOAD_CHANNEL_ID:
        logger.error("Missing required environment variables")
        return

    # Ensure temp directory exists
    ensure_temp_dir()

    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.initialize()

    # Initialize client
    app = Client(
        SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Initialize managers
    auth_manager = AuthManager(db_manager)
    processor = VideoProcessor()
    uploader = ChannelUploader(app, UPLOAD_CHANNEL_ID)
    queue_manager = QueueManager(db_manager, processor, uploader)

    # Initialize handlers
    handlers = MessageHandlers(app, db_manager, auth_manager, queue_manager)

    # Register handlers
    app.add_handler(MessageHandler(handlers.start_command, filters.command("start")))
    app.add_handler(MessageHandler(handlers.help_command, filters.command("help")))
    app.add_handler(MessageHandler(handlers.info_command, filters.command("info")))
    app.add_handler(MessageHandler(handlers.queue_command, filters.command("queue")))
    app.add_handler(MessageHandler(handlers.jobs_command, filters.command("jobs")))
    app.add_handler(MessageHandler(handlers.progress_command, filters.command("progress")))
    app.add_handler(MessageHandler(
        handlers.handle_video, 
        filters.video | (filters.document & filters.create(lambda _, __, m: m.document.mime_type.startswith('video')))
    ))
    app.add_handler(CallbackQueryHandler(handlers.process_video_selection))

    logger.info("Bot started successfully on VPS!")
    logger.info(f"Supporting files up to {config.MAX_FILE_SIZE / (1024*1024*1024):.1f} GB")
    
    # Start queue processing
    await queue_manager.start_processing()
    
    try:
        await app.start()
        logger.info("Bot is running on VPS...")
        await app.idle()  # Keep the bot running
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Stop queue processing
        await queue_manager.stop_processing()
        await app.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
