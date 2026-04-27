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
        # India govt & defence
        "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",   # PIB Defence
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://feeds.feedburner.com/ndtv/india-news",
        "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms",
        "https://www.indiatoday.in/rss/home",
        "https://indianexpress.com/section/india/feed/",
    ],
    "international": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        # India foreign affairs
        "https://www.thehindu.com/news/international/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",  # TOI world
    ],
    "sports": [
        # India sports focused
        "https://sportstar.thehindu.com/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
        "https://feeds.feedburner.com/ndtv/sports",
        "https://www.indiatoday.in/rss/1206578",                       # India Today sports
    ],
    "tech_ai": [
        # India tech
        "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
        "https://www.thehindu.com/sci-tech/feeder/default.rss",
        "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=74",    # PIB Science & Tech
        # Global tech
        "https://techcrunch.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    # Alert scanning — broad mix of India + world
    "all": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.feedburner.com/ndtv/india-news",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms",
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.indiatoday.in/rss/home",
    ],
}

# ── Alert Keywords (title-only, unambiguous emergencies) ───────────
ALERT_KEYWORDS = [
    # Natural disasters
    "earthquake", "tsunami", "cyclone", "hurricane", "tornado",
    "wildfire", "volcano", "eruption", "landslide", "floods kill",
    "floods destroy", "flood warning",
    # Conflict — specific phrases only
    "war declared", "nuclear strike", "nuclear attack",
    "missile strike", "terror attack", "suicide bombing",
    "ceasefire broken", "troops killed", "soldiers killed",
    "airstrike kills", "coup attempt",
    # Health emergencies
    "pandemic declared", "outbreak kills", "epidemic",
    # Infrastructure disasters
    "plane crash", "train crash", "train derail",
    "bridge collapse", "dam burst", "dam breach", "chemical leak",
    # India specific
    "india floods", "india earthquake", "india cyclone",
    "border clash", "loc violation", "surgical strike",
    "blast kills", "explosion kills",
]

# ── CDS Relevance Keywords ─────────────────────────────────────────
CDS_KEYWORDS = [
    "india", "defence", "military", "army", "navy", "air force",
    "isro", "drdo", "ministry", "government", "policy", "border",
    "operation", "exercise", "missile", "geopolitics", "summit",
    "treaty", "bilateral", "parliament", "supreme court",
    "united nations", "nato", "g20", "g7", "brics", "modi",
    "indian", "bharat", "mea", "home ministry", "rajya sabha",
    "lok sabha", "rbi", "upsc", "nda", "cds exam",
]

# ── Currents API query strings (India-focused) ─────────────────────
CURRENTS_QUERIES = {
    "defence":       "India defence military army navy air force DRDO ISRO border",
    "international": "India foreign policy Modi bilateral summit geopolitics",
    "sports":        "India cricket hockey badminton sports medal tournament",
    "tech_ai":       "India technology startup AI artificial intelligence space ISRO",
}

# ── NewsAPI query strings (India-focused) ──────────────────────────
NEWSAPI_QUERIES = {
    "defence":       "India defence OR military OR army OR navy site:thehindu.com OR site:ndtv.com",
    "international": "India foreign affairs OR geopolitics OR Modi",
    "sports":        "India sports OR cricket OR IPL OR hockey",
    "tech_ai":       "India AI OR technology OR ISRO OR startup",
}