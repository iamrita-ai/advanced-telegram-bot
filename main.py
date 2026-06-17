import os
import logging
import asyncio
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

# --- Multi-Language Strings ---
LANG_DATA = {
    "English": {"welcome": "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your minimal media assistant.", "help": "Use /help to explore."},
    "Hindi": {"welcome": "✨ <b>Insta Music में आपका स्वागत है</b> ✨\n\nमैं आपका मीडिया सहायक हूँ।", "help": "सुविधाओं के लिए /help का उपयोग करें।"},
    "French": {"welcome": "✨ <b>Bienvenue sur Insta Music</b> ✨\n\nJe suis votre assistant média.", "help": "Utilisez /help pour explorer."},
    "Korean": {"welcome": "✨ <b>인스타 뮤직에 오신 것을 환영합니다</b> ✨\n\n저는 당신의 미디어 도우미입니다.", "help": "/help를 사용하여 기능을 탐색하십시오."},
    "Russian": {"welcome": "✨ <b>Добро пожаловать в Insta Music</b> ✨\n\nЯ ваш медиа-помощник.", "help": "Используйте /help для изучения."}
}

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
    user_lang = await db.get_user_lang(user.id) or "English"
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
    
    intro = f"{LANG_DATA[user_lang]['welcome']}\n\n{LANG_DATA[user_lang]['help']}"
    await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "view_tos":
        tos_text = "📜 <b>Terms of Service</b>\n\n1. Data is secure.\n2. Media is not stored.\n3. Respect copyrights."
        await query.message.reply_text(tos_text, parse_mode='HTML')
    elif query.data == "change_lang":
        buttons = [[create_button(lang, callback_data=f"setlang_{lang}")] for lang in LANG_DATA.keys()]
        await query.message.reply_text("🌐 <b>Select Language:</b>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')
    elif query.data.startswith("setlang_"):
        new_lang = query.data.split("_")[1]
        await db.set_user_lang(user_id, new_lang)
        await query.message.edit_text(f"✅ Language changed to: <b>{new_lang}</b>", parse_mode='HTML')

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("#music", "").strip() if "#music" in update.message.text else " ".join(context.args)
    if not query: return await update.message.reply_text("Usage: #music <song name>")
    msg = await update.message.reply_text(f"🎵 Searching for: <b>{query}</b>...", parse_mode='HTML')
    await music_dl.search_and_download(query, msg)

async def dl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("Usage: /dl <url>")
    msg = await update.message.reply_text("⏳ Processing your link...")
    await universal_dl.download(url, msg)

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("music", music_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
