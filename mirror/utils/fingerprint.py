import random
from pathlib import Path


class FingerprintManager:
    def __init__(self, profile_dir):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.current_fingerprint = {}
        self._load_or_generate()

    def _load_or_generate(self):
        fp_file = self.profile_dir / "fingerprint.json"
        if fp_file.exists():
            import json
            self.current_fingerprint = json.loads(fp_file.read_text())
        else:
            self.current_fingerprint = self._generate()
            self._save()

    def _generate(self):
        return {
            "canvas": True,
            "webgl_renderer": "Intel Intel(R) HD Graphics 620",
            "webgl_vendor": "Intel Inc.",
            "timezone": "Asia/Dhaka",
            "timezone_offset": 360,
            "languages": ["bn-BD", "en-US", "en-GB"],
            "viewport": {"width": 1366, "height": 768},
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36",
            ]),
            "platform": "Win32",
            "hardware_concurrency": 4,
            "device_memory": 4,
        }

    def _save(self):
        import json
        fp_file = self.profile_dir / "fingerprint.json"
        fp_file.write_text(json.dumps(self.current_fingerprint, indent=2))

    def get_launch_args(self):
        fp = self.current_fingerprint
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-web-security",
            "--disable-infobars",
            f"--window-size={fp['viewport']['width']},{fp['viewport']['height']}",
            f"--lang={fp['languages'][0]}",
        ]
        return args

    def rotate(self):
        self.current_fingerprint = self._generate()
        self._save()
