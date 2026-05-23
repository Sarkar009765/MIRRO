import random
import re


class SpintaxEngine:
    def __init__(self, dna_profile=None):
        self.dna = dna_profile or {}
        self._cache = {}

    def spin(self, text):
        pattern = r"\{([^{}]+)\}"
        while "{" in text:
            text = re.sub(pattern, self._pick_variant, text)
        return text

    def _pick_variant(self, match):
        variants = [v.strip() for v in match.group(1).split("|")]
        return random.choice(variants)

    def personalize(self, text, lead_data=None):
        result = text
        if lead_data:
            placeholders = {
                "{name}": lead_data.get("name", "Bhai"),
                "{project_type}": lead_data.get("project_type", "web"),
                "{budget_range}": lead_data.get("budget_range", "reasonable"),
                "{pain_point}": self._select_pain_point(lead_data),
                "{timeline}": lead_data.get("timeline", "discuss"),
            }
            for key, val in placeholders.items():
                result = result.replace(key, val)
        return result

    def _select_pain_point(self, lead_data):
        points = lead_data.get("pain_points", [])
        if not points:
            return "quality solution"
        return random.choice(points)

    def add_dna_flavor(self, text):
        if not self.dna:
            return text
        vocab = self.dna.get("vocabulary", {})
        tone = self.dna.get("tone_markers", {})

        greetings = tone.get("greeting", ["Bhai"])
        closings = tone.get("closing", ["Thanks bhai"])

        if random.random() < 0.3:
            text = f"{random.choice(greetings)}, {text}"
        if random.random() < 0.2:
            text = f"{text}\n\n{random.choice(closings)}"

        fillers = vocab.get("fillers", [])
        for filler in fillers:
            if random.random() < 0.15 and len(text) > 30:
                insert_point = random.randint(len(text) // 3, len(text) // 2)
                text = text[:insert_point] + f" {filler}," + text[insert_point:]

        return text
