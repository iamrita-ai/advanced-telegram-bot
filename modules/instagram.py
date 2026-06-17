import instaloader
import os
import asyncio

class InstagramDownloader:
    def __init__(self, cookies_path='cookies.txt'):
        self.loader = instaloader.Instaloader()
        self.cookies_path = cookies_path
        self.load_cookies()

    def load_cookies(self):
        if os.path.exists(self.cookies_path):
            try:
                self.loader.load_session_from_file('insta_user', filename=self.cookies_path)
                print("✅ Instagram cookies loaded.")
            except Exception as e:
                print(f"❌ Error loading cookies: {e}")

    def save_cookies(self, cookie_data):
        # Save raw cookie data to file
        with open(self.cookies_path, 'w') as f:
            f.write(cookie_data)
        # Reload after saving
        self.load_cookies()

    async def download_profile(self, username, message):
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            await message.edit_text(f"📸 <b>Profile:</b> {profile.full_name}\n🚀 <b>Followers:</b> {profile.followers}\n📦 <b>Posts:</b> {profile.mediacount}", parse_mode='HTML')
            # Add more download logic here
        except Exception as e:
            await message.edit_text(f"❌ Error: {str(e)}")
