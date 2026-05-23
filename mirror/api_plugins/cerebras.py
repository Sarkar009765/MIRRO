import os
import httpx
from ..utils.logger import get_logger

logger = get_logger("api.cerebras")


class CerebrasPlugin:
    name = "cerebras"
    free_tier = 1_000_000
    requires_key = True
    quota_used = 0

    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY", "")
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"

    async def generate(self, prompt, context=None, system_instruction=None):
        if not self.api_key:
            logger.warning("Cerebras API key not configured")
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
        payload = {"model": "claude-3-haiku", "messages": messages, "temperature": 0.7}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                data = resp.json()
                if resp.status_code == 200:
                    self.quota_used += 1
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"Cerebras API error: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"Cerebras request failed: {e}")
            return None
