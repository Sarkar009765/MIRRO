import os
import httpx
from ..utils.logger import get_logger

logger = get_logger("api.github")


class GitHubModelsPlugin:
    name = "github_models"
    free_tier = 50
    requires_key = True
    quota_used = 0

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://models.inference.ai.azure.com/chat/completions"

    async def generate(self, prompt, context=None, system_instruction=None):
        if not self.token:
            logger.warning("GitHub token not configured")
            return None

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        elif context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {"model": "gpt-4o-mini", "messages": messages}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                data = resp.json()
                if resp.status_code == 200:
                    self.quota_used += 1
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"GitHub Models API error: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"GitHub Models request failed: {e}")
            return None
