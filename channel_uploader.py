import os
import asyncio
from pyrogram import Client
from pyrogram.types import Message
from typing import List, Tuple
import logging
from pathlib import Path
from utils import format_bytes

logger = logging.getLogger(__name__)

class ChannelUploader:
    def __init__(self, app: Client, upload_channel_id: str):
        self.app = app
        self.upload_channel_id = upload_channel_id

    async def upload_to_channel(self, file_path: str, caption: str = "", progress_callback=None) -> Message:
        """Upload file to channel with progress tracking"""
        try:
            logger.info(f"Uploading to channel: {file_path}")
            
            # Upload to channel
            message = await self.app.send_video(
                chat_id=self.upload_channel_id,
                video=file_path,
                caption=caption,
                supports_streaming=True,
                progress=progress_callback
            )
            
            logger.info(f"Uploaded successfully to channel. Message ID: {message.id}")
            return message
            
        except Exception as e:
            logger.error(f"Upload to channel failed: {e}")
            raise

    async def upload_multiple_to_channel(self, file_paths: List[str], base_caption: str = "") -> List[Message]:
        """Upload multiple files to channel"""
        messages = []
        
        for i, file_path in enumerate(file_paths):
            try:
                caption = f"{base_caption}\n\nPart {i+1}/{len(file_paths)}"
                message = await self.upload_to_channel(file_path, caption)
                messages.append(message)
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
                continue
        
        return messages

    async def get_file_from_channel(self, message_id: int) -> Message:
        """Retrieve a file from channel by message ID"""
        try:
            message = await self.app.get_messages(chat_id=self.upload_channel_id, message_ids=message_id)
            return message
        except Exception as e:
            logger.error(f"Failed to retrieve message {message_id}: {e}")
            return None

    async def send_from_channel_to_user(self, message: Message, user_chat_id: int, additional_caption: str = ""):
        """Forward a message from channel to user"""
        try:
            if message.video:
                await self.app.send_video(
                    chat_id=user_chat_id,
                    video=message.video.file_id,
                    caption=f"{additional_caption}\n\nFrom channel: {message.caption or ''}" if additional_caption else message.caption
                )
            elif message.document:
                await self.app.send_document(
                    chat_id=user_chat_id,
                    document=message.document.file_id,
                    caption=f"{additional_caption}\n\nFrom channel: {message.caption or ''}" if additional_caption else message.caption
                )
        except Exception as e:
            logger.error(f"Failed to send from channel to user: {e}")
            raise
