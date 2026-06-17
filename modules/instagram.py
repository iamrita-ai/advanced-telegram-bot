import instaloader
import os
import time

class InstagramDownloader:
    def __init__(self, cookies_path=None):
        self.loader = instaloader.Instaloader()
        if cookies_path and os.path.exists(cookies_path):
            try:
                self.loader.load_session_from_file(cookies_path)
            except Exception as e:
                print(f"Error loading cookies: {e}")

    async def download_profile(self, username, progress_callback):
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            # Implement logic to download posts, stories, etc.
            # Use progress_callback to update the user in Telegram
            pass
        except Exception as e:
            return f"Error: {str(e)}"

    def get_progress_string(self, current, total, speed, eta):
        percent = (current / total) * 100
        return f"Done: {current}/{total} MB | Speed: {speed} MB/s | ETA: {eta}s"
