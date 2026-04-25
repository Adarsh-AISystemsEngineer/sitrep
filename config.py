import os
from dotenv import load_dotenv

load_dotenv()

# ── Credentials ────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
CURRENTS_API_KEY   = os.getenv("CURRENTS_API_KEY")   # currentsapi.services — free, no card
NEWSAPI_KEY        = os.getenv("NEWSAPI_KEY")         # newsapi.org — free, no card

# ── Schedule (IST = UTC+5:30, Railway runs UTC) ────────────────────
SCHEDULE = {
    "morning_digest":  {"hour": 1,  "minute": 30},   # 7:00 AM IST
    "afternoon_flash": {"hour": 7,  "minute": 30},   # 1:00 PM IST
    "evening_sports":  {"hour": 13, "minute": 0},    # 6:30 PM IST
    "night_tech":      {"hour": 15, "minute": 30},   # 9:00 PM IST
}

# Alert scan runs every 30 minutes
ALERT_SCAN_INTERVAL_MINUTES = 30

# ── RSS Feeds (unlimited, no key needed) ───────────────────────────
RSS_FEEDS = {
    "defence": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://feeds.feedburner.com/ndtv/india-news",
        "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    ],
    "international": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    ],
    "tech_ai": [
        "https://techcrunch.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.wired.com/feed/rss",
    ],
    # Alert scanning pulls from all feeds
    "all": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.feedburner.com/ndtv/india-news",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms",
    ],
}

# ── Alert Keywords ─────────────────────────────────────────────────
ALERT_KEYWORDS = [
    # Natural disasters
    "earthquake", "tsunami", "cyclone", "hurricane", "tornado",
    "flood", "wildfire", "volcano", "eruption", "landslide",
    # Conflict / security
    "war declared", "nuclear", "missile strike", "terror attack",
    "bombing", "explosion", "assassination", "coup", "invasion",
    "airstrike", "ceasefire broken", "mass shooting",
    # Health / infrastructure
    "pandemic", "outbreak", "epidemic", "plane crash", "train crash",
    "bridge collapse", "dam burst", "chemical leak",
    # India specific
    "india attack", "india flood", "india earthquake", "india cyclone",
    "border clash", "LOC firing", "surgical strike",
]

# ── CDS Relevance Keywords ─────────────────────────────────────────
CDS_KEYWORDS = [
    "india", "defence", "military", "army", "navy", "air force",
    "isro", "drdo", "ministry", "government", "policy", "border",
    "operation", "exercise", "missile", "geopolitics", "summit",
    "treaty", "bilateral", "parliament", "supreme court",
    "united nations", "nato", "g20", "g7", "brics",
]