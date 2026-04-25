import asyncio
import logging
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SCHEDULE, ALERT_SCAN_INTERVAL_MINUTES
from fetcher import (
    get_all_news, get_defence_news, get_international_news,
    get_sports_news, get_tech_news, scan_for_alerts, format_for_prompt,
)
from summarizer import (
    morning_digest, afternoon_flash, evening_sports, night_tech, format_alert,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# Track already-alerted headlines to avoid duplicate alerts
_alerted_titles: set = set()


# ── Sender ────────────────────────────────────────────────────────

async def send(bot: Bot, text: str):
    """Send message, split if over Telegram's 4096 char limit."""
    MAX = 4000
    chunks = [text[i:i+MAX] for i in range(0, len(text), MAX)]
    for chunk in chunks:
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=chunk,
                parse_mode="Markdown",
            )
            await asyncio.sleep(0.5)
        except TelegramError as e:
            log.error(f"Telegram send failed: {e}")
            # Retry without markdown
            try:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=chunk)
            except TelegramError as e2:
                log.error(f"Retry failed: {e2}")


# ── Scheduled Jobs ────────────────────────────────────────────────

async def job_morning(bot: Bot):
    log.info("⏰ Running: Morning Digest")
    news    = get_all_news()
    digest  = morning_digest(
        defence=format_for_prompt(news["defence"]),
        international=format_for_prompt(news["international"]),
        sports=format_for_prompt(news["sports"]),
        tech=format_for_prompt(news["tech"]),
    )
    await send(bot, digest)
    log.info("✅ Morning digest sent.")


async def job_afternoon(bot: Bot):
    log.info("⏰ Running: Afternoon Flash")
    defence = get_defence_news()
    intl    = get_international_news()
    flash   = afternoon_flash(
        defence=format_for_prompt(defence),
        international=format_for_prompt(intl),
    )
    await send(bot, flash)
    log.info("✅ Afternoon flash sent.")


async def job_sports(bot: Bot):
    log.info("⏰ Running: Evening Sports")
    sports  = get_sports_news()
    update  = evening_sports(format_for_prompt(sports))
    await send(bot, update)
    log.info("✅ Evening sports sent.")


async def job_tech(bot: Bot):
    log.info("⏰ Running: Night Tech")
    tech   = get_tech_news()
    update = night_tech(format_for_prompt(tech))
    await send(bot, update)
    log.info("✅ Night tech sent.")


async def job_alert_scan(bot: Bot):
    """Runs every 30 min. Sends alert only if new catastrophe headlines found."""
    global _alerted_titles
    log.info("🔍 Alert scan running...")

    matched = scan_for_alerts()
    if not matched:
        log.info("✅ No alerts.")
        return

    # Filter out already-alerted titles
    new_alerts = [a for a in matched if a["title"] not in _alerted_titles]
    if not new_alerts:
        log.info("✅ No new alerts (already sent).")
        return

    # Mark as alerted
    for a in new_alerts:
        _alerted_titles.add(a["title"])

    # Keep cache from growing forever
    if len(_alerted_titles) > 200:
        _alerted_titles = set(list(_alerted_titles)[-100:])

    alert_text = format_alert(new_alerts)
    await send(bot, alert_text)
    log.info(f"🚨 Alert sent: {len(new_alerts)} new item(s).")


# ── Main ──────────────────────────────────────────────────────────

async def main():
    log.info("🚀 SitRep Bot starting...")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Verify bot token on startup
    try:
        me = await bot.get_me()
        log.info(f"✅ Bot verified: @{me.username}")
    except TelegramError as e:
        log.critical(f"❌ Bot token invalid: {e}")
        return

    scheduler = AsyncIOScheduler(timezone="UTC")

    # Daily digest jobs
    scheduler.add_job(job_morning,   "cron",
        hour=SCHEDULE["morning_digest"]["hour"],
        minute=SCHEDULE["morning_digest"]["minute"],
        args=[bot])

    scheduler.add_job(job_afternoon, "cron",
        hour=SCHEDULE["afternoon_flash"]["hour"],
        minute=SCHEDULE["afternoon_flash"]["minute"],
        args=[bot])

    scheduler.add_job(job_sports,    "cron",
        hour=SCHEDULE["evening_sports"]["hour"],
        minute=SCHEDULE["evening_sports"]["minute"],
        args=[bot])

    scheduler.add_job(job_tech,      "cron",
        hour=SCHEDULE["night_tech"]["hour"],
        minute=SCHEDULE["night_tech"]["minute"],
        args=[bot])

    # Alert scan every 30 minutes
    scheduler.add_job(job_alert_scan, "interval",
        minutes=ALERT_SCAN_INTERVAL_MINUTES,
        args=[bot])

    scheduler.start()

    log.info("📅 Schedule (UTC):")
    log.info(f"   🌅 Morning digest  → {SCHEDULE['morning_digest']['hour']:02d}:{SCHEDULE['morning_digest']['minute']:02d} UTC  (7:00 AM IST)")
    log.info(f"   ⚡ Afternoon flash → {SCHEDULE['afternoon_flash']['hour']:02d}:{SCHEDULE['afternoon_flash']['minute']:02d} UTC  (1:00 PM IST)")
    log.info(f"   🏆 Evening sports  → {SCHEDULE['evening_sports']['hour']:02d}:{SCHEDULE['evening_sports']['minute']:02d} UTC  (6:30 PM IST)")
    log.info(f"   💻 Night tech      → {SCHEDULE['night_tech']['hour']:02d}:{SCHEDULE['night_tech']['minute']:02d} UTC  (9:00 PM IST)")
    log.info(f"   🚨 Alert scan      → every {ALERT_SCAN_INTERVAL_MINUTES} minutes")
    log.info("✅ SitRep is live.")

    # Send startup confirmation to yourself
    await send(bot, "✅ *SitRep is online.*\nScheduled briefings and alert scanning are active.")

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())