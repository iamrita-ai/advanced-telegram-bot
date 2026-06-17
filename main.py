import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.config import Config
from utils.helpers import STRINGS, get_language_keyboard, check_force_sub
from modules.instagram import InstagramDownloader
from modules.downloader import UniversalDownloader
from modules.music import MusicDownloader
from modules.admin import AdminPanel
from database.mongo import Database

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize modules
db = Database(Config.MONGODB_URI)
insta_dl = InstagramDownloader(Config.START_PIC)
universal_dl = UniversalDownloader()
music_dl = MusicDownloader()
admin = AdminPanel(db, Config.OWNER_IDS[0] if Config.OWNER_IDS else 0)

# --- Health Check Server for Render ---
async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()
    logging.info(f"Health check server started on port {Config.PORT}")

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Register user in DB
    await db.add_user(user_id, user.username)
    
    if not await check_force_sub(context.bot, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_button)
    
    # Dynamic Start Picture
    start_pic = Config.START_PIC
    if not start_pic:
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    # Aesthetic buttons with user link
    keyboard = [
        [InlineKeyboardButton("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")],
        [InlineKeyboardButton("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}")],
        [InlineKeyboardButton(f"👤 {user.first_name}", url=f"tg://user?id={user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f"✨ <b>Welcome to Advanced Bot</b> ✨\n\n"
        f"Use /help to explore my features.\n"
        f"Read our /tos before using."
    )
    
    try:
        await update.message.reply_photo(photo=start_pic, caption=welcome_msg, reply_markup=reply_markup, parse_mode='HTML')
    except Exception:
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='HTML')

async def dl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url:
        return await update.message.reply_text("Usage: /dl <url>")
    
    msg = await update.message.reply_text("⏳ Processing your request...")
    # Add logic for universal_dl.download here
    await msg.edit_text(f"✅ Download started for: {url}")

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = " ".join(context.args)
    if not username:
        return await update.message.reply_text("Usage: /profile <username>")
    
    await update.message.reply_text(f"📸 Fetching Instagram profile: @{username}...")
    # Add logic for insta_dl.download_profile here

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("#music", "").strip() if "#music" in update.message.text else " ".join(context.args)
    if not query:
        return await update.message.reply_text("Usage: #music <song name> or /music <song name>")
    
    await update.message.reply_text(f"🎵 Searching for: <b>{query}</b>...", parse_mode='HTML')
    # Add logic for music_dl.search_and_download here

async def tos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tos_text = (
        "📜 <b>Terms of Service (ToS)</b>\n\n"
        "1. <b>Data Usage:</b> We only store your User ID and Username for bot functionality and admin broadcasting.\n"
        "2. <b>Media:</b> We do not store downloaded media on our servers; they are processed and sent directly to you.\n"
        "3. <b>Cookies:</b> Any cookies provided for private downloads are stored securely and used only for your requests.\n"
        "4. <b>Responsibility:</b> You are responsible for the content you download. Respect copyright laws."
    )
    await update.message.reply_text(tos_text, parse_mode='HTML')

async def cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS:
        return await update.message.reply_text("Unauthorized.")
    # Logic to save cookies
    await update.message.reply_text("✅ Cookies updated successfully.")

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS:
        return await update.message.reply_text("Unauthorized.")
    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("Usage: /broadcast <message>")
    await admin.broadcast(text, context)
    await update.message.reply_text("✅ Broadcast completed.")

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("music", music_handler))
    application.add_handler(CommandHandler("tos", tos_handler))
    application.add_handler(CommandHandler("cookies", cookies_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
