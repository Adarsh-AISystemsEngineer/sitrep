"""
run_once.py
-----------
Called by GitHub Actions. Detects which job to run based on
current UTC time, executes it, sends to Telegram, then exits.

Alert deduplication uses a local file (seen_alerts.txt) which
is persisted between runs via GitHub Actions cache.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from telegram import Bot
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
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

# File to persist seen alert titles across GitHub Actions runs
SEEN_ALERTS_FILE = Path("seen_alerts.json")


# ── Alert deduplication helpers ───────────────────────────────────

def load_seen_alerts() -> set:
    try:
        if SEEN_ALERTS_FILE.exists():
            data = json.loads(SEEN_ALERTS_FILE.read_text())
            return set(data.get("titles", []))
    except Exception as e:
        log.warning(f"Could not load seen alerts: {e}")
    return set()


def save_seen_alerts(seen: set):
    try:
        # Keep only last 500 titles to prevent file growing forever
        titles = list(seen)[-500:]
        SEEN_ALERTS_FILE.write_text(json.dumps({"titles": titles}))
    except Exception as e:
        log.warning(f"Could not save seen alerts: {e}")


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
    seen    = load_seen_alerts()
    matched = scan_for_alerts(seen_titles=seen)

    if not matched:
        log.info("No new alerts.")
        return

    # Update and save seen titles
    for a in matched:
        seen.add(a["title"])
    save_seen_alerts(seen)

    text = format_alert(matched)
    await send(bot, text)
    log.info(f"Alert sent: {len(matched)} new item(s).")


# ── Dispatcher ────────────────────────────────────────────────────

JOB_MAP = {
    (1,  30): run_morning,
    (7,  30): run_afternoon,
    (13,  0): run_sports,
    (15, 30): run_tech,
}


async def main():
    now   = datetime.now(timezone.utc)
    h, m  = now.hour, now.minute
    m_norm = 0 if m < 30 else 30

    log.info(f"UTC: {h:02d}:{m:02d} → normalized: {h:02d}:{m_norm:02d}")

    bot    = Bot(token=TELEGRAM_BOT_TOKEN)
    job_fn = JOB_MAP.get((h, m_norm))

    if job_fn:
        await job_fn(bot)
    else:
        await run_alert(bot)


if __name__ == "__main__":
    asyncio.run(main())