import yt_dlp
import os
import asyncio
import logging
import requests
from utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

class MusicDownloader:
    def __init__(self, download_path='downloads/music'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        self.tracker = ProgressTracker()

    async def search_and_download(self, query, message):
        loop = asyncio.get_running_loop()
        
        # Determine language for texts
        from main import db, LANG_DATA
        user_lang = await db.get_user_lang(message.chat.id)
        texts = LANG_DATA.get(user_lang, LANG_DATA["English"])

        def progress_hook(d):
            if d['status'] == 'downloading':
                current = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                filename = os.path.basename(d.get('filename', 'Unknown'))
                if total > 0:
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(self.tracker.update_progress(message, current, total, filename, texts))
                    )
            elif d['status'] == 'finished':
                filename = os.path.basename(d.get('filename', 'Unknown'))
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.tracker.update_progress(message, 0, 0, filename, texts, is_done=True))
                )

        # Use YouTube specific cookies for music search
        cookie_file = 'cookies_youtube.txt' if os.path.exists('cookies_youtube.txt') else ('cookies.txt' if os.path.exists('cookies.txt') else None)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'cookiefile': cookie_file,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }

        search_queries = [f"ytsearch1:{query} song", f"scsearch1:{query} song"]
        
        for search_query in search_queries:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, search_query, download=True)
                    if 'entries' in info and len(info['entries']) > 0:
                        entry = info['entries'][0]
                        file_path = ydl.prepare_filename(entry).replace(entry['ext'], 'mp3')
                        
                        if not os.path.exists(file_path):
                            base = os.path.splitext(ydl.prepare_filename(entry))[0]
                            for f in os.listdir(self.download_path):
                                if os.path.join(self.download_path, f).startswith(base) and f.endswith(".mp3"):
                                    file_path = os.path.join(self.download_path, f)
                                    break

                        if os.path.exists(file_path):
                            thumb_url = entry.get('thumbnail')
                            thumb_path = None
                            if thumb_url:
                                try:
                                    thumb_path = f"{file_path}_thumb.jpg"
                                    r = requests.get(thumb_url, stream=True)
                                    if r.status_code == 200:
                                        with open(thumb_path, 'wb') as f:
                                            for chunk in r: f.write(chunk)
                                except:
                                    thumb_path = None

                            await message.reply_audio(
                                audio=open(file_path, 'rb'),
                                title=entry.get('title'),
                                performer=entry.get('uploader'),
                                thumbnail=open(thumb_path, 'rb') if thumb_path else None,
                                caption=f"🎵 <b>{entry.get('title')}</b>\n👤 <b>{entry.get('uploader')}</b>",
                                parse_mode='HTML'
                            )
                            
                            os.remove(file_path)
                            if thumb_path: os.remove(thumb_path)
                            return
            except Exception as e:
                logger.error(f"Search provider failed ({search_query}): {e}")
                continue

        await message.edit_text("❌ Failed to download music. This song might be restricted or unavailable. Try uploading fresh cookies.")
