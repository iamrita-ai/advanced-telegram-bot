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
logger = logging.getLogger(__name__)

db = Database(Config.MONGODB_URI)
universal_dl = UniversalDownloader()
insta_dl = InstagramDownloader()
music_dl = MusicDownloader()

# --- Multi-Language Data ---
LANG_DATA = {
    "English": {
        "welcome": "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your minimal media assistant.",
        "help_btn": "Use /help to explore.",
        "report": "Report Errors 🛠",
        "lang": "Language 🌐",
        "owner": "Owner 👑",
        "support": "Support 🛠",
        "tos": "📜 Terms of Service",
        "help_text": "🗺 <b>Mind Map</b>\n\n📸 <b>Insta:</b> /profile [user]\n🎵 <b>Music:</b> #music [name]\n🎥 <b>DL:</b> /dl [url]",
        "eta": "⏳ ETA",
        "speed": "🚀 Speed",
        "done": "✅ Done"
    },
    "Hindi": {
        "welcome": "✨ <b>Insta Music में आपका स्वागत है</b> ✨\n\nमैं आपका मीडिया सहायक हूँ।",
        "help_btn": "सुविधाओं के लिए /help का उपयोग करें।",
        "report": "त्रुटि रिपोर्ट 🛠",
        "lang": "भाषा 🌐",
        "owner": "मालिक 👑",
        "support": "सहायता 🛠",
        "tos": "📜 सेवा की शर्तें",
        "help_text": "🗺 <b>माइंड मैप</b>\n\n📸 <b>इंस्टा:</b> /profile [user]\n🎵 <b>संगीत:</b> #music [name]\n🎥 <b>डाउनलोड:</b> /dl [url]",
        "eta": "⏳ समय",
        "speed": "🚀 गति",
        "done": "✅ पूर्ण"
    },
    "French": {
        "welcome": "✨ <b>Bienvenue sur Insta Music</b> ✨\n\nJe suis votre assistant média.",
        "help_btn": "Utilisez /help pour explorer.",
        "report": "Signaler Erreurs 🛠",
        "lang": "Langue 🌐",
        "owner": "Propriétaire 👑",
        "support": "Support 🛠",
        "tos": "📜 Conditions de Service",
        "help_text": "🗺 <b>Carte Mentale</b>\n\n📸 <b>Insta:</b> /profile [user]\n🎵 <b>Musique:</b> #music [name]\n🎥 <b>DL:</b> /dl [url]",
        "eta": "⏳ Temps",
        "speed": "🚀 Vitesse",
        "done": "✅ Terminé"
    },
    "Korean": {
        "welcome": "✨ <b>인스타 뮤직에 오신 것을 환영합니다</b> ✨\n\n저는 당신의 미디어 도우미입니다.",
        "help_btn": "/help를 사용하여 기능을 탐색하십시오.",
        "report": "오류 보고 🛠",
        "lang": "언어 🌐",
        "owner": "소유자 👑",
        "support": "지원 🛠",
        "tos": "📜 서비스 약관",
        "help_text": "🗺 <b>마인드 맵</b>\n\n📸 <b>인스타:</b> /profile [user]\n🎵 <b>음악:</b> #music [name]\n🎥 <b>다운로드:</b> /dl [url]",
        "eta": "⏳ 남은 시간",
        "speed": "🚀 속도",
        "done": "✅ 완료"
    },
    "Russian": {
        "welcome": "✨ <b>Добро пожаловать в Insta Music</b> ✨\n\nЯ ваш медиа-помощник.",
        "help_btn": "Используйте /help для изучения.",
        "report": "Сообщить об ошибке 🛠",
        "lang": "Язык 🌐",
        "owner": "Владелец 👑",
        "support": "Поддержка 🛠",
        "tos": "📜 Условия использования",
        "help_text": "🗺 <b>Карта мыслей</b>\n\n📸 <b>Инста:</b> /profile [user]\n🎵 <b>Музыка:</b> #music [name]\n🎥 <b>Загрузка:</b> /dl [url]",
        "eta": "⏳ Время",
        "speed": "🚀 Скорость",
        "done": "✅ Готово"
    }
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

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_lang = await db.get_user_lang(user.id)
    texts = LANG_DATA[user_lang]
    
    if not await check_force_sub(context.bot, user.id):
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_btn)

    start_pic = Config.START_PIC
    if not start_pic:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    keyboard = [
        [InlineKeyboardButton(texts["report"], url=f"https://t.me/{Config.OWNER_USERNAME[1:]}"), InlineKeyboardButton(texts["lang"], callback_data="change_lang")],
        [InlineKeyboardButton(texts["owner"], url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}"), InlineKeyboardButton(texts["support"], url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")],
        [InlineKeyboardButton(f"👤 {user.first_name}", url=f"tg://user?id={user.id}")],
        [InlineKeyboardButton(texts["tos"], callback_data="view_tos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    intro = f"{texts['welcome']}\n\n{texts['help_btn']}"
    await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_lang = await db.get_user_lang(user_id)
    texts = LANG_DATA[user_lang]
    await query.answer()
    
    if query.data == "view_tos":
        await query.message.reply_text(texts["tos"], parse_mode='HTML')
    elif query.data == "change_lang":
        buttons = [[InlineKeyboardButton(lang, callback_data=f"setlang_{lang}")] for lang in LANG_DATA.keys()]
        await query.message.reply_text(texts["lang"], reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')
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
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(CommandHandler("music", music_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logger.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
