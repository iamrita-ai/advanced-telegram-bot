<div align="center">

# 🌟 Advanced Multi-Media Bot 🌟
### Powered by Technical Serena & Groq AI

![GitHub License](https://img.shields.io/github/license/iamrita-ai/advanced-telegram-bot?style=for-the-badge)
![GitHub Stars](https://img.shields.io/github/stars/iamrita-ai/advanced-telegram-bot?style=for-the-badge)
![Python Version](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eXJ6eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxx669K876g/giphy.gif" width="400">

---

**A premium, high-performance Telegram Bot for Instagram, Music, and Universal Media Downloading.**

[Owner 👑](https://t.me/TechnicalSerena) | [Developer 💻](https://t.me/Xioqui_Xin) | [Support 🛠](https://t.me/TechnicalSerena)

</div>

---

## ✨ Features

### 📸 Instagram Mastery
- **Profile:** Download all posts, stories, and highlights.
- **Media:** HD Photos, Reels, and Carousel posts.
- **Metadata:** Extracts captions, likes, and views.

### 🎵 Music on Demand
- **Search:** Use `#music <name>` to find any track.
- **Quality:** High-quality MP3 with embedded cover art.
- **Controls:** Play directly in Telegram with metadata tags.

### 🎥 Universal Downloader
- Supports **YouTube, TikTok, Facebook, X, Reddit, Pinterest**.
- Batch download support with renaming flow.

### 🤖 AI Magic (Groq)
- **Caption Gen:** AI-powered captions for your media.
- **Analysis:** Scene, mood, and object detection.

---

## 🚀 Deployment

### 1. Environment Setup
Create a `.env` file based on `.env.example`:
```env
BOT_TOKEN=your_token
OWNER_IDS=id1,id2
LOG_CHANNEL_ID=-100...
MONGODB_URI=mongodb+srv://...
GROQ_API_KEY=gsk_...
FORCE_SUB_CHANNEL=@TechnicalSerena
```

### 2. Docker (Recommended)
```bash
docker build -t advanced-bot .
docker run -p 8080:8080 --env-file .env advanced-bot
```

### 3. Render Deployment
- Connect your GitHub.
- Set **Environment Variables**.
- Render will automatically detect the **Dockerfile** and start the health check server on port `8080`.

---

## 🛠 Admin Panel
Access via `/admin` (Owners only):
- 📊 **Analytics:** Daily users & system metrics.
- 📢 **Broadcast:** Send messages to all users.
- 🚫 **Ban:** Manage access control.

---

## 📜 Credits
- **Owner/Founder:** [Technical Serena](https://t.me/TechnicalSerena)
- **Developer:** [Xioqui_Xin](https://t.me/Xioqui_Xin)

<div align="center">
  Made with ❤️ for the Community
</div>
