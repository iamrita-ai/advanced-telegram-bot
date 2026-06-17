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
                    # Run the async update in the event loop
                    asyncio.run_coroutine_threadsafe(
                        self.tracker.update_progress(message, current, total, filename),
                        asyncio.get_event_loop()
                    )

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
