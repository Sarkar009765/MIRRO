import asyncio
import yaml
import json
from pathlib import Path

from .state_machine import StateMachine, AgentState
from .scheduler import Scheduler
from .memory import Memory, LeadStore, ConversationStore, NurtureStore
from ..utils.logger import get_logger, ActivityLogger

logger = get_logger("brain")


class MirrorBrain:
    def __init__(self, config_dir=None):
        config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent / "config"
        self.config_dir = config_dir

        self.policy = self._load_config("policy.yaml")
        self.safety = self._load_config("safety.yaml")
        self.groups = self._load_config("groups.yaml")

        self.memory = Memory()
        self.activity_logger = ActivityLogger(self.memory)
        self.leads = LeadStore(self.memory)
        self.conversations = ConversationStore(self.memory)
        self.nurture = NurtureStore(self.memory)

        self.state_machine = StateMachine()
        self.scheduler = Scheduler(self.policy)

        self.modules = {}
        self._tasks = []
        self._running = False

        Scheduler.on_event(self._handle_event)
        logger.info("MIRROR brain initialized")

    def _load_config(self, filename):
        path = self.config_dir / filename
        if path.suffix == ".yaml":
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def register_module(self, name, module):
        self.modules[name] = module
        logger.info(f"Module '{name}' registered")

    async def _handle_event(self, event_type):
        if event_type == "work_start":
            self.state_machine.transition(AgentState.IDLE)
            logger.info("Work day started")
        elif event_type == "work_end":
            self.state_machine.transition(AgentState.IDLE)
            logger.info("Work day ended")
        elif event_type == "sleep":
            self.state_machine.transition(AgentState.SLEEPING)
            logger.info("Going to sleep")
        elif event_type == "daily_summary":
            await self._generate_daily_summary()
        elif event_type == "backup":
            await self._perform_backup()

    async def _generate_daily_summary(self):
        hot_leads = self.leads.get_hot_leads()
        logger.info(f"Daily summary: {len(hot_leads)} hot leads today")

    async def _perform_backup(self):
        import shutil
        db_dir = Path(__file__).parent.parent / "database"
        backup_dir = Path(__file__).parent.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        for f in db_dir.glob("*.db"):
            shutil.copy2(f, backup_dir / f.name)
        logger.info("Database backup completed")

    async def run_cycle(self):
        if not self.state_machine.is_active() or not self.scheduler.is_within_working_hours():
            await asyncio.sleep(60)
            return

        self.state_machine.transition(AgentState.WATCHING)
        watcher = self.modules.get("watcher")
        if watcher:
            await watcher.scan_groups()

        nurture = self.modules.get("nurture_loop")
        if nurture:
            await nurture.process_pending()

        self.state_machine.transition(AgentState.IDLE)

    async def run_forever(self):
        self._running = True
        self.state_machine.transition(AgentState.IDLE)
        self.scheduler.start()
        logger.info("MIRROR is now running 24/7")

        try:
            while self._running:
                await self.run_cycle()
                await asyncio.sleep(300)
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            await self.shutdown()

    async def shutdown(self):
        self._running = False
        self.scheduler.stop()
        self.state_machine.transition(AgentState.IDLE)
        logger.info("MIRROR shutdown complete")

    def status(self):
        return {
            "state": self.state_machine.state.name,
            "modules": list(self.modules.keys()),
            "scheduler_jobs": self.scheduler.jobs,
            "running": self._running,
        }
