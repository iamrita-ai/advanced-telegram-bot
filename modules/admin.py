from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class AdminPanel:
    def __init__(self, db, owner_id):
        self.db = db
        self.owner_id = int(owner_id)

    async def show_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.owner_id:
            return await update.message.reply_text("Unauthorized.")

        keyboard = [
            [InlineKeyboardButton("Users Stats", callback_data="stats"),
             InlineKeyboardButton("Broadcast", callback_data="broadcast")],
            [InlineKeyboardButton("Ban User", callback_data="ban"),
             InlineKeyboardButton("Logs", callback_data="logs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Admin Panel:", reply_markup=reply_markup)

    async def broadcast(self, message, context: ContextTypes.DEFAULT_TYPE):
        users = await self.db.get_all_users()
        for user in users:
            try:
                await context.bot.send_message(chat_id=user['user_id'], text=message)
            except Exception:
                pass
