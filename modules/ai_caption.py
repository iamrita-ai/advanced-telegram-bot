import os
import datetime
from groq import Groq
import logging

logger = logging.getLogger(__name__)

class AICaptionGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    async def generate_caption(self, media_info: dict, language: str = "English") -> str:
        # Build metadata-driven prompt
        title = media_info.get("title", "N/A")
        description = media_info.get("description", "N/A")
        tags = ", ".join(media_info.get("tags", [])) if media_info.get("tags") else "N/A"
        uploader = media_info.get("uploader", "N/A")
        uploader_url = media_info.get("uploader_url", "#")

        prompt = (
            f"Generate 5 short and creative Instagram captions in {language}.\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Tags: {tags}\n\n"
            "Return only the captions, one per line, starting with an emoji. Do not use checkmark emojis."
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            ai_output = completion.choices[0].message.content.strip()
            
            # IST Timestamp
            ist_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
            timestamp = ist_time.strftime("%d-%m-%Y %H:%M:%S IST")
            
            # Format final caption
            final_caption = (
                f"<b>Title</b> - {ai_output.split('\n')[0]}\n"
                f"<b>Creator</b> - <a href='{uploader_url}'>{uploader}</a>\n"
                f"<b>Time</b> - {timestamp}\n"
                f"<b>Download Through</b> - <a href='https://t.me/Insta_musicRena_bot'>Insta Music</a>"
            )
            return final_caption
        except Exception as e:
            logger.error(f"AI Caption Error: {e}")
            return f"<b>Title</b> - {title}\n<b>Time</b> - {timestamp}"
