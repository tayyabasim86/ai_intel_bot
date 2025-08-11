import re, hashlib, datetime as dt
from urllib.parse import urlparse
from bs4 import BeautifulSoup

KEYWORDS = [
    "ai","model","llm","agent","research","paper","benchmark","release",
    "open-source","inference","fine-tune","safety","product","feature","update"
]

def strip_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.get_text(" ").split())

def canonical_domain(url: str) -> str:
    try:
        return urlparse(url).netloc or ""
    except Exception:
        return ""

def compute_key(title: str, domain: str, date_str: str) -> str:
    base = f"{(title or '').lower().strip()}|{domain or ''}|{date_str or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def simple_relevance(text: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    hits = sum(1 for kw in KEYWORDS if kw in t)
    return min(1.0, hits / 8.0)

def now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
