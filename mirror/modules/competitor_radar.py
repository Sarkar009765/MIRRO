import re
from datetime import datetime
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("competitor_radar")


class CompetitorRadar:
    competitor_patterns = [
        r"(I'?m|we'?re|am)\s+a\s+(web|app|full.?stack|freelance)\s*(developer|designer|engineer)",
        r"(hire|contact|DM)\s*me\s*(for|if)\s*(web|app|development)",
        r"(portfolio|work|samples)\s*(link|here|below|check)",
        r"\d+\s*(projects|clients)\s*(done|completed|delivered)",
        r"(cheap|affordable|low.?cost|budget.?friendly)\s*(web|app|development)",
    ]

    def __init__(self, lead_store=None):
        self.leads = lead_store
        self.detected = {}
        logger.info("Competitor Radar initialized")

    def scan_post(self, post_text, group_name, author_name=None):
        text_lower = post_text.lower()
        matches = []
        for pattern in self.competitor_patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)
                break

        if not matches:
            return None

        key = f"{author_name or 'unknown'}@{group_name}"
        if key not in self.detected:
            self.detected[key] = {
                "name": author_name or "Unknown",
                "group": group_name,
                "first_detected": datetime.now(),
                "last_active": datetime.now(),
                "pitch_count": 0,
                "patterns": [],
            }

        self.detected[key]["pitch_count"] += 1
        self.detected[key]["last_active"] = datetime.now()
        self.detected[key]["patterns"].extend(matches)

        return self.detected[key]

    def get_competitor_summary(self):
        return list(self.detected.values())

    def get_aggressive_competitors(self, threshold=5):
        return [
            c for c in self.detected.values()
            if c["pitch_count"] >= threshold
        ]

    def extract_pricing(self, text):
        patterns = [
            r'(starting|from|only|just)\s*\$?(\d[\d,]*)\s*(taka|tk|bdt)?',
            r'(\d[\d,]*)\s*(taka|tk|bdt)\s*(per|for|only)',
            r'(price|cost|rate|charge)\s*:?\s*\$?(\d[\d,]*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def get_differentiation_suggestions(self):
        return [
            "Focus on post-delivery support (many competitors don't offer this)",
            "Highlight transparent pricing with no hidden costs",
            "Emphasize local availability and Bengali language support",
            "Offer free consultation call — differentiator from low-cost providers",
            "Showcase complex projects to position as premium not cheap",
        ]

    def reset(self):
        self.detected = {}
        logger.info("Competitor radar data reset")
