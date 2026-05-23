import random
from datetime import datetime, time
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.humanizer import Humanizer

logger = get_logger("safety_guard")


class SafetyGuard:
    def __init__(self, config=None):
        cfg = config or {}
        self.action_budget = cfg.get("action_budget", {})
        self.behavioral = cfg.get("behavioral_mimicry", {})
        self.canary_cfg = cfg.get("canary", {})

        self.daily_actions = {"comments": 0, "posts": 0, "likes": 0, "dms": 0}
        self.group_action_counts = {}
        self.last_action_time = {}
        self._is_paused = False
        self._canary_status = "ok"

        self.humanizer = Humanizer(self.behavioral)
        logger.info("Safety Guard initialized")

    def can_perform_action(self, action_type, group_name=None):
        if self._is_paused:
            logger.warning("Action blocked: system paused")
            return False

        now = datetime.now()
        current_hour = now.hour
        is_weekend = now.weekday() >= 5

        if self.humanizer.should_take_break(current_hour, is_weekend):
            logger.info("Action blocked: break time")
            return False

        budget_limits = {
            "comment": ("comments", self.action_budget.get("max_daily_comments", 8)),
            "post": ("posts", self.action_budget.get("max_daily_posts", 2)),
            "like": ("likes", self.action_budget.get("max_daily_likes", 20)),
            "dm": ("dms", self.action_budget.get("max_daily_dms", 5)),
        }

        key, limit = budget_limits.get(action_type, (None, 0))
        if key and self.daily_actions.get(key, 0) >= limit:
            logger.warning(f"Daily {action_type} limit reached")
            return False

        if group_name:
            group_key = f"{group_name}:{action_type}"
            group_limit = self.action_budget.get("per_group_max_comments", 2)
            if self.group_action_counts.get(group_key, 0) >= group_limit:
                logger.warning(f"Group {group_name} {action_type} limit reached")
                return False

        if group_name:
            last_time = self.last_action_time.get(group_name)
            min_gap = self.action_budget.get("min_gap_between_actions_minutes", 120)
            if last_time and (now - last_time).total_seconds() < min_gap * 60:
                remaining = min_gap * 60 - (now - last_time).total_seconds()
                logger.info(f"Cooldown: {remaining:.0f}s remaining for {group_name}")
                return False

        return True

    def record_action(self, action_type, group_name=None):
        if action_type == "comment":
            self.daily_actions["comments"] += 1
        elif action_type == "post":
            self.daily_actions["posts"] += 1
        elif action_type == "like":
            self.daily_actions["likes"] += 1
        elif action_type == "dm":
            self.daily_actions["dms"] += 1

        if group_name:
            key = f"{group_name}:{action_type}"
            self.group_action_counts[key] = self.group_action_counts.get(key, 0) + 1
            self.last_action_time[group_name] = datetime.now()

    def pause_system(self, reason="admin_request"):
        self._is_paused = True
        logger.warning(f"System paused: {reason}")

    def resume_system(self):
        self._is_paused = False
        logger.info("System resumed")

    def canary_alert(self, restriction_type="unknown"):
        self._canary_status = f"restricted_{restriction_type}"
        if self.canary_cfg.get("pause_on_restriction", True):
            duration = self.canary_cfg.get("pause_duration_hours", 48)
            self.pause_system(f"canary_{restriction_type}")
            logger.warning(f"Canary alert: {restriction_type}, pausing {duration}h")

    def reset_daily_counters(self):
        self.daily_actions = {"comments": 0, "posts": 0, "likes": 0, "dms": 0}

    def safety_report(self):
        return {
            "paused": self._is_paused,
            "canary": self._canary_status,
            "actions_today": dict(self.daily_actions),
            "group_action_counts": dict(self.group_action_counts),
        }
