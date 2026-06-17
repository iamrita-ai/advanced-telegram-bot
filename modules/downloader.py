import yt_dlp
import os
import asyncio
from utils.progress import ProgressTracker

class UniversalDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        self.tracker = ProgressTracker()

    async def download(self, url, message):
        def progress_hook(d):
            if d['status'] == 'downloading':
                current = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                filename = d.get('filename', 'Unknown')
                if total > 0:
                    asyncio.run_coroutine_threadsafe(
                        self.tracker.update_progress(message, current, total, filename),
                        asyncio.get_event_loop()
                    )

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                file_path = ydl.prepare_filename(info)
                await message.reply_video(video=open(file_path, 'rb'), caption=f"✅ Downloaded: {info.get('title')}")
                os.remove(file_path)
        except Exception as e:
            await message.edit_text(f"❌ Error: {str(e)}")
