import yt_dlp
import os

class MusicDownloader:
    def __init__(self, download_path='downloads/music'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    def search_and_download(self, query):
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
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=True)
            return info['entries']
