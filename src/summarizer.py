import os, re
from util import strip_html

def _fallback_extractive(text: str, max_sents: int = 4) -> str:
    if not text:
        return ""
    sents = re.split(r'(?<=[.!?])\s+', text)
    sents = [s.strip() for s in sents if s.strip()]
    seen = set()
    scored = []
    for s in sents:
        key = s.lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        scored.append((min(len(s), 220), s))
    top = [s for _, s in sorted(scored, reverse=True)[:max_sents]]
    return "TL;DR (extractive)\n- " + "\n- ".join(top)

def gemini_summary(text: str) -> str:
    import google.generativeai as genai
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("No GEMINI_API_KEY")
    genai.configure(api_key=key)
    prompt = f"""You are an expert analyst. Summarize the content into:
- TL;DR (1–2 lines)
- 3–5 bullets (key facts only)
- Why it matters (1 line)
Return plain text only.
CONTENT:
{text[:12000]}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    out = model.generate_content(prompt).text or ""
    if not out.strip():
        raise RuntimeError("Empty LLM response")
    return out.strip()

def summarize(html_or_text: str) -> str:
    text = strip_html(html_or_text or "")
    try:
        if os.getenv("GEMINI_API_KEY"):
            return gemini_summary(text)
    except Exception as e:
        print("[WARN] LLM summarization failed, using fallback:", e)
    return _fallback_extractive(text)
