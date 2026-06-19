import yt_dlp
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class MusicDownloader:
    def __init__(self, download_path='downloads/music'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    async def search_and_download(self, query, message):
        # We'll use yt-dlp with a more resilient configuration
        # If one search provider fails, we can try others (ytsearch, scsearch, etc.)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }, {
                'key': 'EmbedThumbnail',
            }, {
                'key': 'FFmpegMetadata',
            }],
            'writethumbnail': True,
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        
        # Try multiple search providers if the default fails
        search_queries = [f"ytsearch1:{query} song", f"scsearch1:{query} song"]
        
        for search_query in search_queries:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, search_query, download=True)
                    if 'entries' in info and len(info['entries']) > 0:
                        entry = info['entries'][0]
                        file_path = ydl.prepare_filename(entry).replace(entry['ext'], 'mp3')
                        
                        # Handle potential filename mismatches
                        if not os.path.exists(file_path):
                            base = os.path.splitext(ydl.prepare_filename(entry))[0]
                            for f in os.listdir(self.download_path):
                                if os.path.join(self.download_path, f).startswith(base) and f.endswith(".mp3"):
                                    file_path = os.path.join(self.download_path, f)
                                    break

                        if os.path.exists(file_path):
                            thumb_path = os.path.splitext(file_path)[0] + ".jpg"
                            thumb_file = None
                            if os.path.exists(thumb_path):
                                thumb_file = open(thumb_path, 'rb')
                            
                            await message.reply_audio(
                                audio=open(file_path, 'rb'),
                                title=entry.get('title'),
                                performer=entry.get('uploader'),
                                thumb=thumb_file,
                                caption=f"🎵 <b>{entry.get('title')}</b>\n✅ Downloaded successfully!",
                                parse_mode='HTML'
                            )
                            
                            if thumb_file: thumb_file.close()
                            # Cleanup
                            os.remove(file_path)
                            if os.path.exists(thumb_path): os.remove(thumb_path)
                            return # Success, exit the loop
            except Exception as e:
                logger.error(f"Search provider failed ({search_query}): {e}")
                continue # Try next provider

        await message.edit_text("❌ Failed to download music. This song might be restricted or unavailable. Try uploading fresh cookies.")
