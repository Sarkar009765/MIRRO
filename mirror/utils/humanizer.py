import asyncio
import random
import time


class Humanizer:
    def __init__(self, config=None):
        cfg = config or {}
        self.typing_min = cfg.get("typing_speed_min_wpm", 40)
        self.typing_max = cfg.get("typing_speed_max_wpm", 70)
        self.backspace_prob = cfg.get("backspace_probability", 0.08)
        self.pause_min = cfg.get("random_pause_min_seconds", 3)
        self.pause_max = cfg.get("random_pause_max_seconds", 15)

    async def human_type(self, page, text, element_selector=None):
        target = page.locator(element_selector) if element_selector else page
        await target.click()
        await asyncio.sleep(random.uniform(0.3, 0.8))

        for char in text:
            await target.type(char, delay=random.randint(30, 80))
            if random.random() < self.backspace_prob and len(text) > 5:
                await target.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await target.type(char, delay=random.randint(30, 60))

    async def human_scroll(self, page, target_y=None):
        target_y = target_y or random.randint(300, 1500)
        current_y = 0
        while current_y < target_y:
            step = random.randint(50, 200)
            current_y += step
            await page.evaluate(f"window.scrollTo(0, {current_y})")
            await asyncio.sleep(random.uniform(0.1, 0.4))
        await asyncio.sleep(random.uniform(0.5, 1.5))

    async def human_pause(self, min_s=None, max_s=None):
        duration = random.uniform(
            min_s or self.pause_min, max_s or self.pause_max
        )
        await asyncio.sleep(duration)

    async def random_mouse_move(self, page):
        vp = page.viewport_size
        for _ in range(random.randint(1, 3)):
            x = random.randint(0, vp["width"])
            y = random.randint(0, vp["height"])
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.05, 0.2))

    async def simulate_thinking_pause(self, page):
        await self.random_mouse_move(page)
        await self.human_pause(2, 6)

    def time_to_next_action(self, min_minutes=2, max_minutes=15):
        return random.randint(min_minutes * 60, max_minutes * 60)

    def should_take_break(self, hour, is_weekend=False):
        if 1 <= hour < 8:
            return True
        if 13 <= hour < 14:
            return True
        if is_weekend and random.random() < 0.5:
            return True
        return False
