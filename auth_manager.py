from typing import Dict, Optional
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def is_user_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        if not config.REQUIRE_AUTHENTICATION:
            return True
        return await self.db.is_user_authorized(user_id)

    async def register_user(self, user_data: Dict) -> bool:
        """Register user and check authorization"""
        # Add user to database
        await self.db.add_user(user_data)
        
        # Check if user is in authorized list
        if str(user_data['id']) in config.AUTHORIZED_USERS:
            await self.db.authorize_user(user_data['id'], True)
            return True
        
        return config.REQUIRE_AUTHENTICATION

    async def get_authorization_status(self, user_id: int) -> Dict:
        """Get user authorization status"""
        user = await self.db.get_user(user_id)
        if not user:
            return {
                'authorized': False,
                'message': 'User not registered'
            }
        
        is_auth = user.get('is_authorized', False)
        if not is_auth and config.REQUIRE_AUTHENTICATION:
            return {
                'authorized': False,
                'message': 'Access denied. Contact admin for authorization.'
            }
        
        return {
            'authorized': True,
            'message': 'Access granted'
        }

    async def add_authorized_user(self, admin_user_id: int, target_user_id: int) -> bool:
        """Admin function to add authorized user"""
        # Check if admin
        if str(admin_user_id) not in config.ADMIN_USERS:
            return False
        
        await self.db.authorize_user(target_user_id, True)
        return True

    async def remove_authorized_user(self, admin_user_id: int, target_user_id: int) -> bool:
        """Admin function to remove authorized user"""
        # Check if admin
        if str(admin_user_id) not in config.ADMIN_USERS:
            return False
        
        await self.db.authorize_user(target_user_id, False)
        return True
