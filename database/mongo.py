import motor.motor_asyncio
import os

class Database:
    def __init__(self, uri):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client.telegram_bot

    async def add_user(self, user_id, username):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "last_active": os.times()}},
            upsert=True
        )

    async def get_all_users(self):
        return await self.db.users.find().to_list(length=None)

    async def ban_user(self, user_id):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"banned": True}})

    async def is_banned(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id})
        return user.get("banned", False) if user else False
