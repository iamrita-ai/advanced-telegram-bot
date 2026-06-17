import yt_dlp
import os
import asyncio
import logging
from utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

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
        
        logger.info(f"[DL] Starting download for URL: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("[YT-DLP] Extracting info...")
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                file_path = ydl.prepare_filename(info)
                
                # yt-dlp might change extension (e.g. .webm to .mp4)
                if not os.path.exists(file_path):
                    base_path = os.path.splitext(file_path)[0]
                    for f in os.listdir(self.download_path):
                        if os.path.join(self.download_path, f).startswith(base_path):
                            file_path = os.path.join(self.download_path, f)
                            break

                if os.path.exists(file_path):
                    logger.info(f"[SEND] Sending file: {file_path}")
                    await message.reply_video(
                        video=open(file_path, 'rb'), 
                        caption=f"✅ Downloaded: {info.get('title')}",
                        supports_streaming=True
                    )
                    os.remove(file_path)
                    logger.info(f"[DL] Task completed and file removed.")
                else:
                    logger.error(f"[DL] File not found after download: {file_path}")
                    await message.edit_text("❌ Download failed: File not found.")
        except Exception as e:
            logger.error(f"[DL] Error occurred: {str(e)}")
            await message.edit_text(f"❌ Error: {str(e)}")
