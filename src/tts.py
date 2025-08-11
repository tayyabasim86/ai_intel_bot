from gtts import gTTS

def synthesize_tts(text: str, out_path: str, lang: str = "en", slow: bool = False) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(out_path)
    return out_path
