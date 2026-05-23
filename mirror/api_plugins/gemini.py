import os
import json
import httpx
from ..utils.logger import get_logger

logger = get_logger("api.gemini")


class GeminiPlugin:
    name = "gemini"
    free_tier = 1500
    requires_key = True
    quota_used = 0

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.0-flash"

    async def generate(self, prompt, context=None, system_instruction=None):
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return None

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": system_instruction}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {"contents": contents}
        if context:
            payload["systemInstruction"] = {"parts": [{"text": context}]}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=payload)
                data = resp.json()
                if resp.status_code == 200:
                    self.quota_used += 1
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info(f"Gemini response: {len(text)} chars")
                    return text
                else:
                    logger.warning(f"Gemini API error: {resp.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return None

    async def generate_with_fallback(self, prompt, context=None):
        result = await self.generate(prompt, context)
        return result
