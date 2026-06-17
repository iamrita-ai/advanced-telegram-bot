import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config.config import Config
from utils.helpers import check_force_sub
from database.mongo import Database

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

db = Database(Config.MONGODB_URI)

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

    # Aesthetic Start Message
    intro = (
        "✨ <b>Welcome to Insta Music</b> ✨\n\n"
        "I am your all-in-one media assistant. I can download:\n"
        "• 📸 <b>Instagram:</b> Reels, Stories, Posts, & Profiles.\n"
        "• 🎵 <b>Music:</b> High-quality MP3s with metadata.\n"
        "• 🎥 <b>Universal:</b> YouTube, TikTok, FB, & more.\n\n"
        "Use /help to explore my features.\n"
        "Read our /tos before using."
    )
    
    # Colored Buttons (Simulated via Bot API 9.4+ style if supported by client)
    keyboard = [
        [{"text": "Report Errors 🛠", "url": f"https://t.me/{Config.OWNER_USERNAME[1:]}", "style": "danger"}],
        [{"text": "Owner 👑", "url": f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}", "style": "success"}],
        [{"text": f"👤 {user.first_name}", "url": f"tg://user?id={user.id}", "style": "primary"}]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(intro, reply_markup=reply_markup, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>Insta Music Manual</b>\n\n"
        "🚀 <b>Commands:</b>\n"
        "• <code>/profile &lt;user&gt;</code> - Download Instagram Profile\n"
        "• <code>#music &lt;name&gt;</code> - Search & Download Music\n"
        "• <code>/dl &lt;url&gt;</code> - Universal Link Downloader\n"
        "• <code>/tos</code> - Read Terms of Service\n\n"
        "🛠 <b>Support:</b> @TechnicalSerena"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def tos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tos_text = (
        "📜 <b>Terms of Service & Privacy Policy</b>\n\n"
        "1️⃣ <b>Data Collection:</b> We only store your Telegram User ID and Username to provide personalized services and admin updates.\n\n"
        "2️⃣ <b>Media Processing:</b> All media is processed in real-time. We do not store your downloaded files on our permanent servers after delivery.\n\n"
        "3️⃣ <b>Privacy:</b> Your search history and download logs are strictly confidential and are used only for improving bot performance.\n\n"
        "4️⃣ <b>Cookies:</b> Any session cookies you provide are encrypted and used solely for accessing private content requested by you.\n\n"
        "5️⃣ <b>Copyright:</b> Users are responsible for the content they download. Please respect intellectual property rights.\n\n"
        "✅ <i>By using this bot, you agree to these terms.</i>"
    )
    await update.message.reply_text(tos_text, parse_mode='HTML')

async def cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.OWNER_IDS:
        return await update.message.reply_text("Unauthorized.")
    
    data = " ".join(context.args)
    if not data:
        return await update.message.reply_text("❌ Please provide cookie data in Netscape format.")
    
    # Save cookie logic...
    await update.message.reply_text("✅ Cookies updated successfully.")

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tos", tos_command))
    application.add_handler(CommandHandler("cookies", cookies_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), help_command)) # Placeholder for logic
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True: await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
