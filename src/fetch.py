import feedparser, requests
from bs4 import BeautifulSoup
from util import strip_html, canonical_domain

UA = {"User-Agent": "intel-bot/1.0 (+github actions)"}

def fetch_rss(url: str):
    parsed = feedparser.parse(url)
    for e in parsed.entries[:30]:
        yield {
            "title": e.get("title"),
            "link": e.get("link"),
            "author": e.get("author") or e.get("source",{}).get("title") or "",
            "published": e.get("published") or e.get("updated") or "",
            "summary_html": e.get("summary") or e.get("content",[{}])[0].get("value",""),
        }

def fetch_html_page(url: str):
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else url
    paras = [p.get_text(" ", strip=True) for p in soup.select("p")]
    body = " ".join(paras[:6])
    return {"title": title, "link": url, "author":"", "published":"", "summary_html": body}
