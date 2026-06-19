import os
import logging
import asyncio
import random
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

# --- Reactions Data (60+ Emojis) ---
EMOJIS = [
    "🔥", "⚡", "✨", "🌟", "❤️", "🎉", "🚀", "🤖", "😎", "💎", "🎯", "🌈", "🎬", "🎵", "📸", "✅", "👑", "💡", "🛡️", "🤝",
    "🤩", "🥳", "🤯", "🥰", "😍", "😋", "😜", "😇", "🤔", "🤫", "🫡", "💪", "🙌", "👏", "🤜", "🤛", "✌️", "🤟", "🎸", "🎹",
    "🎺", "🎻", "🎧", "🎤", "🎥", "🎞️", "🍿", "📺", "🎮", "🕹️", "📱", "💻", "🛰️", "🛸", "🌍", "🌕", "🌞", "🍀", "🎈", "🎁"
]

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
        "processing": "⏳ Processing your link...",
        "searching": "🎵 Searching for: <b>{}</b>...",
        "downloading": "⬇️ Downloading from server...",
        "done": "Done",
        "progress": "Progress",
        "speed": "Speed",
        "eta": "ETA",
        "network": "Network",
        "tos_full": "📜 <b>Terms of Service</b>\n\n1. Privacy: We don't store your data.\n2. Usage: Bot is for personal use only.\n3. Content: You are responsible for what you download."
    },
    "Hindi": {
        "welcome": "✨ <b>Insta Music में आपका स्वागत है</b> ✨\n\nमैं आपका मीडिया सहायक हूँ।",
        "help_btn": "सुविधाओं के लिए /help का उपयोग करें।",
        "report": "त्रुटि रिपोर्ट 🛠",
        "lang": "भाषा 🌐",
        "owner": "मालिक 👑",
        "support": "सहायता 🛠",
        "tos": "📜 सेवा की शर्तें",
        "processing": "⏳ आपकी लिंक प्रोसेस हो रही है...",
        "searching": "🎵 खोजा जा रहा है: <b>{}</b>...",
        "downloading": "⬇️ सर्वर से डाउनलोड हो रहा है...",
        "done": "पूर्ण",
        "progress": "प्रगति",
        "speed": "गति",
        "eta": "समय",
        "network": "नेटवर्क",
        "tos_full": "📜 <b>सेवा की शर्तें</b>\n\n1. गोपनीयता: हम आपका डेटा स्टोर नहीं करते हैं।\n2. उपयोग: बॉट केवल व्यक्तिगत उपयोग के लिए है।\n3. सामग्री: आप जो डाउनलोड करते हैं उसके लिए आप जिम्मेदार हैं।"
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

# --- Colored Button Helper ---
def colored_button(text, url=None, callback_data=None, style="primary"):
    btn = {"text": text}
    if url: btn["url"] = url
    if callback_data: btn["callback_data"] = callback_data
    btn["style"] = style
    return btn

# --- Bot Handlers ---
async def send_reaction(update: Update, emoji=None):
    try:
        if not emoji:
            emoji = random.choice(EMOJIS)
        # Using big animated reactions
        await update.message.set_reaction(reaction=emoji, is_big=True)
    except Exception as e:
        logger.error(f"Reaction error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_lang = await db.get_user_lang(user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    
    if not await check_force_sub(context.bot, user.id):
        await send_reaction(update, "💩")
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_btn)

    await send_reaction(update)
    start_pic = Config.START_PIC
    if not start_pic:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        start_pic = photos.photos[0][-1].file_id if photos.total_count > 0 else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    keyboard = [
        [
            colored_button(texts["report"], url=f"https://t.me/{Config.OWNER_USERNAME[1:]}", style="danger"),
            colored_button(texts["lang"], callback_data="change_lang", style="primary")
        ],
        [
            colored_button(texts["owner"], url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}", style="success"),
            colored_button(texts["support"], url=f"https://t.me/{Config.OWNER_USERNAME[1:]}", style="primary")
        ],
        [colored_button(f"👤 {user.first_name}", url=f"tg://user?id={user.id}", style="primary")],
        [colored_button(texts["tos"], callback_data="view_tos", style="danger")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    intro = f"{texts['welcome']}\n\n{texts['help_btn']}"
    await update.message.reply_photo(photo=start_pic, caption=intro, reply_markup=reply_markup, parse_mode='HTML')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_lang = await db.get_user_lang(user_id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    await query.answer()
    
    if query.data == "view_tos":
        await query.message.reply_text(texts["tos_full"], parse_mode='HTML')
    elif query.data == "change_lang":
        buttons = [[colored_button(lang, callback_data=f"setlang_{lang}", style="success")] for lang in ["English", "Hindi", "French", "Korean", "Russian"]]
        await query.message.reply_text(f"🌐 <b>{texts['lang']}</b>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')
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
    
    # Process download and generate AI caption
    file_path, info = await universal_dl.download(url, msg, texts)
    if file_path:
        caption = await ai_caption.generate_caption(info, language=user_lang)
        await universal_dl.send_media(update.message, file_path, info, caption)

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_reaction(update)
    user_lang = await db.get_user_lang(update.effective_user.id)
    texts = LANG_DATA.get(user_lang, LANG_DATA["English"])
    query = update.message.text.replace("#music", "").strip() if "#music" in update.message.text else " ".join(context.args)
    if not query: return await update.message.reply_text("Usage: #music <song name>")
    msg = await update.message.reply_text(texts["searching"].format(query), parse_mode='HTML')
    await music_dl.search_and_download(query, msg)

async def cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS: return
    if update.message.document and update.message.document.file_name.endswith(".txt"):
        file_name = update.message.document.file_name
        file = await context.bot.get_file(update.message.document.file_id)
        # Support multiple cookie files (e.g., instagram_cookies.txt, youtube_cookies.txt)
        save_path = os.path.join(os.getcwd(), file_name)
        await file.download_to_drive(save_path)
        return await update.message.reply_text(f"✅ <b>{file_name}</b> updated successfully!", parse_mode='HTML')
    await update.message.reply_text("❌ Please upload a valid <code>.txt</code> cookie file.", parse_mode='HTML')

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dl", dl_handler))
    application.add_handler(CommandHandler("cookies", cookies_handler))
    application.add_handler(MessageHandler(filters.Document.FileExtension("txt"), cookies_handler))
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
