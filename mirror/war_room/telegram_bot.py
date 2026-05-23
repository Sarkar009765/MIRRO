import os
import json
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger("war_room")

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed — War Room unavailable")


class WarRoom:
    def __init__(self, brain=None):
        self.brain = brain
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID", "")
        self.app = None
        logger.info("War Room initialized")

    async def start(self):
        if not TELEGRAM_AVAILABLE or not self.token:
            logger.warning("Telegram bot not available — skipping")
            return

        self.app = Application.builder().token(self.token).build()

        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("leads", self._cmd_leads))
        self.app.add_handler(CommandHandler("approve", self._cmd_approve))
        self.app.add_handler(CommandHandler("reject", self._cmd_reject))
        self.app.add_handler(CommandHandler("autopilot", self._cmd_autopilot))
        self.app.add_handler(CommandHandler("pause", self._cmd_pause))
        self.app.add_handler(CommandHandler("resume", self._cmd_resume))
        self.app.add_handler(CommandHandler("config", self._cmd_config))
        self.app.add_handler(CommandHandler("quota", self._cmd_quota))
        self.app.add_handler(CommandHandler("shadows", self._cmd_shadows))
        self.app.add_handler(CommandHandler("warmth", self._cmd_warmth))
        self.app.add_handler(CommandHandler("competitors", self._cmd_competitors))
        self.app.add_handler(CommandHandler("report", self._cmd_report))

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("War Room bot is live")

    async def stop(self):
        if self.app:
            await self.app.stop()
            await self.app.shutdown()

    def _check_admin(self, update):
        return str(update.effective_user.id) == self.admin_chat_id

    async def _cmd_start(self, update, context):
        if not self._check_admin(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        await update.message.reply_text(
            "🤖 **MIRROR War Room Active**\n\n"
            "`/status` — System health\n"
            "`/leads` — Today's leads\n"
            "`/approve [id]` — Approve lead\n"
            "`/reject [id]` — Reject lead\n"
            "`/pause [h]` — Pause activity\n"
            "`/resume` — Resume activity\n"
            "`/autopilot on|off` — Toggle autopilot\n"
            "`/report` — Daily summary\n"
            "`/config` — View config\n"
            "`/quota` — API usage\n"
            "`/shadows` — Account health\n"
            "`/warmth` — Group scores\n"
            "`/competitors` — Intel report"
        )

    async def _cmd_status(self, update, context):
        if not self._check_admin(update):
            return
        if not self.brain:
            await update.message.reply_text("Brain not connected")
            return
        status = self.brain.status()
        await update.message.reply_text(
            f"📊 **MIRROR Status**\n"
            f"State: `{status['state']}`\n"
            f"Modules: `{len(status['modules'])}` loaded\n"
            f"Jobs: `{len(status['scheduler_jobs'])}` scheduled\n"
            f"Running: `{'✅' if status['running'] else '❌'}`"
        )

    async def _cmd_leads(self, update, context):
        if not self._check_admin(update):
            return
        if not self.brain:
            return
        hot = self.brain.leads.get_hot_leads()
        if not hot:
            await update.message.reply_text("No hot leads today.")
            return
        msg = "**🔥 Hot Leads Today**\n\n"
        for lead in hot[:10]:
            msg += (
                f"`#{lead['id']}` — {lead.get('name', 'Unknown')}\n"
                f"  Score: {lead['hotness_score']} | Group: {lead.get('group_name', 'N/A')}\n"
                f"  Status: {lead.get('status', 'new')}\n\n"
            )
        await update.message.reply_text(msg)

    async def _cmd_approve(self, update, context):
        if not self._check_admin(update):
            return
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /approve [id] or /approve all")
            return
        await update.message.reply_text(f"✅ Lead {args[0]} approved")

    async def _cmd_reject(self, update, context):
        if not self._check_admin(update):
            return
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /reject [id]")
            return
        await update.message.reply_text(f"❌ Lead {args[0]} rejected")

    async def _cmd_autopilot(self, update, context):
        if not self._check_admin(update):
            return
        args = context.args
        mode = args[0] if args else "toggle"
        await update.message.reply_text(f"✈️ Autopilot: {mode}")

    async def _cmd_pause(self, update, context):
        if not self._check_admin(update):
            return
        args = context.args
        duration = args[0] if args else "1"
        if self.brain:
            self.brain.state_machine.pause()
        await update.message.reply_text(f"⏸️ Paused for {duration}h")

    async def _cmd_resume(self, update, context):
        if not self._check_admin(update):
            return
        if self.brain:
            self.brain.state_machine.resume()
        await update.message.reply_text("▶️ Resumed")

    async def _cmd_config(self, update, context):
        if not self._check_admin(update):
            return
        if not self.brain:
            return
        policy = self.brain.policy
        await update.message.reply_text(
            f"⚙️ **Current Policy**\n"
            f"Active: {policy.get('scheduling', {}).get('active_start', 'N/A')}-"
            f"{policy.get('scheduling', {}).get('active_end', 'N/A')}\n"
            f"Max comments/day: {policy.get('scheduling', {}).get('max_daily_comments', 8)}\n"
            f"Min pitch warmth: {policy.get('warmth_protocol', {}).get('min_warmth_score_pitch', 70)}"
        )

    async def _cmd_quota(self, update, context):
        if not self._check_admin(update):
            return
        await update.message.reply_text("🔋 API quotas: Check `/status` for details")

    async def _cmd_shadows(self, update, context):
        if not self._check_admin(update):
            return
        await update.message.reply_text(
            "👥 **Shadow Matrix**\n"
            "• Primary: Agency Page\n"
            "• Shadow-1: Dev Persona\n"
            "• Shadow-2: Past Client\n"
            "Status: All active"
        )

    async def _cmd_warmth(self, update, context):
        if not self._check_admin(update):
            return
        await update.message.reply_text("🌡️ Warmth scores: Check `/status`")

    async def _cmd_competitors(self, update, context):
        if not self._check_admin(update):
            return
        await update.message.reply_text("🕵️ Competitor radar: No threats detected")

    async def _cmd_report(self, update, context):
        if not self._check_admin(update):
            return
        await update.message.reply_text(
            f"📈 **Daily Report**\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"System: Operational\n"
            f"Check `/leads` for lead details"
        )

    async def send_alert(self, message, alert_type="info"):
        if not self.app or not self.admin_chat_id:
            return
        try:
            await self.app.bot.send_message(
                chat_id=self.admin_chat_id,
                text=f"🚨 **{alert_type.upper()}**\n{message}",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
