import os
import logging
from pyrogram import Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME
from database import DatabaseManager
from auth_manager import AuthManager
from queue_manager import QueueManager
from handlers import MessageHandlers
from utils import check_ffmpeg, ensure_temp_dir
import asyncio

# Check if running on Railway
IS_RAILWAY = 'RAILWAY' in os.environ

async def main():
    # Check prerequisites
    if not await check_ffmpeg():
        print("FFmpeg is not available. Installing...")
        # On Railway, FFmpeg should be available if Dockerfile is used
        return

    # Validate configuration
    if not API_ID or not API_HASH or not BOT_TOKEN or not config.UPLOAD_CHANNEL_ID:
        print("Missing required environment variables")
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
    uploader = ChannelUploader(app, config.UPLOAD_CHANNEL_ID)
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

    print("Bot started successfully!")
    
    # Start queue processing
    await queue_manager.start_processing()
    
    try:
        await app.start()
        print("Bot is running on Railway...")
        await app.idle()  # Keep the bot running
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Stop queue processing
        await queue_manager.stop_processing()
        await app.stop()
        print("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
