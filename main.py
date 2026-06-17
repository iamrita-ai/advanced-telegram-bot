import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.config import Config
from utils.helpers import STRINGS, get_language_keyboard, check_force_sub

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
    user_id = update.effective_user.id
    if not await check_force_sub(context.bot, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_button)
    
    keyboard = [
        [InlineKeyboardButton("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")],
        [InlineKeyboardButton("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = f"✨ **Welcome to Technical Serena's Advanced Bot** ✨\n\nCreated by: {Config.OWNER_NAME}\nCredits: {Config.DEVELOPER_USERNAME}\n\nUse /help to explore features!"
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("#music", "").strip()
    if not query:
        return await update.message.reply_text("Usage: #music <song name>")
    
    await update.message.reply_text(f"🎵 Searching for: {query}...")
    # Call music downloader logic here

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"📖 **Bot Manual**\n\nCommands:\n/profile <user> - Instagram\n#music <name> - Search Music\n/dl <url> - All-in-one Downloader\n\nSupport: {Config.OWNER_USERNAME}"
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def main():
    # Start health check server in background
    asyncio.create_task(start_server())
    
    # Initialize Bot
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep the script running
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
