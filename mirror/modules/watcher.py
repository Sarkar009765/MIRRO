import re
import json
from datetime import datetime
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("watcher")


class Watcher:
    high_priority = [
        r"need\s*(a\s*)?(website|web\s*site|webpage)",
        r"(website|web\s*site)\s*(lagbe|chai|dorkar|darker)",
        r"web\s*developer\s*(chai|lagbe|needed|required)",
        r"(app|application|software)\s*(lagbe|chai|dorkar|needed|required)",
        r"(mobile\s*app|android\s*app|ios\s*app)\s*(lagbe|chai|dorkar)",
        r"(ecommerce|e-commerce|online\s*shop|business\s*website)",
        r"(full\s*stack|mern|react\s*developer|next\.?js)",
    ]

    medium_priority = [
        r"(developer|freelancer|programmer)\s*(chai|lagbe|needed|required)",
        r"(outsource|hire|find)\s*(developer|freelancer|team)",
        r"(bug\s*fix|website\s*repair|maintenance)",
        r"(redesign|revamp|update|rebuild)\s*(website|site|app)",
    ]

    budget_indicators = [
        r"(budget|taka|tk|price|cost|rate)",
        r"\d+\s*(k|tk|taka|lakh|lac)",
    ]

    urgency_signals = [
        r"(urgent|asap|immediately|emergency)",
        r"(tomorrow|this\s*week|fast\s*delivery|quick\s*turnaround)",
    ]

    def __init__(self, lead_store=None, api_aggregator=None, groups=None):
        self.leads = lead_store
        self.api = api_aggregator
        self.groups = groups or []
        self.processed_posts = set()
        logger.info(f"Watcher initialized with {len(self.groups)} groups")

    def set_groups(self, groups):
        self.groups = groups
        logger.info(f"Watcher groups updated: {len(groups)} total")

    async def scan_groups(self):
        logger.info("Starting group scan cycle")
        found = []
        for group in self.groups:
            posts = await self._fetch_group_posts(group)
            for post in posts:
                if post.get("id") in self.processed_posts:
                    continue
                score = self._score_post(post)
                if score > 0:
                    post["hotness_score"] = score
                    found.append(post)
                    self.processed_posts.add(post.get("id"))

        logger.info(f"Scan complete: {len(found)} potential leads found")

        for post in found:
            self._process_lead(post)

        return found

    async def _fetch_group_posts(self, group):
        return []

    def _score_post(self, post):
        text = (post.get("text") or "").lower()
        score = 0

        for pattern in self.high_priority:
            if re.search(pattern, text, re.IGNORECASE):
                score += 30
                post["matched_keywords"] = re.findall(pattern, text, re.IGNORECASE)
                break

        for pattern in self.medium_priority:
            if re.search(pattern, text, re.IGNORECASE):
                score += 15
                break

        for pattern in self.budget_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                score += 10
                post["has_budget"] = True
                break

        for pattern in self.urgency_signals:
            if re.search(pattern, text, re.IGNORECASE):
                score += 5
                post["is_urgent"] = True
                break

        return score

    def _process_lead(self, post):
        if not self.leads:
            return

        lead_id = self.leads.insert(
            fb_id=post.get("id", f"post_{datetime.now().timestamp()}"),
            name=post.get("author"),
            group_name=post.get("group"),
            post_content=post.get("text"),
            detected_keywords=", ".join(post.get("matched_keywords", [])),
            hotness_score=post.get("hotness_score", 0),
        )

        sentiment = self._detect_sentiment(post.get("text", ""))
        if lead_id:
            self.leads.update(lead_id, sentiment=sentiment)

    def _detect_sentiment(self, text):
        text_lower = text.lower()
        positive = ["want", "need", "looking", "help", "recommendation", "suggest"]
        negative = ["urgent", "problem", "issue", "bug", "frustrated", "stuck"]
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    @classmethod
    def get_keyword_library(cls):
        return {
            "high": cls.high_priority,
            "medium": cls.medium_priority,
            "budget": cls.budget_indicators,
            "urgency": cls.urgency_signals,
        }
