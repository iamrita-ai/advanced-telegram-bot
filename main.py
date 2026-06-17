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
from modules.music import MusicDownloader

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

db = Database(Config.MONGODB_URI)
universal_dl = UniversalDownloader()
insta_dl = InstagramDownloader()
music_dl = MusicDownloader()

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

def create_button(text, url=None, callback_data=None):
    btn_dict = {"text": text}
    if url: btn_dict["url"] = url
    if callback_data: btn_dict["callback_data"] = callback_data
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

    keyboard = [
        [create_button("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}"), create_button("Language 🌐", callback_data="change_lang")],
        [create_button("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}"), create_button("Support 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")],
        [create_button(f"👤 {user.first_name}", url=f"tg://user?id={user.id}")],
        [create_button("📜 Terms of Service", callback_data="view_tos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    intro = "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your minimal media assistant. Use /help to explore."
    await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "view_tos":
        tos_text = (
            "📜 <b>Terms of Service & Privacy Policy</b>\n\n"
            "1️⃣ <b>Data Collection:</b> We only store your User ID and Username for functionality.\n"
            "2️⃣ <b>Media:</b> Files are processed and sent; we do not store them permanently.\n"
            "3️⃣ <b>Cookies:</b> Session cookies are encrypted and used only for your requests.\n"
            "✅ <i>By using this bot, you agree to these terms.</i>"
        )
        await query.message.reply_text(tos_text, parse_mode='HTML')
    elif query.data == "change_lang":
        lang_text = "🌐 <b>Select Language:</b>\n\n• English\n• Hindi\n• French\n• Korean\n• Russian"
        await query.message.reply_text(lang_text, parse_mode='HTML')

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("#music", "").strip() if "#music" in update.message.text else " ".join(context.args)
    if not query: return await update.message.reply_text("Usage: #music <song name>")
    msg = await update.message.reply_text(f"🎵 Searching for: <b>{query}</b>...", parse_mode='HTML')
    await music_dl.search_and_download(query, msg)

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    application.add_handler(CommandHandler("music", music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
