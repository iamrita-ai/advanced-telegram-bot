# Advanced Multi-Media Telegram Bot

A professional, Docker-compatible Telegram bot featuring Instagram downloading, music fetching, universal media downloading, AI-powered caption generation, and a comprehensive admin panel.

## Features

### 📸 Instagram Downloader
- Download Profile Photos, Posts, Reels, Stories, and Highlights.
- Progress tracking with ETA, speed, and size.
- Support for private accounts via cookies.

### 🎵 Music Fetcher
- Search and download music directly to Telegram.
- High-quality MP3 with embedded cover art and metadata.

### 🎥 Universal Downloader
- Support for YouTube, TikTok, Facebook, X, Reddit, Pinterest, and more.
- Batch download support.

### 🤖 AI Caption Generation
- Powered by Groq AI.
- Media analysis for scene, mood, and object detection.
- Customizable caption styles (Genz, Aesthetic, Professional, etc.).

### 🛠 Admin Panel
- User management, broadcasting, and analytics.
- Real-time logs and system metrics.

## Deployment

### Prerequisites
- Telegram Bot Token (from @BotFather)
- MongoDB URI
- Groq API Key
- Render.com Account (for deployment)

### Docker
```bash
docker build -t advanced-bot .
docker run --env-file .env advanced-bot
```

### Render Deployment
1. Connect your GitHub repository to Render.
2. Choose "Web Service" or "Background Worker".
3. Set the environment variables in the Render dashboard.
4. Deploy!

## Commands
- `/start` - Initialize the bot.
- `/help` - View all features and usage.
- `/profile <username>` - Instagram downloader.
- `/music <name>` - Search and download music.
- `/dl <url>` - Universal downloader.
- `/admin` - Access the admin panel.
- `/cookies` - Update session cookies.
- `/lock` / `/unlock` - Bot access control.
