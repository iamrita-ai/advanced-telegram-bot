import os
import datetime
from groq import Groq
import logging

logger = logging.getLogger(__name__)

class AICaptionGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]

    async def generate_caption(self, media_info: dict, style: str = "normal", language: str = "English") -> str:
        prompt = self._build_prompt(media_info, style, language)
        try:
            completion = self.client.chat.completions.create(
                model=self.models[0], # Use the versatile model by default
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
                top_p=1,
                stream=False,
                stop=None
            )
            caption = completion.choices[0].message.content.strip()
            # Remove checkmark emojis as requested
            caption = caption.replace("✅", "").strip()
            
            # Add IST timestamp
            ist_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
            timestamp = ist_time.strftime("%d-%m-%Y %H:%M:%S IST")
            
            return f"{caption}\n\n<small>Generated at {timestamp}</small>"
        except Exception as e:
            logger.error(f"Error generating AI caption: {e}")
            return f"Failed to generate caption: {e}"

    def _build_prompt(self, media_info: dict, style: str, language: str) -> str:
        # Example media_info: {"scene":"sunset beach", "mood":"peaceful", "objects":["sea","person"], "text":""}
        
        prompt_parts = [
            f"Generate an Instagram caption in {language} language."
        ]

        if media_info.get("mood"): prompt_parts.append(f"Mood: {media_info["mood"]}.")
        if media_info.get("scene"): prompt_parts.append(f"Scene: {media_info["scene"]}.")
        if media_info.get("objects"): prompt_parts.append(f"Objects: {", ".join(media_info["objects"])}.")
        if media_info.get("text"): prompt_parts.append(f"Text detected: \"{media_info["text"]}\".")
        
        prompt_parts.append(f"Style: {style}.")
        prompt_parts.append("Length: short.")
        prompt_parts.append("Ensure no checkmark emojis are used.")

        return " ".join(prompt_parts)
