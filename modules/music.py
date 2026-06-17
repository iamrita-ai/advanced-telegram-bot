import yt_dlp
import os
import asyncio

class MusicDownloader:
    def __init__(self, download_path='downloads/music'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    async def search_and_download(self, query, message):
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
            # Use cookies if available to bypass bot detection
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                
                # Finding the generated mp3 file
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
                    # Clean up thumbnails
                    for f in os.listdir(self.download_path):
                        os.remove(os.path.join(self.download_path, f))
                else:
                    await message.edit_text("❌ Failed to process the audio file. Try using cookies.")
        except Exception as e:
            await message.edit_text(f"❌ Music Error: {str(e)}\n\n💡 <i>Try uploading your cookies.txt using /cookies</i>", parse_mode='HTML')
