import feedparser
import requests
import logging
from config import (
    RSS_FEEDS, CDS_KEYWORDS, ALERT_KEYWORDS,
    CURRENTS_API_KEY, NEWSAPI_KEY
)

log = logging.getLogger(__name__)


# ── RSS (primary source, unlimited & free) ────────────────────────

def fetch_rss(feed_urls: list, max_per_feed: int = 6) -> list:
    articles = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Strip HTML tags simply
                import re
                summary = re.sub(r"<[^>]+>", "", summary)[:400]
                articles.append({
                    "title":   title,
                    "summary": summary,
                    "link":    entry.get("link", ""),
                    "source":  feed.feed.get("title", "RSS"),
                })
        except Exception as e:
            log.warning(f"RSS failed [{url}]: {e}")
    return articles


# ── Currents API (free, no card, 600 req/day) ─────────────────────

def fetch_currents(keywords: str, max_results: int = 5) -> list:
    if not CURRENTS_API_KEY:
        return []
    try:
        url = "https://api.currentsapi.services/v1/search"
        params = {
            "keywords": keywords,
            "language": "en",
            "apiKey":   CURRENTS_API_KEY,
            "page_size": max_results,
        }
        res  = requests.get(url, params=params, timeout=10)
        data = res.json()
        return [
            {
                "title":   a.get("title", ""),
                "summary": a.get("description", "")[:400],
                "link":    a.get("url", ""),
                "source":  "Currents",
            }
            for a in data.get("news", [])
        ]
    except Exception as e:
        log.warning(f"Currents API failed: {e}")
        return []


# ── NewsAPI (free, no card, 100 req/day) ──────────────────────────

def fetch_newsapi(query: str, max_results: int = 5) -> list:
    if not NEWSAPI_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q":        query,
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": max_results,
            "apiKey":   NEWSAPI_KEY,
        }
        res  = requests.get(url, params=params, timeout=10)
        data = res.json()
        return [
            {
                "title":   a.get("title", ""),
                "summary": (a.get("description") or "")[:400],
                "link":    a.get("url", ""),
                "source":  a.get("source", {}).get("name", "NewsAPI"),
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        log.warning(f"NewsAPI failed: {e}")
        return []


# ── Deduplication & Scoring ───────────────────────────────────────

def deduplicate(articles: list) -> list:
    seen, unique = set(), []
    for a in articles:
        key = "".join(a["title"].lower().split()[:6])
        if key and key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def score(article: dict, keywords: list) -> int:
    text = (article["title"] + " " + article["summary"]).lower()
    return sum(1 for kw in keywords if kw in text)


def format_for_prompt(articles: list) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. [{a['source']}] {a['title']}. {a['summary']}")
    return "\n".join(lines) if lines else "No articles fetched."


# ── Category Fetchers ─────────────────────────────────────────────

def get_defence_news() -> list:
    arts = fetch_rss(RSS_FEEDS["defence"], 8)
    arts += fetch_currents("India defence military army navy air force", 5)
    arts = deduplicate(arts)
    arts.sort(key=lambda a: score(a, CDS_KEYWORDS), reverse=True)
    return arts[:8]


def get_international_news() -> list:
    arts = fetch_rss(RSS_FEEDS["international"], 6)
    arts += fetch_newsapi("India foreign affairs geopolitics world", 4)
    return deduplicate(arts)[:8]


def get_sports_news() -> list:
    arts = fetch_rss(RSS_FEEDS["sports"], 6)
    arts += fetch_currents("India sports cricket hockey badminton", 4)
    return deduplicate(arts)[:8]


def get_tech_news() -> list:
    arts = fetch_rss(RSS_FEEDS["tech_ai"], 6)
    arts += fetch_newsapi("artificial intelligence technology India", 4)
    return deduplicate(arts)[:8]


def get_all_news() -> dict:
    log.info("Fetching all news categories...")
    return {
        "defence":       get_defence_news(),
        "international": get_international_news(),
        "sports":        get_sports_news(),
        "tech":          get_tech_news(),
    }


# ── Alert Scanner ─────────────────────────────────────────────────

def scan_for_alerts() -> list:
    """
    Scan all RSS feeds for catastrophe/danger keywords.
    Returns list of matched articles.
    """
    arts = fetch_rss(RSS_FEEDS["all"], max_per_feed=10)
    matched = []
    for a in arts:
        text = (a["title"] + " " + a["summary"]).lower()
        hit_keywords = [kw for kw in ALERT_KEYWORDS if kw in text]
        if hit_keywords:
            a["matched_keywords"] = hit_keywords
            matched.append(a)
    return deduplicate(matched)