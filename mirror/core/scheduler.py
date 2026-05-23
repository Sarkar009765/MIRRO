import asyncio
import random
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from ..utils.logger import get_logger

logger = get_logger("scheduler")


class Scheduler:
    def __init__(self, policy):
        self.policy = policy
        self.scheduler = AsyncIOScheduler()
        self._jobs = {}
        self._running = False

    def start(self):
        if self._running:
            return
        self._schedule_core_jobs()
        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started")

    def stop(self):
        if not self._running:
            return
        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("Scheduler stopped")

    def _schedule_core_jobs(self):
        policy = self.policy

        active_start = policy.get("scheduling", {}).get("active_start", "10:00")
        active_end = policy.get("scheduling", {}).get("active_end", "21:00")
        sleep_start = policy.get("scheduling", {}).get("sleep_start", "01:00")

        active_h = int(active_start.split(":")[0])
        active_m = int(active_start.split(":")[1])
        end_h = int(active_end.split(":")[0])
        end_m = int(active_end.split(":")[1])
        sleep_h = int(sleep_start.split(":")[0])
        sleep_m = int(sleep_start.split(":")[1])

        self.scheduler.add_job(
            self._trigger_event,
            CronTrigger(hour=active_h, minute=active_m),
            args=["work_start"],
            id="work_start",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._trigger_event,
            CronTrigger(hour=end_h, minute=end_m),
            args=["work_end"],
            id="work_end",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._trigger_event,
            CronTrigger(hour=sleep_h, minute=sleep_m),
            args=["sleep"],
            id="sleep",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._trigger_event,
            CronTrigger(hour=22, minute=0),
            args=["daily_summary"],
            id="daily_summary",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._trigger_event,
            IntervalTrigger(hours=6),
            args=["backup"],
            id="backup",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._trigger_event,
            CronTrigger(hour=3, minute=0),
            args=["check_update"],
            id="check_update",
            replace_existing=True,
        )

    def add_job(self, name, func, trigger, **kwargs):
        self.scheduler.add_job(func, trigger, id=name, replace_existing=True, **kwargs)
        self._jobs[name] = True
        logger.info(f"Job '{name}' registered")

    def remove_job(self, name):
        try:
            self.scheduler.remove_job(name)
            self._jobs.pop(name, None)
        except Exception:
            pass

    _event_listeners = []

    @classmethod
    def on_event(cls, func):
        cls._event_listeners.append(func)
        return func

    async def _trigger_event(self, event_type):
        for listener in self._event_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_type)
                else:
                    listener(event_type)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")

    @property
    def jobs(self):
        return list(self._jobs.keys())

    def is_within_working_hours(self):
        now = datetime.now()
        policy = self.policy
        active_start = policy.get("scheduling", {}).get("active_start", "10:00")
        active_end = policy.get("scheduling", {}).get("active_end", "21:00")
        start_h, start_m = map(int, active_start.split(":"))
        end_h, end_m = map(int, active_end.split(":"))
        start_t = time(start_h, start_m)
        end_t = time(end_h, end_m)
        now_t = now.time()
        if start_t <= end_t:
            return start_t <= now_t <= end_t
        return now_t >= start_t or now_t <= end_t
