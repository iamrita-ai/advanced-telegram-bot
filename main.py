import os
import logging
import asyncio
import random
import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.config import Config
from utils.helpers import check_force_sub
from database.mongo import Database
from modules.downloader import UniversalDownloader
from modules.instagram import InstagramDownloader
from modules.music import MusicDownloader
from modules.ai_caption import AICaptionGenerator

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database(Config.MONGODB_URI)
universal_dl = UniversalDownloader()
insta_dl = InstagramDownloader()
music_dl = MusicDownloader()
ai_caption = AICaptionGenerator()

# --- Reactions Data (60+ Big Animated Emojis) ---
REACTIONS = ["🔥", "👍", "👎", "❤️", "🎉", "🤩", "🙏", "⚡", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🥳", "🎈", "🎊", "😎", "🌟"]

# --- Multi-Language Data ---
LANG_DATA = {
    "English": {
        "welcome": "✨ <b>Welcome to Insta Music</b> ✨\n\nI am your advanced media assistant. I can download Reels, Music, and more with high quality!",
        "help_btn": "Use /help to explore my features.",
        "report": "Report Errors 🛠",
        "lang": "Language 🌐",
        "owner": "Owner 👑",
        "support": "Support 🛠",
        "tos": "📜 Terms of Service",
        "processing": "⏳ Processing your link...",
        "searching": "🎵 Searching for: <b>{}</b>...",
        "downloading": "⬇️ Downloading from server...",
        "done": "Done",
        "progress": "Progress",
        "speed": "Speed",
        "eta": "ETA",
        "network": "Network",
        "tos_full": "📜 <b>Terms of Service</b>\n\n1. Data Privacy: We do not store your personal media.\n2. Usage Policy: Use responsibly.\n3. Content Responsibility: You are responsible for the content you download.\n4. No Warranty: Provided as-is.\n5. Compliance: Follow Telegram and source platform terms.",
        "help_text": "🧠 <b>Bot Mind Map</b>\n\n📥 <b>Downloaders</b>\n• <code>/dl [url]</code> - Download any video/reel\n🎵 <b>Music</b>\n• <code>/music [name]</code> - Search and download MP3\n👤 <b>Profile</b>\n• <code>/profile [username]</code> - Download Insta profile pic"
    },
    "Hindi": {
        "welcome": "✨ <b>Insta Music में आपका स्वागत है</b> ✨\n\nमैं आपका उन्नत मीडिया सहायक हूँ। मैं रील्स और संगीत डाउनलोड कर सकता हूँ!",
        "help_btn": "/help का उपयोग करें।",
        "report": "त्रुटि रिपोर्ट 🛠",
        "lang": "भाषा 🌐",
        "owner": "मालिक 👑",
        "support": "सहायता 🛠",
        "tos": "📜 सेवा की शर्तें",
        "processing": "⏳ प्रोसेस हो रहा है...",
        "searching": "🎵 खोजा जा रहा है: <b>{}</b>...",
        "downloading": "⬇️ डाउनलोड हो रहा है...",
        "done": "पूर्ण",
        "progress": "प्रगति",
        "speed": "गति",
        "eta": "समय",
        "network": "नेटवर्क",
        "tos_full": "📜 <b>सेवा की शर्तें</b>\n\n1. डेटा गोपनीयता\n2. उपयोग नीति\n3. सामग्री जिम्मेदारी\n4. कोई वारंटी नहीं\n5. अनुपालन",
        "help_text": "🧠 <b>सहायता माइंड मैप</b>\n\n📥 <b>डाउनलोडर</b>\n• <code>/dl [url]</code> - कोई भी वीडियो डाउनलोड करें\n🎵 <b>संगीत</b>\n• <code>/music [name]</code> - MP3 खोजें और डाउनलोड करें\n👤 <b>प्रोफ़ाइल</b>\n• <code>/profile [username]</code> - इंस्टा प्रोफ़ाइल फोटो डाउनलोड करें"
    },
    "Korean": {
        "welcome": "✨ <b>Insta Music에 오신 것을 환영합니다</b> ✨\n\n저는 고급 미디어 도우미입니다. 릴스, 음악 등을 고품질로 다운로드할 수 있습니다!",
        "help_btn": "/help를 사용하여 기능을 탐색하십시오.",
        "report": "오류 보고 🛠",
        "lang": "언어 🌐",
        "owner": "소유자 👑",
        "support": "지원 🛠",
        "tos": "📜 서비스 약관",
        "processing": "⏳ 링크를 처리 중입니다...",
        "searching": "🎵 검색 중: <b>{}</b>...",
        "downloading": "⬇️ 서버에서 다운로드 중...",
        "done": "완료",
        "progress": "진행",
        "speed": "속도",
        "eta": "남은 시간",
        "network": "네트워크",
        "tos_full": "📜 <b>서비스 약관</b>\n\n1. 데이터 개인 정보 보호\n2. 사용 정책\n3. 콘텐츠 책임\n4. 보증 없음\n5. 규정 준수",
        "help_text": "🧠 <b>봇 마인드 맵</b>\n\n📥 <b>다운로더</b>\n• <code>/dl [url]</code> - 모든 비디오 다운로드\n🎵 <b>음악</b>\n• <code>/music [name]</code> - MP3 검색 및 다운로드\n👤 <b>프로필</b>\n• <code>/profile [username]</code> - 인스타 프로필 사진 다운로드"
    },
    "Russian": {
        "welcome": "✨ <b>Добро пожаловать в Insta Music</b> ✨\n\nЯ ваш продвинутый медиа-помощник. Я могу скачивать Reels, музыку и многое другое в высоком качестве!",
        "help_btn": "Используйте /help, чтобы изучить мои возможности.",
        "report": "Сообщить об ошибках 🛠",
        "lang": "Язык 🌐",
        "owner": "Владелец 👑",
        "support": "Поддержка 🛠",
        "tos": "📜 Условия использования",
        "processing": "⏳ Обработка вашей ссылки...",
        "searching": "🎵 Поиск: <b>{}</b>...",
        "downloading": "⬇️ Загрузка с сервера...",
        "done": "Готово",
        "progress": "Прогресс",
        "speed": "Скорость",
        "eta": "Осталось",
        "network": "Сеть",
        "tos_full": "📜 <b>Условия использования</b>\n\n1. Конфиденциальность данных\n2. Политика использования\n3. Ответственность за контент\n4. Отказ от гарантий\n5. Соблюдение правил",
        "help_text": "🧠 <b>Карта функций бота</b>\n\n📥 <b>Загрузчики</b>\n• <code>/dl [url]</code> - Скачать любое видео\n🎵 <b>Музыка</b>\n• <code>/music [name]</code> - Поиск и скачивание MP3\n👤 <b>Профиль</b>\n• <code>/profile [username]</code> - Скачать фото профиля Инста"
    },
    "French": {
        "welcome": "✨ <b>Bienvenue sur Insta Music</b> ✨\n\nJe suis votre assistant média avancé. Je peux télécharger des Reels, de la musique et plus encore en haute qualité !",
        "help_btn": "Utilisez /help pour explorer mes fonctionnalités.",
        "report": "Signaler des erreurs 🛠",
        "lang": "Langue 🌐",
        "owner": "Propriétaire 👑",
        "support": "Support 🛠",
        "tos": "📜 Conditions d'utilisation",
        "processing": "⏳ Traitement de votre lien...",
        "searching": "🎵 Recherche de : <b>{}</b>...",
        "downloading": "⬇️ Téléchargement depuis le serveur...",
        "done": "Terminé",
        "progress": "Progression",
        "speed": "Vitesse",
        "eta": "Temps restant",
        "network": "Réseau",
        "tos_full": "📜 <b>Conditions d'utilisation</b>\n\n1. Confidentialité des données\n2. Politique d'utilisation\n3. Responsabilité du contenu\n4. Aucune garantie\n5. Conformité",
        "help_text": "🧠 <b>Carte mentale du bot</b>\n\n📥 <b>Téléchargeurs</b>\n• <code>/dl [url]</code> - Télécharger n'importe quelle vidéo\n🎵 <b>Musique</b>\n• <code>/music [name]</code> - Rechercher et télécharger MP3\n👤 <b>Profil</b>\n• <code>/profile [username]</code> - Télécharger la photo de profil Insta"
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
async def send_reaction(update: Update, emoji=None):
    try:
        if not emoji:
            emoji = random.choice(REACTIONS)
        await update.message.set_reaction(reaction=emoji, is_big=True)
    except Exception as e:
        logger.error(f"Reaction error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    await db.add_user(user.id, user.username)
    user_lang = await db.get_user_lang(user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    
    if not await check_force_sub(context.bot, user.id):
        await send_reaction(update, "💩")
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_btn)

    await send_reaction(update)
    start_pic = Config.START_PIC
    if not start_pic:
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"
        except:
            start_pic = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    keyboard = [
        [
            {"text": texts["report"], "url": f"https://t.me/{Config.OWNER_USERNAME[1:]}"},
            {"text": texts["lang"], "callback_data": "change_lang"}
        ],
        [
            {"text": texts["owner"], "url": f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}"},
            {"text": texts["support"], "url": f"https://t.me/{Config.OWNER_USERNAME[1:]}"}
        ],
        [{"text": f"👤 {user.first_name}", "url": f"tg://user?id={user.id}"}],
        [{"text": texts["tos"], "callback_data": "view_tos"}]
    ]
    
    # Use dict for colored buttons styling bypass
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": texts["report"], "url": f"https://t.me/{Config.OWNER_USERNAME[1:]}", "style": "danger"},
                {"text": texts["lang"], "callback_data": "change_lang", "style": "primary"}
            ],
            [
                {"text": texts["owner"], "url": f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}", "style": "success"},
                {"text": texts["support"], "url": f"https://t.me/{Config.OWNER_USERNAME[1:]}", "style": "primary"}
            ],
            [{"text": f"👤 {user.first_name}", "url": f"tg://user?id={user.id}", "style": "primary"}],
            [{"text": texts["tos"], "callback_data": "view_tos", "style": "primary"}]
        ]
    }
    
    await update.message.reply_photo(photo=start_pic, caption=texts["welcome"], reply_markup=reply_markup, parse_mode='HTML')

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = await db.get_user_lang(update.effective_user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    await update.message.reply_text(texts["help_text"], parse_mode='HTML')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_lang = await db.get_user_lang(user_id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    await query.answer()
    
    if query.data == "view_tos":
        await query.message.reply_text(texts["tos_full"], parse_mode='HTML')
    elif query.data == "change_lang":
        buttons = [[{"text": lang, "callback_data": f"setlang_{lang}", "style": "primary"}] for lang in ["English", "Hindi", "French", "Korean", "Russian"]]
        await query.message.reply_text(f"🌐 <b>{texts['lang']}</b>", reply_markup={"inline_keyboard": buttons}, parse_mode='HTML')
    elif query.data.startswith("setlang_"):
        new_lang = query.data.split("_")[1]
        await db.set_user_lang(user_id, new_lang)
        await query.message.edit_text(f"✅ Language changed to: <b>{new_lang}</b>", parse_mode='HTML')

async def dl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_reaction(update)
    user_lang = await db.get_user_lang(update.effective_user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("Usage: /dl <url>")
    msg = await update.message.reply_text(texts["processing"])
    
    file_path, info = await universal_dl.download(url, msg, texts)
    if file_path:
        caption = await ai_caption.generate_caption(info, language=user_lang)
        await universal_dl.send_media(update.message, file_path, info, caption)

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_reaction(update)
    username = " ".join(context.args)
    if not username: return await update.message.reply_text("Usage: /profile <username>")
    msg = await update.message.reply_text(f"📸 Fetching Instagram profile: @{username}...")
    
    # Ensure cookies are loaded for profile fetching
    cookies = await db.get_cookies("instagram")
    if cookies:
        with open("cookies_instagram.txt", "w") as f: f.write(cookies)
    
    await insta_dl.download_profile(username, msg)

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_reaction(update)
    user_lang = await db.get_user_lang(update.effective_user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    query = " ".join(context.args)
    if not query: return await update.message.reply_text("Usage: /music <song name>")
    msg = await update.message.reply_text(texts["searching"].format(query), parse_mode='HTML')
    
    # Ensure cookies are loaded for music search
    cookies = await db.get_cookies("youtube")
    if cookies:
        with open("cookies_youtube.txt", "w") as f: f.write(cookies)
        
    await music_dl.search_and_download(query, msg)

async def cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, service=None):
    user_id = update.effective_user.id
    if user_id not in Config.OWNER_IDS: return
    
    if not service:
        if context.args: service = context.args[0].lower()
        else: service = "instagram"

    # Check if this is a reply to a document
    target_msg = update.message
    if update.message.reply_to_message and update.message.reply_to_message.document:
        target_msg = update.message.reply_to_message

    if target_msg.document and target_msg.document.file_name.endswith(".txt"):
        file = await context.bot.get_file(target_msg.document.file_id)
        content = (await file.download_as_bytearray()).decode('utf-8')
        await db.save_cookies(service, content)
        with open(f"cookies_{service}.txt", "w") as f: f.write(content)
        return await update.message.reply_text(f"✅ Cookies for {service} updated and saved to DB!")
    
    await update.message.reply_text(f"❌ Please reply to a .txt file with /{service} to set cookies.")

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    # Restore cookies from DB on startup
    for service in ["instagram", "youtube"]:
        cookies = await db.get_cookies(service)
        if cookies:
            with open(f"cookies_{service}.txt", "w") as f: f.write(cookies)
            logger.info(f"Restored {service} cookies from database.")
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler("music", music_handler))
    application.add_handler(CommandHandler("insta", lambda u, c: cookies_handler(u, c, "instagram")))
    application.add_handler(CommandHandler("yt", lambda u, c: cookies_handler(u, c, "youtube")))
    application.add_handler(MessageHandler(filters.Document.FileExtension("txt"), cookies_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    
    logger.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
