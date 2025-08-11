import os, yaml, datetime as dt
from fetch import fetch_rss
from util import strip_html, canonical_domain, compute_key, simple_relevance, now_utc_iso
from summarizer import summarize
from sheets import open_sheet, existing_keys, append_rows
from emailer import send_email
from tts import synthesize_tts

def load_feeds(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("feeds", []))

def compose_digest(items: list[dict]) -> str:
    lines = []
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it['title']} — {it['source']}")
        lines.append(f"   Link: {it['link']}")
        lines.append(it['summary'])
        lines.append("")
    return "\n".join(lines).strip()

def run():
    feeds_file = os.getenv("FEEDS_FILE", "config/feeds.yaml")
    feeds = load_feeds(feeds_file)

    ws = open_sheet()  # uses prefilled defaults if env not set
    known = existing_keys(ws)

    collected = []
    for url in feeds:
        for e in fetch_rss(url):
            title = e.get("title") or ""
            link  = e.get("link") or ""
            source = canonical_domain(link)
            date = e.get("published") or now_utc_iso()
            content = e.get("summary_html") or ""
            key = compute_key(title, source, date)
            if key in known:
                continue
            summary = summarize(content)
            relevance = round(simple_relevance(title + " " + strip_html(content)) * 100, 1)
            item = {
                "Type": "news",
                "Source": source,
                "Title": title,
                "Author/Company": e.get("author",""),
                "Date": date,
                "ExecutiveSummary": summary,
                "BusinessInsight": "",
                "RelevanceScore": relevance,
                "Link": link,
                "CanonicalLink": link,
                "PrimaryOrSecondary": "Primary",
                "DedupeKey": key,
                "Status": "New",
            }
            collected.append(item)

    collected.sort(key=lambda x: x["RelevanceScore"], reverse=True)
    top_n = int(os.getenv("DIGEST_TOP_N", "3"))
    top = collected[:top_n]

    def to_row(it):
        return [it[h] for h in ['Type','Source','Title','Author/Company','Date','ExecutiveSummary','BusinessInsight','RelevanceScore','Link','CanonicalLink','PrimaryOrSecondary','DedupeKey','Status']]
    if collected:
        append_rows(ws, [to_row(it) for it in collected])

    subject = f"AI highlights — {dt.datetime.utcnow().date()}"
    body = compose_digest([{"title": it["Title"], "source": it["Source"], "link": it["Link"], "summary": it["ExecutiveSummary"]} for it in top]) or "No new items."
    to_addr = os.getenv("GMAIL_TO")
    if not to_addr:
        raise RuntimeError("GMAIL_TO not set")
    attach_tts = os.getenv("ATTACH_TTS","true").lower()=="true"
    attach = None
    if attach_tts and body.strip():
        try:
            fname = f"digest_{dt.datetime.utcnow().strftime('%Y%m%d_%H%M')}.mp3"
            attach = synthesize_tts(body, fname)
        except Exception as e:
            print("[WARN] TTS failed:", e)
            attach = None
    send_email(subject, body, [to_addr], attach_path=attach)
    print(f"[INFO] Sent email to {to_addr} with {len(top)} items.")

if __name__ == "__main__":
    run()
