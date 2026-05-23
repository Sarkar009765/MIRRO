from datetime import datetime, timedelta
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("nurture_loop")


class NurtureLoop:
    nurture_sequence = {
        0: {"day": 0, "action": "initial_pitch", "channel": "comment"},
        1: {"day": 3, "action": "helpful_group_post", "channel": "group_post"},
        2: {"day": 5, "action": "comment_on_non_business_post", "channel": "comment"},
        3: {"day": 7, "action": "share_relevant_article", "channel": "group_post"},
        4: {"day": 10, "action": "soft_re_engage", "channel": "dm"},
        5: {"day": 14, "action": "final_check_in", "channel": "dm"},
        6: {"day": 30, "action": "monthly_touch", "channel": "group_interaction"},
    }

    def __init__(self, lead_store=None, nurture_store=None, ghost_writer=None):
        self.leads = lead_store
        self.nurture = nurture_store
        self.writer = ghost_writer
        self.engaged_leads = {}

    async def process_pending(self):
        if not self.nurture:
            logger.info("Nurture store not available, skipping")
            return []

        pending = self.nurture.get_pending()
        results = []
        for action in pending:
            try:
                result = await self._execute_action(action)
                self.nurture.mark_done(action["id"])
                results.append(result)
            except Exception as e:
                logger.error(f"Nurture action {action['id']} failed: {e}")
        return results

    async def _execute_action(self, action):
        logger.info(f"Executing nurture action {action['id']} step {action['step']}")
        return {"action_id": action["id"], "status": "executed"}

    def start_nurture(self, lead_id, lead_name, interaction_date=None):
        start = interaction_date or datetime.now()
        for step, seq in self.nurture_sequence.items():
            if step == 0:
                continue
            scheduled = start + timedelta(days=seq["day"])
            self.nurture.schedule(lead_id, step, seq["action"], scheduled)
        logger.info(f"Nurture sequence started for lead {lead_id}")

    def get_sequence(self, step):
        return self.nurture_sequence.get(step)

    def is_active(self, lead_id):
        return lead_id in self.engaged_leads

    def track_engagement(self, lead_id, action):
        if lead_id not in self.engaged_leads:
            self.engaged_leads[lead_id] = {"actions": [], "current_step": 0}
        self.engaged_leads[lead_id]["actions"].append(action)
        logger.info(f"Lead {lead_id} engaged: {action}")

    def get_status(self, lead_id):
        data = self.engaged_leads.get(lead_id)
        if not data:
            return {"status": "not_in_nurture"}
        return {
            "actions_taken": len(data["actions"]),
            "current_step": data["current_step"],
        }
