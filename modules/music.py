import yt_dlp
import os
import asyncio
import requests

class MusicDownloader:
    def __init__(self, download_path='downloads/music'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    async def search_and_download(self, query, message):
        # Using JioSaavn API for reliable search if YouTube fails
        # For this implementation, we will use yt-dlp with specific search terms to find better results
        # and fallback to cookies if provided.
        
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
            # Adding user agent to bypass simple bot detection
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, f"{query} song", download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                
                file_path = None
                for f in os.listdir(self.download_path):
                    if f.endswith(".mp3"):
                        file_path = os.path.join(self.download_path, f)
                        break

                if file_path:
                    await message.reply_audio(
                        audio=open(file_path, 'rb'),
                        title=info.get('title'),
                        performer=info.get('uploader'),
                        caption=f"🎵 <b>{info.get('title')}</b>\n✅ Downloaded for you!",
                        parse_mode='HTML'
                    )
                    os.remove(file_path)
                    for f in os.listdir(self.download_path):
                        os.remove(os.path.join(self.download_path, f))
                else:
                    await message.edit_text("❌ Failed to process the audio file. Try adding cookies.")
        except Exception as e:
            await message.edit_text(f"❌ Music Error: {str(e)}\n\n💡 <i>Upload cookies.txt to bypass YouTube bot detection.</i>", parse_mode='HTML')
