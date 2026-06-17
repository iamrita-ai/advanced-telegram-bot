import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot tokens and IDs
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Support multiple owners (comma separated in .env)
    OWNER_IDS = [int(id.strip()) for id in os.getenv("OWNER_IDS", "").split(",") if id.strip()]
    
    # Log channel for activities
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))
    
    # Database
    MONGODB_URI = os.getenv("MONGODB_URI")
    
    # AI APIs
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Force Subscription
    FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@TechnicalSerena")
    
    # Credits and Branding
    OWNER_NAME = "Technical Serena"
    OWNER_USERNAME = "@TechnicalSerena"
    DEVELOPER_USERNAME = "@Xioqui_Xin"
    
    # Bot Settings
    DEFAULT_LANGUAGE = "English"
    SUPPORTED_LANGUAGES = ["English", "French", "Hindi", "Korean", "Russian"]
    
    # Render Port (to fix "no open ports detected")
    PORT = int(os.environ.get('PORT', 8080))
