import os
import logging
import asyncio
import time
import psutil
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.config import Config
from utils.helpers import check_force_sub
from database.mongo import Database
from modules.downloader import UniversalDownloader
from modules.instagram import InstagramDownloader

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

db = Database(Config.MONGODB_URI)
universal_dl = UniversalDownloader()
insta_dl = InstagramDownloader()

# --- Health Check Server ---
async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.add_user(user.id, user.username)
    
    if not await check_force_sub(context.bot, user.id):
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_btn)

    # User Profile Pic Logic
    start_pic = Config.START_PIC
    if not start_pic:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    # Button Layout: Row 1 (2 buttons), Row 2 (2 buttons), Row 3 (Full), Row 4 (Full)
    keyboard = [
        [
            InlineKeyboardButton("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}"),
            InlineKeyboardButton("Language 🌐", callback_data="change_lang")
        ],
        [
            InlineKeyboardButton("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}"),
            InlineKeyboardButton("Support 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")
        ],
        [InlineKeyboardButton(f"👤 {user.first_name}", url=f"tg://user?id={user.id}")],
        [InlineKeyboardButton("📜 Terms of Service", callback_data="view_tos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    intro = "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your minimal media assistant. Use /help to explore."
    
    try:
        await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')
    except Exception:
        await update.message.reply_text(intro, reply_markup=reply_markup, parse_mode='HTML')

async def dl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("Usage: /dl <url>")
    msg = await update.message.reply_text("⏳ Processing...")
    await universal_dl.download(url, msg)

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = " ".join(context.args)
    if not username: return await update.message.reply_text("Usage: /profile <username>")
    await update.message.reply_text(f"📸 Fetching profile: @{username}")
    # Call insta_dl.download_profile(username)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_map = (
        "🗺 <b>Bot Mind Map</b>\n\n"
        "START\n"
        " ┣ 📥 <b>Downloaders</b>\n"
        " ┃ ┣ 📸 Instagram (/profile)\n"
        " ┃ ┣ 🎵 Music (#music)\n"
        " ┃ ┗ 🎥 Universal (/dl)\n"
        " ┣ 🛠 <b>Support</b>\n"
        " ┃ ┣ 👑 Owner (@TechnicalSerena)\n"
        " ┃ ┗ 📜 TOS (/tos)\n"
        " ┗ ⚙️ <b>Settings</b>\n"
        "   ┗ 🌐 Language"
    )
    await update.message.reply_text(help_map, parse_mode='HTML')

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS: return
    
    # System Stats
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    users = await db.get_all_users()
    
    stats = (
        "📊 <b>Admin Dashboard</b>\n\n"
        f"👥 <b>Total Users:</b> {len(users)}\n"
        f"🖥 <b>CPU Usage:</b> {cpu}%\n"
        f"💾 <b>RAM Usage:</b> {ram}%\n"
        f"📶 <b>Latency:</b> {round(context.bot.timeout, 2)}s\n"
    )
    await update.message.reply_text(stats, parse_mode='HTML')

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_handler))
    application.add_handler(CommandHandler("users", admin_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
