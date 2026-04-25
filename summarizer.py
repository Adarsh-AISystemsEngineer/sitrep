import logging
from groq import Groq
from config import GROQ_API_KEY
from datetime import datetime

log    = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)
MODEL  = "llama3-8b-8192"   # Free on Groq, 14,400 req/day


def _today() -> str:
    return datetime.utcnow().strftime("%d %B %Y, %A")  # Railway runs UTC


def _call(system: str, user: str, max_tokens: int = 900) -> str:
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.35,
            max_tokens=max_tokens,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"Groq error: {e}")
        return "⚠️ Could not generate summary. Raw news was fetched successfully."


SYSTEM = """You are SitRep — a sharp current affairs briefing bot for CDS (Combined Defence Services) exam aspirants.
Write crisp, factual, exam-relevant digests from raw news headlines.
Use Telegram markdown (*bold*, _italic_). Every bullet must be one complete factual sentence.
Never invent facts. Only use what is provided."""


# ── Digest Builders ───────────────────────────────────────────────

def morning_digest(defence: str, international: str, sports: str, tech: str) -> str:
    prompt = f"""Build today's full morning digest.

DEFENCE / NATIONAL:
{defence}

INTERNATIONAL:
{international}

SPORTS:
{sports}

TECH & AI:
{tech}

Use EXACTLY this format:

🌅 *SITREP — MORNING BRIEFING*
📅 {_today()}
━━━━━━━━━━━━━━━━━━

🪖 *DEFENCE & NATIONAL*
• [3-4 exam-relevant points]

🌍 *INTERNATIONAL*
• [3-4 points]

🏅 *SPORTS*
• [2-3 points, include results/rankings if available]

🤖 *TECH & AI*
• [2-3 points, include India tech and global AI]

━━━━━━━━━━━━━━━━━━
📝 *KEY FACTS — REMEMBER THESE*
• [5 crisp one-liners: names, dates, places, firsts — good for SSB/written]

Max 420 words."""
    return _call(SYSTEM, prompt)


def afternoon_flash(defence: str, international: str) -> str:
    prompt = f"""Quick afternoon flash update.

DEFENCE:
{defence}

INTERNATIONAL:
{international}

Format:
⚡ *SITREP — AFTERNOON FLASH*
📅 {_today()} | 1:00 PM IST

🪖 *DEFENCE*
• [2-3 key points]

🌍 *WORLD*
• [2-3 key points]

🔑 *Must-Know Today:* [1 bold key fact]

Max 180 words."""
    return _call(SYSTEM, prompt, max_tokens=400)


def evening_sports(sports: str) -> str:
    prompt = f"""Evening sports update.

SPORTS NEWS:
{sports}

Format:
🏆 *SITREP — SPORTS UPDATE*
📅 {_today()} | 6:30 PM IST

🏅 *RESULTS & HIGHLIGHTS*
• [3-4 points with scores/winners/records]

🇮🇳 *INDIA IN SPORTS*
• [1-2 India-specific points]

Max 150 words."""
    return _call(SYSTEM, prompt, max_tokens=350)


def night_tech(tech: str) -> str:
    prompt = f"""Night tech & AI brief.

TECH NEWS:
{tech}

Format:
💻 *SITREP — TECH & AI BRIEF*
📅 {_today()} | 9:00 PM IST

🤖 *AI & TECHNOLOGY*
• [3-4 points: India tech, global AI, space, cybersecurity]

🧠 *CDS Exam Angle:* [1-2 points relevant to science & tech paper]

Max 150 words."""
    return _call(SYSTEM, prompt, max_tokens=350)


# ── Alert Formatter ───────────────────────────────────────────────

def format_alert(articles: list) -> str:
    """Format matched alert articles into a Telegram warning message."""
    lines = []
    for a in articles[:5]:   # Cap at 5 alerts per scan
        kws = ", ".join(a.get("matched_keywords", [])[:3])
        lines.append(f"• *{a['title']}*\n  _Source: {a['source']} | Keywords: {kws}_")

    body = "\n\n".join(lines)
    return (
        f"🚨 *SITREP ALERT — BREAKING*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{body}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ _Stay informed. Verify from official sources._"
    )