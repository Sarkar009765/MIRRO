#!/usr/bin/env python3
"""
MIRROR — Autonomous Client Hunting Organism
Main entry point — starts the 24/7 agent
"""

import os
import sys
import asyncio
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mirror.core.brain import MirrorBrain
from mirror.api_plugins import APIAggregator
from mirror.modules.dna_cloner import DNACloner
from mirror.modules.archaeologist import Archaeologist
from mirror.modules.watcher import Watcher
from mirror.modules.ghost_writer import GhostWriter
from mirror.modules.shadow_matrix import ShadowMatrix
from mirror.modules.warmth_protocol import WarmthProtocol
from mirror.modules.nurture_loop import NurtureLoop
from mirror.modules.competitor_radar import CompetitorRadar
from mirror.modules.portfolio_sniping import PortfolioSniping
from mirror.modules.safety_guard import SafetyGuard
from mirror.war_room.telegram_bot import WarRoom
from mirror.utils.logger import get_logger

logger = get_logger("main")


class MirrorApplication:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else (
            Path(__file__).parent / "config"
        )
        self._load_env()
        self.brain = MirrorBrain(self.config_dir)
        self.api = APIAggregator()
        self.modules = {}
        self.war_room = WarRoom(self.brain)
        self._initialized = False

    def _load_env(self):
        env_file = self.config_dir / "secrets.env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

    def init_modules(self):
        dna = DNACloner(self.config_dir)
        self.modules["dna_cloner"] = dna

        archaeologist = Archaeologist(self.api, self.brain.leads)
        self.modules["archaeologist"] = archaeologist

        watcher = Watcher(
            self.brain.leads, self.api,
            self.brain.groups.get("groups", [])
        )
        self.modules["watcher"] = watcher

        writer = GhostWriter(self.api, dna.get_profile())
        self.modules["ghost_writer"] = writer

        shadow = ShadowMatrix()
        self.modules["shadow_matrix"] = shadow

        warmth = WarmthProtocol(self.brain.policy, self.brain.leads)
        self.modules["warmth_protocol"] = warmth

        nurture = NurtureLoop(self.brain.leads, self.brain.nurture, writer)
        self.modules["nurture_loop"] = nurture

        radar = CompetitorRadar(self.brain.leads)
        self.modules["competitor_radar"] = radar

        portfolio = PortfolioSniping()
        self.modules["portfolio_sniping"] = portfolio

        safety = SafetyGuard(self.brain.safety)
        self.modules["safety_guard"] = safety

        for name, module in self.modules.items():
            self.brain.register_module(name, module)

        self._initialized = True
        logger.info(f"All {len(self.modules)} modules initialized")

    async def start(self):
        if not self._initialized:
            self.init_modules()

        logger.info("MIRROR starting up...")

        start_task = asyncio.create_task(self.war_room.start())
        await asyncio.sleep(1)

        brain_task = asyncio.create_task(self.brain.run_forever())

        try:
            await asyncio.gather(brain_task, start_task)
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def shutdown(self):
        logger.info("Shutting down MIRROR...")
        await self.war_room.stop()
        await self.brain.shutdown()
        logger.info("MIRROR shutdown complete")


async def main():
    app = MirrorApplication()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
