import os
import logging
import asyncio
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

# --- Helper for Colored Buttons ---
def create_button(text, url=None, callback_data=None, style=None):
    # Note: style is not natively supported by python-telegram-bot yet.
    # We pass it in a way that doesn't crash, but actual coloring depends on client support.
    btn_dict = {"text": text}
    if url: btn_dict["url"] = url
    if callback_data: btn_dict["callback_data"] = callback_data
    # We remove 'style' from the constructor call to avoid TypeError
    return InlineKeyboardButton(**btn_dict)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.add_user(user.id, user.username)
    
    if not await check_force_sub(context.bot, user.id):
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_btn)

    start_pic = Config.START_PIC
    if not start_pic:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    # Layout: Row 1 (2x2), Row 2 (Full), Row 3 (Full)
    keyboard = [
        [
            create_button("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}"),
            create_button("Language 🌐", callback_data="change_lang")
        ],
        [
            create_button("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}"),
            create_button("Support 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")
        ],
        [create_button(f"👤 {user.first_name}", url=f"tg://user?id={user.id}")],
        [create_button("📜 Terms of Service", callback_data="view_tos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    intro = "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your minimal media assistant. Use /help to explore."
    await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')

async def dl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("Usage: /dl <url>")
    msg = await update.message.reply_text("⏳ Processing your link...")
    await universal_dl.download(url, msg)

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = " ".join(context.args)
    if not username: return await update.message.reply_text("Usage: /profile <username>")
    msg = await update.message.reply_text(f"📸 Fetching profile: @{username}")
    await insta_dl.download_profile(username, msg)

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("#music", "").strip() if "#music" in update.message.text else " ".join(context.args)
    if not query: return await update.message.reply_text("Usage: #music <song name>")
    await update.message.reply_text(f"🎵 Searching for: <b>{query}</b>...", parse_mode='HTML')
    # Implement actual music search logic here

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🗺 <b>Insta Music Mind Map</b>\n\n"
        "🚀 <b>Media Downloader</b>\n"
        " ┣ 📸 <b>Instagram:</b> <code>/profile prince572002</code>\n"
        " ┣ 🎵 <b>Music:</b> <code>#music Under the influence</code>\n"
        " ┗ 🎥 <b>Universal:</b> <code>/dl [url]</code>\n\n"
        "🛠 <b>Support & Info</b>\n"
        " ┣ 👑 <b>Owner:</b> @TechnicalSerena\n"
        " ┣ 📜 <b>TOS:</b> /tos (Read before use)\n"
        " ┗ 🌐 <b>Lang:</b> Change via /start button"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS: return
    data = " ".join(context.args)
    if not data: return await update.message.reply_text("❌ Please provide cookie data.")
    insta_dl.save_cookies(data)
    await update.message.reply_text("✅ Cookies updated and saved permanently.")

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS: return
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    users = await db.get_all_users()
    stats = f"📊 <b>Stats</b>\n\n👥 Users: {len(users)}\n🖥 CPU: {cpu}%\n💾 RAM: {ram}%"
    await update.message.reply_text(stats, parse_mode='HTML')

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("music", music_handler))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_handler))
    application.add_handler(CommandHandler("cookies", cookies_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
