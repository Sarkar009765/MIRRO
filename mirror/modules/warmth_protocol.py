import random
from datetime import datetime, timedelta
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("warmth_protocol")


class WarmthProtocol:
    def __init__(self, policy=None, lead_store=None):
        policy = policy or {}
        warmth = policy.get("warmth_protocol", {})
        self.phase1_days = warmth.get("phase1_days", 7)
        self.phase2_days = warmth.get("phase2_days", 7)
        self.min_warmth_pitch = warmth.get("min_warmth_score_pitch", 70)
        self.new_group_wait = warmth.get("new_group_wait_hours", 72)

        self.leads = lead_store
        self.scores = {}
        logger.info("Warmth Protocol initialized")

    async def process_group(self, group_name, member_count=0):
        score = self.scores.get(group_name, 0)
        phase = self._determine_phase(score)

        if phase == 1:
            return await self._phase1_action(group_name)
        elif phase == 2:
            return await self._phase2_action(group_name)
        elif phase == 3:
            return {"action": "ready_to_pitch", "group": group_name, "score": score}

        return {"action": "wait", "group": group_name, "reason": "too_early"}

    def _determine_phase(self, score):
        if score < 30:
            return 1
        elif score < self.min_warmth_pitch:
            return 2
        else:
            return 3

    async def _phase1_action(self, group_name):
        actions = [
            "answer_technical_question",
            "like_recent_posts",
            "share_experience",
            "congratulate_member",
        ]
        action = random.choice(actions)
        self._increase_score(group_name, random.randint(5, 15))
        logger.info(f"[Phase 1] {group_name} -> {action}")
        return {"action": action, "group": group_name, "phase": 1, "pitch": False}

    async def _phase2_action(self, group_name):
        actions = [
            "comment_with_advice",
            "share_relevant_experience",
            "help_with_technical_question",
            "engage_in_discussion",
        ]
        action = random.choice(actions)
        self._increase_score(group_name, random.randint(3, 10))
        logger.info(f"[Phase 2] {group_name} -> {action}")
        return {"action": action, "group": group_name, "phase": 2, "pitch": False}

    async def _phase3_action(self, group_name):
        return {"action": "pitch", "group": group_name, "phase": 3, "pitch": True}

    def _increase_score(self, group_name, amount):
        current = self.scores.get(group_name, 0)
        self.scores[group_name] = min(current + amount, 100)

    def get_score(self, group_name):
        return self.scores.get(group_name, 0)

    def get_all_scores(self):
        return dict(self.scores)

    def set_initial_score(self, group_name, score=0):
        self.scores[group_name] = score

    def can_pitch(self, group_name):
        return self.scores.get(group_name, 0) >= self.min_warmth_pitch

    def summary(self):
        return {
            "group_count": len(self.scores),
            "ready_to_pitch": sum(
                1 for s in self.scores.values() if s >= self.min_warmth_pitch
            ),
            "warming_up": sum(
                1 for s in self.scores.values() if 0 < s < self.min_warmth_pitch
            ),
            "new_groups": sum(1 for s in self.scores.values() if s == 0),
        }
