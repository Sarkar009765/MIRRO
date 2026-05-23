import random
from pathlib import Path
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.spintax import SpintaxEngine

logger = get_logger("ghost_writer")


class GhostWriter:
    def __init__(self, api_aggregator=None, dna_profile=None, templates_dir=None):
        self.api = api_aggregator
        self.templates_dir = Path(templates_dir) if templates_dir else (
            Path(__file__).parent.parent / "templates"
        )
        self.spintax = SpintaxEngine(dna_profile)
        self.dna = dna_profile or {}
        self._template_cache = {}

    async def generate_response(self, lead_data, scenario="web_dev"):
        logger.info(f"Generating response for {lead_data.get('name', 'unknown')} [{scenario}]")

        template = self._select_template(scenario, lead_data)

        if template and self.api:
            try:
                context = self._build_context(lead_data)
                ai_response = await self.api.generate(template, context)
                if ai_response:
                    return self._post_process(ai_response, lead_data)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")

        processed = self.spintax.spin(template)
        processed = self.spintax.personalize(processed, lead_data)
        processed = self.spintax.add_dna_flavor(processed)
        return processed

    def _select_template(self, scenario, lead_data):
        template_path = self.templates_dir / scenario
        if not template_path.exists():
            template_path = self.templates_dir / "generic"
            if not template_path.exists():
                return self._fallback_response(lead_data)

        if "budget" in str(lead_data.get("detected_keywords", "")).lower():
            f = template_path / "budget_mentioned.txt"
        elif lead_data.get("urgency") == "High":
            f = template_path / "urgent_request.txt"
        elif lead_data.get("personality_type") == "Analytical":
            f = template_path / "vague_request.txt"
        else:
            candidates = list(template_path.glob("*.txt"))
            f = random.choice(candidates) if candidates else None

        if f and f.exists():
            return f.read_text(encoding="utf-8")
        return self._fallback_response(lead_data)

    def _build_context(self, lead_data):
        parts = []
        if lead_data.get("pain_points"):
            parts.append(f"Pain points: {', '.join(lead_data['pain_points'])}")
        if lead_data.get("budget_range"):
            parts.append(f"Budget: {lead_data['budget_range']}")
        if lead_data.get("personality_type"):
            parts.append(f"Personality: {lead_data['personality_type']}")
        if lead_data.get("preferred_tone"):
            parts.append(f"Preferred tone: {lead_data['preferred_tone']}")
        return "\n".join(parts)

    def _post_process(self, text, lead_data):
        text = self.spintax.spin(text)
        text = self.spintax.personalize(text, lead_data)
        text = self.spintax.add_dna_flavor(text)
        return text

    def _fallback_response(self, lead_data):
        name = lead_data.get("name", "Bhai")
        return (
            f"{name}, apnar project type ta ki? Amra full-stack web solution "
            f"provide kori — React, Node.js, Laravel, WordPress — jai laguk na keno. "
            f"Portfolio dekhte chan? DM koren details boli."
        )

    async def generate_follow_up(self, lead_data, step=1):
        scenarios = {
            1: f"Bhai, project ta kemon gelo? Kono help lagle janaben.",
            2: f"Vai, just ekbar portfolio ta dekhen — https://mirror.showcase.dev",
            3: f"Bhaijaan, current e amra special offer chalachi. Interested?",
        }
        return scenarios.get(step, scenarios[1])

    def load_templates(self):
        self._template_cache = {}
        for category_dir in self.templates_dir.iterdir():
            if category_dir.is_dir():
                for f in category_dir.glob("*.txt"):
                    key = f"{category_dir.name}/{f.stem}"
                    self._template_cache[key] = f.read_text(encoding="utf-8")
        return self._template_cache
