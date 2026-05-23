import os
import httpx
from ..utils.logger import get_logger

logger = get_logger("api.openrouter")


class OpenRouterPlugin:
    name = "openrouter"
    free_tier = 50
    requires_key = True
    quota_used = 0

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "mistralai/mixtral-8x22b-instruct"

    async def generate(self, prompt, context=None, system_instruction=None):
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")
            return None

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        elif context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                data = resp.json()
                if resp.status_code == 200:
                    self.quota_used += 1
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"OpenRouter API error: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"OpenRouter request failed: {e}")
            return None
