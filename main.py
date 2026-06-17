import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.first_name}! I am your advanced assistant bot. Use /help to see what I can do.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available Commands:
/start - Start the bot
/help - Show this help message
/profile <username> - Download Instagram profile data
/music <name> - Search and download music
/dl <url> - Universal downloader
/cancel - Cancel ongoing tasks
/lock - Lock the bot (Admin)
/unlock - Unlock the bot (Admin)
/cookies - Update Instagram cookies
/admin - Admin panel
    """
    await update.message.reply_text(help_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Logic to cancel ongoing tasks for the user
    await update.message.reply_text("All ongoing tasks have been cancelled.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Placeholder for other handlers
    # application.add_handler(CommandHandler("profile", profile_handler))
    # application.add_handler(CommandHandler("music", music_handler))
    # application.add_handler(CommandHandler("dl", dl_handler))
    
    application.run_polling()
