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
        loop = asyncio.get_running_loop()

        def progress_hook(d):
            if d['status'] == 'downloading':
                current = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                filename = d.get('filename', 'Unknown')
                if total > 0:
                    # Use call_soon_threadsafe to schedule the async update safely
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(self.tracker.update_progress(message, current, total, filename))
                    )

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'quiet': True,
            'extract_flat': False,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    await message.reply_video(video=open(file_path, 'rb'), caption=f"✅ Downloaded: {info.get('title')}")
                    os.remove(file_path)
                else:
                    await message.edit_text("❌ Download failed: File not found.")
        except Exception as e:
            await message.edit_text(f"❌ Error: {str(e)}")
