import random
from pathlib import Path
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..utils.fingerprint import FingerprintManager

logger = get_logger("shadow_matrix")


class ShadowAccount:
    def __init__(self, name, role, profile_dir):
        self.name = name
        self.role = role
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.fingerprint = FingerprintManager(self.profile_dir)
        self.last_active = None
        self.action_count = 0

    async def login(self):
        logger.info(f"Shadow account '{self.name}' logging in")
        return True

    async def logout(self):
        logger.info(f"Shadow account '{self.name}' logging out")

    async def perform_action(self, action_type, target=None):
        self.action_count += 1
        self.last_active = datetime.now()
        logger.info(f"Shadow '{self.name}' -> {action_type}")
        return True


class ShadowMatrix:
    def __init__(self, profiles_dir=None):
        self.profiles_dir = Path(profiles_dir) if profiles_dir else (
            Path(__file__).parent.parent / "browser_profiles"
        )
        self.accounts = {}
        self.coordination_log = []
        self._init_accounts()

    def _init_accounts(self):
        self.accounts["primary"] = ShadowAccount(
            "Agency Page", "official", self.profiles_dir / "primary"
        )
        self.accounts["shadow_1"] = ShadowAccount(
            "Dev Persona", "technical_authority", self.profiles_dir / "shadow_1"
        )
        self.accounts["shadow_2"] = ShadowAccount(
            "Past Client", "social_proof", self.profiles_dir / "shadow_2"
        )
        logger.info("Shadow Matrix initialized: 3 accounts ready")

    async def coordinated_action(self, action_type, target, lead_data=None):
        self.coordination_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target,
        })

        if action_type == "pitch":
            return await self._coordinate_pitch(target, lead_data)
        elif action_type == "vouch_bomb":
            return await self._coordinate_vouch(target, lead_data)
        return await self.accounts["primary"].perform_action(action_type, target)

    async def _coordinate_pitch(self, target, lead_data):
        await self.accounts["primary"].perform_action("pitch", target)
        await self.accounts["shadow_1"].perform_action("comment_after_pitch", target)
        delay = random.randint(300, 900)
        await self.accounts["shadow_2"].perform_action("vouch", target)
        logger.info(f"Coordinated pitch complete for {target}")

    async def _coordinate_vouch(self, target, lead_data):
        await self.accounts["shadow_2"].perform_action("testimonial", target)
        await self.accounts["shadow_1"].perform_action("technical_endorsement", target)
        return True

    async def vouch_bomb(self, lead_name):
        await self._coordinate_vouch(lead_name, None)
        logger.info(f"Vouch bomb deployed on {lead_name}")

    def get_health_report(self):
        return {
            name: {
                "role": acc.role,
                "last_active": acc.last_active.isoformat() if acc.last_active else "never",
                "actions_today": acc.action_count,
            }
            for name, acc in self.accounts.items()
        }
