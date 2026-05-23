import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("portfolio_sniping")


class PortfolioSniping:
    def __init__(self, portfolio_dir=None):
        self.portfolio_dir = Path(portfolio_dir) if portfolio_dir else (
            Path(__file__).parent.parent / "portfolio"
        )
        self.projects = self._load_projects()
        self._showcases = {}
        logger.info(f"Portfolio Sniping loaded: {len(self.projects)} projects")

    def _load_projects(self):
        projects_file = self.portfolio_dir / "projects.json"
        if projects_file.exists():
            with open(projects_file, encoding="utf-8") as f:
                return json.load(f)
        return []

    def match_projects(self, lead_keywords, max_results=3):
        if not self.projects:
            return []

        scored = []
        for project in self.projects:
            score = 0
            tags = [t.lower() for t in project.get("tags", [])]
            for keyword in lead_keywords:
                kw = keyword.lower()
                if kw in tags:
                    score += 10
                if kw in project.get("title", "").lower():
                    score += 5
                if kw in project.get("description", "").lower():
                    score += 3
            if score > 0:
                scored.append((score, project))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:max_results]]

    def generate_showcase(self, lead_id, lead_name, project_type, matched_projects=None):
        matched = matched_projects or self.match_projects([project_type])
        if not matched:
            return self._fallback_showcase(lead_name)

        showcase_id = f"showcase_{lead_id}_{int(datetime.now().timestamp())}"
        expiry = datetime.now() + timedelta(days=7)

        showcase = {
            "id": showcase_id,
            "lead_name": lead_name,
            "project_type": project_type,
            "projects": matched,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiry.isoformat(),
            "url": f"/showcase/{showcase_id}",
        }

        self._showcases[showcase_id] = showcase
        logger.info(f"Showcase generated: {showcase_id} for {lead_name}")
        return showcase

    def _fallback_showcase(self, lead_name):
        return {
            "id": f"fallback_{int(datetime.now().timestamp())}",
            "lead_name": lead_name,
            "message": f"{lead_name}, amader portfolio te onek similar project ache. DM kore details nite paren.",
            "url": None,
        }

    def is_showcase_expired(self, showcase_id):
        showcase = self._showcases.get(showcase_id)
        if not showcase:
            return True
        expiry = datetime.fromisoformat(showcase["expires_at"])
        return datetime.now() > expiry

    def get_showcase_url(self, lead_id):
        for sid, showcase in self._showcases.items():
            if str(lead_id) in sid and not self.is_showcase_expired(sid):
                return showcase["url"]
        return None

    def cleanup_expired(self):
        expired = [sid for sid in self._showcases if self.is_showcase_expired(sid)]
        for sid in expired:
            del self._showcases[sid]
        logger.info(f"Cleaned up {len(expired)} expired showcases")
