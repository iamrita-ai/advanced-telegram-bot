import os
from groq import Groq

class AICaptionGenerator:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.default_model = "llama-3.3-70b-versatile"

    def generate_caption(self, scene, mood, style, language, length, model=None):
        target_model = model or self.default_model
        prompt = f"""
        Generate an Instagram caption.
        Scene: {scene}
        Mood: {mood}
        Style: {style}
        Language: {language}
        Length: {length}
        """
        
        completion = self.client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "You are a professional social media manager."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            max_tokens=1024,
            top_p=1.0,
            stream=False
        )
        return completion.choices[0].message.content

    def analyze_media(self, file_path):
        # Media analysis logic
        return {
            "scene": "sunset beach",
            "mood": "peaceful",
            "objects": ["sea", "person"]
        }
