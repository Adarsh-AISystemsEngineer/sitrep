import feedparser
import requests
import logging
import re
from config import (
    RSS_FEEDS, CDS_KEYWORDS, ALERT_KEYWORDS,
    CURRENTS_API_KEY, NEWSAPI_KEY,
    CURRENTS_QUERIES, NEWSAPI_QUERIES,
)

log = logging.getLogger(__name__)


# ── RSS (primary, unlimited & free) ───────────────────────────────

def fetch_rss(feed_urls: list, max_per_feed: int = 6) -> list:
    articles = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                summary = re.sub(r"<[^>]+>", "", summary)[:400]
                if title:
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
        res = requests.get(
            "https://api.currentsapi.services/v1/search",
            params={
                "keywords": keywords,
                "language": "en",
                "apiKey":   CURRENTS_API_KEY,
                "page_size": max_results,
                "country":  "IN",
            },
            timeout=10,
        )
        return [
            {
                "title":   a.get("title", ""),
                "summary": a.get("description", "")[:400],
                "link":    a.get("url", ""),
                "source":  "Currents",
            }
            for a in res.json().get("news", [])
        ]
    except Exception as e:
        log.warning(f"Currents API failed: {e}")
        return []


# ── NewsAPI (free, no card, 100 req/day) ──────────────────────────

def fetch_newsapi(query: str, max_results: int = 5) -> list:
    if not NEWSAPI_KEY:
        return []
    try:
        res = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":        query,
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": max_results,
                "apiKey":   NEWSAPI_KEY,
            },
            timeout=10,
        )
        return [
            {
                "title":   a.get("title", ""),
                "summary": (a.get("description") or "")[:400],
                "link":    a.get("url", ""),
                "source":  a.get("source", {}).get("name", "NewsAPI"),
            }
            for a in res.json().get("articles", [])
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]
    except Exception as e:
        log.warning(f"NewsAPI failed: {e}")
        return []


# ── Helpers ───────────────────────────────────────────────────────

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
    if not articles:
        return "No articles fetched."
    return "\n".join(
        f"{i}. [{a['source']}] {a['title']}. {a['summary']}"
        for i, a in enumerate(articles, 1)
    )


# ── Category Fetchers ─────────────────────────────────────────────

def get_defence_news() -> list:
    arts  = fetch_rss(RSS_FEEDS["defence"], 8)
    arts += fetch_currents(CURRENTS_QUERIES["defence"], 5)
    arts += fetch_newsapi(NEWSAPI_QUERIES["defence"], 4)
    arts  = deduplicate(arts)
    arts.sort(key=lambda a: score(a, CDS_KEYWORDS), reverse=True)
    return arts[:10]


def get_international_news() -> list:
    arts  = fetch_rss(RSS_FEEDS["international"], 6)
    arts += fetch_currents(CURRENTS_QUERIES["international"], 4)
    arts += fetch_newsapi(NEWSAPI_QUERIES["international"], 4)
    return deduplicate(arts)[:10]


def get_sports_news() -> list:
    arts  = fetch_rss(RSS_FEEDS["sports"], 6)
    arts += fetch_currents(CURRENTS_QUERIES["sports"], 4)
    arts += fetch_newsapi(NEWSAPI_QUERIES["sports"], 3)
    return deduplicate(arts)[:10]


def get_tech_news() -> list:
    arts  = fetch_rss(RSS_FEEDS["tech_ai"], 6)
    arts += fetch_currents(CURRENTS_QUERIES["tech_ai"], 4)
    arts += fetch_newsapi(NEWSAPI_QUERIES["tech_ai"], 3)
    return deduplicate(arts)[:10]


def get_all_news() -> dict:
    log.info("Fetching all news categories...")
    return {
        "defence":       get_defence_news(),
        "international": get_international_news(),
        "sports":        get_sports_news(),
        "tech":          get_tech_news(),
    }


# ── Alert Scanner (title-only, no duplicates) ─────────────────────

def scan_for_alerts(seen_titles: set = None) -> list:
    """
    Scans RSS titles ONLY for unambiguous emergency keywords.
    Skips titles already in seen_titles to prevent duplicate alerts.
    """
    if seen_titles is None:
        seen_titles = set()

    arts    = fetch_rss(RSS_FEEDS["all"], max_per_feed=15)
    matched = []

    for a in arts:
        title_lower = a["title"].lower()
        if a["title"] in seen_titles:
            continue
        hit = [kw for kw in ALERT_KEYWORDS if kw in title_lower]
        if hit:
            a["matched_keywords"] = hit
            matched.append(a)

    return deduplicate(matched) 