import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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
    user = update.effective_user
    user_id = user.id
    
    # Force Sub Check
    if not await check_force_sub(context.bot, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL[1:]}")]])
        return await update.message.reply_text(f"❌ Access Denied!\n\nPlease join {Config.FORCE_SUB_CHANNEL} to use me.", reply_markup=join_button)
    
    # Dynamic Start Picture
    start_pic = os.getenv("START_PIC")
    if not start_pic:
        # Get user profile picture if START_PIC is not set
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            start_pic = photos.photos[0][-1].file_id
        else:
            # Fallback if no profile pic
            start_pic = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif"

    keyboard = [
        [InlineKeyboardButton("Report Errors 🛠", url=f"https://t.me/{Config.OWNER_USERNAME[1:]}")],
        [InlineKeyboardButton("Owner 👑", url=f"https://t.me/{Config.DEVELOPER_USERNAME[1:]}")],
        [InlineKeyboardButton(f"👤 {user.first_name}", url=f"tg://user?id={user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Use HTML to avoid Markdown parsing issues with underscores in usernames
    welcome_msg = (
        f"✨ <b>Welcome to Technical Serena's Advanced Bot</b> ✨\n\n"
        f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{user.first_name}</a>\n"
        f"👑 <b>Owner:</b> {Config.OWNER_NAME}\n"
        f"💻 <b>Developer:</b> {Config.DEVELOPER_USERNAME}\n\n"
        f"Use /help to explore features!"
    )
    
    try:
        if isinstance(start_pic, str) and start_pic.startswith("http"):
            await update.message.reply_photo(photo=start_pic, caption=welcome_msg, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_photo(photo=start_pic, caption=welcome_msg, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logging.error(f"Error sending start photo: {e}")
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='HTML')

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    query = text.replace("#music", "").strip()
    if not query:
        return await update.message.reply_text("Usage: #music <song name>")
    
    await update.message.reply_text(f"🎵 Searching for: <b>{query}</b>...", parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        f"📖 <b>Bot Manual</b>\n\n"
        f"🚀 <b>Commands:</b>\n"
        f"• <code>/profile &lt;user&gt;</code> - Instagram Downloader\n"
        f"• <code>#music &lt;name&gt;</code> - Search Music\n"
        f"• <code>/dl &lt;url&gt;</code> - All-in-one Downloader\n\n"
        f"🛠 <b>Support:</b> {Config.OWNER_USERNAME}"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def main():
    asyncio.create_task(start_server())
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex(r'^#music'), music_handler))
    
    logging.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
