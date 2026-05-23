import os
import httpx
from ..utils.logger import get_logger

logger = get_logger("api.cloudflare")


class CloudflarePlugin:
    name = "cloudflare"
    free_tier = 10000
    requires_key = True
    quota_used = 0

    def __init__(self):
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"

    async def generate(self, prompt, context=None, system_instruction=None):
        if not self.api_token or not self.account_id:
            logger.warning("Cloudflare API credentials not configured")
            return None

        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"prompt": prompt}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.base_url}/@cf/mistral/mistral-7b-instruct-v0.1",
                    json=payload, headers=headers
                )
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    self.quota_used += 1
                    return data["result"]["response"]
                logger.warning(f"Cloudflare API error: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"Cloudflare request failed: {e}")
            return None
