from config.config import Config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

STRINGS = {
    "English": {
        "welcome": "Welcome to Advanced Bot! 🚀",
        "force_sub": "Please join our channel to use this bot.",
        "lang_select": "Select your preferred language:",
        "error_report": "Report Errors",
    },
    "Hindi": {
        "welcome": "एडवांस्ड बॉट में आपका स्वागत है! 🚀",
        "force_sub": "कृपया इस बॉट का उपयोग करने के लिए हमारे चैनल से जुड़ें।",
        "lang_select": "अपनी पसंदीदा भाषा चुनें:",
        "error_report": "त्रुटि रिपोर्ट करें",
    },
    # Add other languages similarly...
}

async def check_force_sub(bot, user_id):
    try:
        member = await bot.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return False

def get_language_keyboard():
    buttons = [[InlineKeyboardButton(lang, callback_data=f"setlang_{lang}")] for lang in Config.SUPPORTED_LANGUAGES]
    return InlineKeyboardMarkup(buttons)
