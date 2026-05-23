import random
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger("api.template")


class TemplateEngine:
    name = "template"
    free_tier = float("inf")
    requires_key = False
    quota_used = 0

    def __init__(self, templates_dir=None):
        self.templates_dir = Path(templates_dir) if templates_dir else (
            Path(__file__).parent.parent / "templates"
        )
        self._template_cache = {}
        self._load_templates()

    def _load_templates(self):
        if not self.templates_dir.exists():
            return
        for category_dir in self.templates_dir.iterdir():
            if category_dir.is_dir():
                for f in category_dir.glob("*.txt"):
                    key = f"{category_dir.name}/{f.stem}"
                    self._template_cache[key] = f.read_text(encoding="utf-8")

    async def generate(self, prompt, context=None, system_instruction=None):
        text = self._fallback_generate(prompt, context)
        logger.info(f"Template engine used: {len(text)} chars")
        return text

    def _fallback_generate(self, prompt, context=None):
        responses = [
            "Bhai, apnar project ta ki type? Amra full-stack web solution provide kori.",
            "Ektu details dile ami exact quotation dite parbo. Ki lagbe apnar?",
            "Amader portfolio dekhen: past clients der jonno similar project korsi.",
            "Bhai, DM koren — details discuss kore scope final kori.",
            "Amar ekta similar project chilo last month. Quality and timing — dutoi best.",
        ]
        return random.choice(responses)

    def get_template(self, path_key):
        return self._template_cache.get(path_key)

    def all_templates(self):
        return list(self._template_cache.keys())
