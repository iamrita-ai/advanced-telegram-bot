import yt_dlp
import os
import asyncio
import logging
import requests
from utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

class UniversalDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        self.tracker = ProgressTracker()

    async def download(self, url, message, texts):
        loop = asyncio.get_running_loop()

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

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if not os.path.exists(file_path):
                    base = os.path.splitext(file_path)[0]
                    for f in os.listdir(self.download_path):
                        if os.path.join(self.download_path, f).startswith(base):
                            file_path = os.path.join(self.download_path, f)
                            break

                if os.path.exists(file_path):
                    return file_path, info
                else:
                    await message.edit_text("❌ Error: Media file not found.")
                    return None, None
        except Exception as e:
            await message.edit_text(f"❌ Error: {str(e)}\n\n💡 <i>Try uploading cookies.txt for Instagram links.</i>", parse_mode='HTML')
            return None, None

    async def send_media(self, message, file_path, info, caption):
        try:
            duration = info.get('duration')
            width = info.get('width')
            height = info.get('height')
            thumb_url = info.get('thumbnail')
            
            thumb_file = None
            thumb_path = None
            if thumb_url:
                try:
                    thumb_path = f"{file_path}_thumb.jpg"
                    r = requests.get(thumb_url, stream=True)
                    if r.status_code == 200:
                        with open(thumb_path, 'wb') as f:
                            for chunk in r: f.write(chunk)
                        thumb_file = open(thumb_path, 'rb')
                except:
                    thumb_file = None

            await message.reply_video(
                video=open(file_path, 'rb'),
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                thumbnail=thumb_file,
                supports_streaming=True,
                parse_mode='HTML'
            )
            
            if thumb_file:
                thumb_file.close()
                if os.path.exists(thumb_path): os.remove(thumb_path)
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error sending media: {e}")
            await message.reply_text(f"❌ Failed to send media: {str(e)}")
