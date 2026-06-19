import motor.motor_asyncio
import os

class Database:
    def __init__(self, uri):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client.telegram_bot

    async def add_user(self, user_id, username):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username}},
            upsert=True
        )

    async def get_all_users(self):
        return await self.db.users.find().to_list(length=None)

    async def get_user_lang(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id})
        return user.get("language", "English") if user else "English"

    async def set_user_lang(self, user_id, language):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"language": language}},
            upsert=True
        )

    async def save_cookies(self, service, content):
        """Save cookies for a specific service (e.g., 'instagram', 'youtube')"""
        await self.db.settings.update_one(
            {"key": f"cookies_{service}"},
            {"$set": {"content": content}},
            upsert=True
        )

    async def get_cookies(self, service):
        """Retrieve cookies for a specific service"""
        doc = await self.db.settings.find_one({"key": f"cookies_{service}"})
        return doc.get("content") if doc else None

    async def ban_user(self, user_id):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"banned": True}})

    async def is_banned(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id})
        return user.get("banned", False) if user else False
