<div align="center">

# 🌟 Advanced Multi-Media Downloader 🌟
### ✨ Professional Telegram Bot by Technical Serena ✨

![GitHub License](https://img.shields.io/github/license/iamrita-ai/advanced-telegram-bot?style=for-the-badge&color=blue)
![GitHub Stars](https://img.shields.io/github/stars/iamrita-ai/advanced-telegram-bot?style=for-the-badge&color=gold)
![Python Version](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![VPS Deployment](https://img.shields.io/badge/VPS-Compatible-green?style=for-the-badge&logo=linux)

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif" width="500">

---

**A premium, high-performance Telegram Bot for Instagram, Music, and Universal Media Downloading.**

[Owner 👑](https://t.me/TechnicalSerena) | [Developer 💻](https://t.me/Xioqui_Xin) | [Support 🛠](https://t.me/TechnicalSerena)

</div>

---

## 🛠 Features & Capabilities

### 📸 Instagram Suite
- **Full Profile:** Download all posts, stories, and highlights.
- **HD Media:** High-definition Photos, Reels, and Carousel posts.
- **AI Captions:** Generate viral captions using Groq AI.

### 🎵 Music Engine
- **Search:** Use `#music <name>` in any chat or group.
- **High Quality:** 320kbps MP3 with embedded cover art and metadata.
- **Direct Play:** Seamless integration with Telegram's music player.

### 🎥 Universal Downloader
- **Supported Platforms:** YouTube, TikTok, Facebook, X, Reddit, Pinterest.
- **Batch Processing:** Download multiple links at once.
- **Smart Rename:** Auto-renaming flow for organized libraries.

---

## 📋 Commands Structure

| Command | Usage | Description |
| :--- | :--- | :--- |
| `/start` | `/start` | Initialize bot & check status |
| `/help` | `/help` | Detailed guide for all features |
| `/profile` | `/profile <username>` | Download full Insta profile |
| `#music` | `#music <song name>` | Fetch & play music in groups |
| `/dl` | `/dl <url>` | Universal link downloader |
| `/admin` | `/admin` | Admin control panel (Owners) |
| `/lock` | `/lock` | Restrict bot access |
| `/cookies` | `/cookies <data>` | Set Instagram session cookies |

---

## 🚀 Deployment Guide

### 🌐 VPS Deployment (Recommended)
1. **Update System:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
2. **Install Dependencies:**
   ```bash
   sudo apt install python3-pip ffmpeg git -y
   ```
3. **Clone & Setup:**
   ```bash
   git clone https://github.com/iamrita-ai/advanced-telegram-bot.git
   cd advanced-telegram-bot
   pip install -r requirements.txt
   ```
4. **Configure Environment:**
   ```bash
   cp .env.example .env
   nano .env
   ```
5. **Run with Screen (Persistent):**
   ```bash
   screen -S bot
   python3 main.py
   ```

### 🐳 Docker Deployment
```bash
docker build -t advanced-bot .
docker run -d --name mybot --env-file .env advanced-bot
```

### ☁️ Render Deployment
- Simply connect this repo to Render.
- Add your Environment Variables.
- The bot includes a built-in health check server on port `8080`.

---

## 📜 Credits & License
- **Founder:** [Technical Serena](https://t.me/TechnicalSerena)
- **Developer:** [Xioqui_Xin](https://t.me/Xioqui_Xin)
- **License:** [MIT License](LICENSE)

<div align="center">
  <b>Built with ❤️ for the Global Community</b>
</div>
