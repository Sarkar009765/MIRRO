import json
import re
from collections import Counter
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger("dna_cloner")


class DNACloner:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else (
            Path(__file__).parent.parent / "config"
        )
        self.profile_path = self.config_dir / "dna_profile.json"
        self.profile = self._load_or_default()

    def _load_or_default(self):
        if self.profile_path.exists():
            with open(self.profile_path, encoding="utf-8") as f:
                return json.load(f)
        return self._default_profile()

    def _default_profile(self):
        return {
            "vocabulary": {"top_words": [], "slang": [], "fillers": []},
            "structure": {"avg_sentence_length": 12, "question_ratio": 0.3,
                          "paragraph_count": 1},
            "style": {"emoji_frequency": 0.1, "emoji_top": [],
                      "formality_score": 5, "banglish_ratio": 0.5},
            "tone_markers": {"greeting": ["Bhai"], "closing": ["Thanks bhai"]},
        }

    def save(self):
        self.profile_path.write_text(
            json.dumps(self.profile, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.info(f"DNA profile saved to {self.profile_path}")

    def extract_from_fb_data(self, fb_export_path):
        fb_path = Path(fb_export_path)
        all_texts = []

        for f in fb_path.rglob("*.html"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            comments = re.findall(r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</div>',
                                  text, re.DOTALL)
            all_texts.extend(comments)

        self._analyze_texts(all_texts)
        self.save()
        logger.info(f"DNA cloned from {len(all_texts)} comments")

    def _analyze_texts(self, texts):
        words = []
        sentences = []
        emojis = []
        banglish_count = 0

        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0\u2764-\U0000FE0F]+",
            re.UNICODE
        )

        for t in texts:
            t = t.strip()
            if not t:
                continue
            sentences.append(t)
            words.extend(t.split())

            emojis.extend(emoji_pattern.findall(t))

            has_bangla = bool(re.search(r'[\u0980-\u09FF]', t))
            if has_bangla:
                banglish_count += 1

        if not sentences:
            return

        word_counts = Counter(w.lower().strip(",.!?") for w in words)
        filler_words = {"ar ki", "taile", "hmm", "actually", "basically",
                        "mane", "mtlb", "to be honest", "accha", "thik ace"}

        self.profile["vocabulary"]["top_words"] = [
            w for w, _ in word_counts.most_common(100) if len(w) > 2
        ][:100]
        self.profile["vocabulary"]["fillers"] = [
            w for w in word_counts if w.lower() in filler_words
        ]

        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        question_count = sum(1 for s in sentences if "?" in s)

        self.profile["structure"]["avg_sentence_length"] = round(avg_len, 1)
        self.profile["structure"]["question_ratio"] = round(
            question_count / len(sentences), 2
        )
        self.profile["structure"]["paragraph_count"] = round(
            len(sentences) / max(len(set(s[:20] for s in sentences)), 1), 1
        )

        self.profile["style"]["banglish_ratio"] = round(
            banglish_count / len(sentences), 2
        )

        if emojis:
            emoji_counts = Counter(emojis)
            self.profile["style"]["emoji_top"] = [
                e for e, _ in emoji_counts.most_common(5)
            ]
            self.profile["style"]["emoji_frequency"] = round(
                len(emojis) / len(sentences), 2
            )

    def get_profile(self):
        return self.profile

    def get_greeting(self):
        greetings = self.profile.get("tone_markers", {}).get("greeting", ["Bhai"])
        import random
        return random.choice(greetings)

    def get_closing(self):
        closings = self.profile.get("tone_markers", {}).get("closing", ["Thanks bhai"])
        import random
        return random.choice(closings)
