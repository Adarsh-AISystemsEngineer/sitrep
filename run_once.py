"""
run_once.py
-----------
Called by GitHub Actions. Detects which job to run based on
the current UTC hour:minute, executes it, sends to Telegram, then exits.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from telegram import Bot
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ALERT_KEYWORDS
from fetcher import (
    get_all_news,
    get_defence_news,
    get_international_news,
    get_sports_news,
    get_tech_news,
    scan_for_alerts,
    format_for_prompt,
)
from summarizer import (
    morning_digest,
    afternoon_flash,
    evening_sports,
    night_tech,
    format_alert,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ── Sender ────────────────────────────────────────────────────────

async def send(bot: Bot, text: str):
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
            try:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=chunk)
            except TelegramError as e2:
                log.error(f"Retry failed: {e2}")


# ── Jobs ──────────────────────────────────────────────────────────

async def run_morning(bot: Bot):
    log.info("Running: Morning Digest")
    news = get_all_news()
    text = morning_digest(
        defence=format_for_prompt(news["defence"]),
        international=format_for_prompt(news["international"]),
        sports=format_for_prompt(news["sports"]),
        tech=format_for_prompt(news["tech"]),
    )
    await send(bot, text)
    log.info("Morning digest sent.")


async def run_afternoon(bot: Bot):
    log.info("Running: Afternoon Flash")
    text = afternoon_flash(
        defence=format_for_prompt(get_defence_news()),
        international=format_for_prompt(get_international_news()),
    )
    await send(bot, text)
    log.info("Afternoon flash sent.")


async def run_sports(bot: Bot):
    log.info("Running: Evening Sports")
    text = evening_sports(format_for_prompt(get_sports_news()))
    await send(bot, text)
    log.info("Evening sports sent.")


async def run_tech(bot: Bot):
    log.info("Running: Night Tech")
    text = night_tech(format_for_prompt(get_tech_news()))
    await send(bot, text)
    log.info("Night tech sent.")


async def run_alert(bot: Bot):
    log.info("Running: Alert Scan")
    matched = scan_for_alerts()
    if not matched:
        log.info("No alerts found.")
        return
    text = format_alert(matched)
    await send(bot, text)
    log.info(f"Alert sent: {len(matched)} item(s).")


# ── Dispatcher ────────────────────────────────────────────────────

# Maps (hour, minute) UTC → job function
JOB_MAP = {
    (1,  30): run_morning,
    (7,  30): run_afternoon,
    (13,  0): run_sports,
    (15, 30): run_tech,
}

# Alert scan runs on any other trigger (workflow_dispatch or */30 cron)
ALERT_MINUTES = {0, 30}   # runs at :00 and :30 of every hour


async def main():
    now = datetime.now(timezone.utc)
    h, m = now.hour, now.minute

    # Normalize minute to nearest 0 or 30 to handle slight timing drift
    m_norm = 0 if m < 30 else 30

    log.info(f"Current UTC: {h:02d}:{m:02d} (normalized minute: {m_norm})")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Check if a named digest job matches this time
    job_fn = JOB_MAP.get((h, m_norm))

    if job_fn:
        await job_fn(bot)
    else:
        # Any other trigger → run alert scan
        await run_alert(bot)


if __name__ == "__main__":
    asyncio.run(main())