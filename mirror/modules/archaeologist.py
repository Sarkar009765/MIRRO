import json
import re
from datetime import datetime
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("archaeologist")


class Archaeologist:
    def __init__(self, api_aggregator=None, lead_store=None):
        self.api = api_aggregator
        self.leads = lead_store

    async def investigate(self, lead_id, fb_profile_data=None):
        logger.info(f"Investigating lead {lead_id}")
        lead = self.leads.get_by_id(lead_id) if self.leads else None
        if not lead:
            return None

        report = self._build_report(lead, fb_profile_data)

        if self.leads:
            self.leads.update(lead_id, archaeology_report=json.dumps(
                report, ensure_ascii=False
            ))

        logger.info(f"Archaeology complete for lead {lead_id}: {report['personality_type']}")
        return report

    def _build_report(self, lead, fb_data=None):
        post_text = (lead.get("post_content") or "") + " " + (fb_data or {}).get("recent_posts", "")

        personality = self._detect_personality(post_text)
        budget = self._extract_budget(post_text)
        urgency = self._detect_urgency(post_text)
        pain_points = self._detect_pain_points(post_text)
        tone = self._detect_preferred_tone(personality)
        risk = self._detect_risk_factors(post_text)

        return {
            "lead_id": lead.get("fb_id"),
            "personality_type": personality,
            "budget_range": budget,
            "urgency": urgency,
            "pain_points": pain_points,
            "preferred_tone": tone,
            "active_hours": self._detect_active_hours(fb_data),
            "engagement_style": personality,
            "risk_factors": risk,
        }

    def _detect_personality(self, text):
        text_lower = text.lower()

        analytical_signals = ["how much", "compare", "details", "specific",
                              "features", "tech stack", "technology"]
        emotional_signals = ["frustrated", "tired", "hoping", "please help",
                             "desperate", "need badly"]
        rush_signals = ["urgent", "asap", "immediately", "right now",
                        "today", "tonight", "tomorrow"]
        cautious_signals = ["first time", "new to", "scared", "nervous",
                            "previous scam", "cheated", "scammed"]

        scores = {"Analytical": 0, "Emotional": 0, "Rush": 0, "Cautious": 0}

        for word in analytical_signals:
            if word in text_lower:
                scores["Analytical"] += 1
        for word in emotional_signals:
            if word in text_lower:
                scores["Emotional"] += 2
        for word in rush_signals:
            if word in text_lower:
                scores["Rush"] += 3
        for word in cautious_signals:
            if word in text_lower:
                scores["Cautious"] += 2

        return max(scores, key=scores.get) if any(scores.values()) else "Balanced"

    def _extract_budget(self, text):
        patterns = [
            r'(\d+[\s-]?\d*)\s*(k|tk|taka|hazard|hajjar)',  # 15k, 20tk
            r'(\d+)\s*(lakh|lac)',  # 1 lakh
            r'budget[:\s]*(\d[\d,\s]*)',  # budget: 15000
            r'(\d[\d,]*)\s*(taka|tk)',  # 15000 taka
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "Unknown"

    def _detect_urgency(self, text):
        urgent_signals = ["urgent", "asap", "immediately", "today",
                          "tomorrow", "this week", "fast", "quick",
                          "emergency", "right now", "need it fast"]
        text_lower = text.lower()
        count = sum(1 for s in urgent_signals if s in text_lower)
        if count >= 3:
            return "High"
        elif count >= 1:
            return "Medium"
        return "Low"

    def _detect_pain_points(self, text):
        pain_map = {
            "previous_dev_ghosted": ["ghosted", "disappeared", "vanished", "not responding"],
            "delayed_delivery": ["delay", "late", "overdue", "missed deadline"],
            "budget_issues": ["expensive", "overcharged", "over budget", "costly"],
            "quality_concerns": ["buggy", "not working", "poor quality", "bad code"],
            "communication_problems": ["not understanding", "language barrier", "confusion"],
        }
        found = []
        text_lower = text.lower()
        for pain, signals in pain_map.items():
            if any(s in text_lower for s in signals):
                found.append(pain)
        return found

    def _detect_preferred_tone(self, personality):
        tone_map = {
            "Analytical": "Professional with details",
            "Emotional": "Empathetic and reassuring",
            "Rush": "Direct and confident",
            "Cautious": "Gentle with guarantees",
            "Balanced": "Friendly and informative",
        }
        return tone_map.get(personality, "Friendly and informative")

    def _detect_active_hours(self, fb_data):
        if not fb_data:
            return "Not determined"
        return "19:00-22:00"

    def _detect_risk_factors(self, text):
        risks = []
        text_lower = text.lower()
        if any(w in text_lower for w in ["cheap", "low budget", "minimal budget"]):
            risks.append("mentioned_cheap_option")
        if any(w in text_lower for w in ["first time", "new to this", "no idea"]):
            risks.append("first_time_client")
        if any(w in text_lower for w in ["previous scam", "scammed", "cheated"]):
            risks.append("scammed_before")
        return risks
