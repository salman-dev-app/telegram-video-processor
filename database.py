import aiosqlite
import sqlite3
from typing import List, Dict, Optional
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH

    async def initialize(self):
        """Initialize the database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_authorized BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS video_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    file_id TEXT,
                    original_filename TEXT,
                    original_size INTEGER,
                    target_resolution TEXT,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_status ON video_queue(status)
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id ON video_queue(user_id)
            ''')            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_status_created ON video_queue(status, created_at)
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")

    async def add_user(self, user_data: Dict):
        """Add or update user information"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users (id, username, first_name, last_name, is_authorized)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('is_authorized', False)
            ))
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'is_authorized': row[4],
                    'created_at': row[5]
                }
            return None

    async def is_user_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        user = await self.get_user(user_id)
        if not user:
            return False
        return user.get('is_authorized', False)

    async def add_to_queue(self, user_id: int, file_id: str, filename: str, size: int, resolution: str) -> int:
        """Add video processing job to queue"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''                INSERT INTO video_queue (user_id, file_id, original_filename, original_size, target_resolution)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, file_id, filename, size, resolution))
            job_id = cursor.lastrowid
            await db.commit()
            return job_id

    async def get_pending_jobs(self) -> List[Dict]:
        """Get pending jobs ordered by creation time"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM video_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC
            ''')
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'file_id': row[2],
                    'original_filename': row[3],
                    'original_size': row[4],
                    'target_resolution': row[5],
                    'status': row[6],
                    'progress': row[7],
                    'error_message': row[8],
                    'created_at': row[9],
                    'started_at': row[10],
                    'completed_at': row[11]
                }
                for row in rows
            ]

    async def get_user_queue_count(self, user_id: int) -> int:
        """Get number of jobs in queue for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM video_queue 
                WHERE user_id = ? AND status IN ('pending', 'processing')
            ''', (user_id,))
            count = await cursor.fetchone()
            return count[0]

    async def get_job_by_id(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM video_queue WHERE id = ?', (job_id,))
            row = await cursor.fetchone()
            if row:                return {
                    'id': row[0],
                    'user_id': row[1],
                    'file_id': row[2],
                    'original_filename': row[3],
                    'original_size': row[4],
                    'target_resolution': row[5],
                    'status': row[6],
                    'progress': row[7],
                    'error_message': row[8],
                    'created_at': row[9],
                    'started_at': row[10],
                    'completed_at': row[11]
                }
            return None

    async def update_job_status(self, job_id: int, status: str, progress: float = None, error: str = None):
        """Update job status"""
        async with aiosqlite.connect(self.db_path) as db:
            update_fields = []
            params = []
            
            update_fields.append('status = ?')
            params.append(status)
            
            if progress is not None:
                update_fields.append('progress = ?')
                params.append(progress)
            
            if error is not None:
                update_fields.append('error_message = ?')
                params.append(error)
            
            if status == 'processing':
                update_fields.append('started_at = CURRENT_TIMESTAMP')
            elif status in ['completed', 'failed']:
                update_fields.append('completed_at = CURRENT_TIMESTAMP')
            
            query = f"UPDATE video_queue SET {', '.join(update_fields)} WHERE id = ?"
            params.append(job_id)
            
            await db.execute(query, params)
            await db.commit()

    async def get_user_jobs(self, user_id: int) -> List[Dict]:
        """Get all jobs for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM video_queue 
                WHERE user_id = ?                 ORDER BY created_at DESC
                LIMIT 20
            ''', (user_id,))
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'file_id': row[2],
                    'original_filename': row[3],
                    'original_size': row[4],
                    'target_resolution': row[5],
                    'status': row[6],
                    'progress': row[7],
                    'error_message': row[8],
                    'created_at': row[9],
                    'started_at': row[10],
                    'completed_at': row[11]
                }
                for row in rows
            ]

    async def authorize_user(self, user_id: int, authorized: bool = True):
        """Authorize or unauthorize a user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE users SET is_authorized = ? WHERE id = ?', (authorized, user_id))
            await db.commit()
