import yt_dlp
import os

class UniversalDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    def download(self, url, progress_callback):
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_callback],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def yt_dlp_callback(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        s = d.get('_speed_str', '0KB/s')
        e = d.get('_eta_str', '00:00')
        # This would be sent back to Telegram
        print(f"Downloading: {p} | Speed: {s} | ETA: {e}")
