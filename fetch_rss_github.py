import requests
import xml.etree.ElementTree as ET
import json
import re
import os
import hashlib
from datetime import datetime, timezone

RSS_URL = "https://www.shafaq.com/rss/ar/%D9%85%D8%AC%D8%AA%D9%80%D9%85%D8%B9"
OUT_DIR = "out/news"

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = (text.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&lt;", "<")
                .replace("&gt;", ">"))
    text = re.sub(r'\sstyle=(".*?"|\'.*?\')', '', text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*p[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text

def pick_image_url(item: ET.Element) -> str | None:
    """
    يحاول استخراج صورة من RSS إذا كانت موجودة.
    لا يولد أي صور.
    """
    # 1) media:content أو media:thumbnail (namespaces)
    for tag in ["{http://search.yahoo.com/mrss/}content", "{http://search.yahoo.com/mrss/}thumbnail"]:
        el = item.find(tag)
        if el is not None:
            url = (el.attrib.get("url") or "").strip()
            if url:
                return url

    # 2) enclosure url
    enc = item.find("enclosure")
    if enc is not None:
        url = (enc.attrib.get("url") or "").strip()
        if url:
            return url

    # 3) محاولة من داخل description (img src)
    desc = item.findtext("description", default="") or ""
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()

    return None

def make_id(link: str) -> str:
    return hashlib.sha1(link.encode("utf-8")).hexdigest()[:16]

def safe_filename(s: str) -> str:
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.UNICODE)
    return s.strip("_")[:80] or "news"

def main():
    r = requests.get(RSS_URL, timeout=30)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("RSS: لم يتم العثور على channel")

    items = channel.findall("item")
    if not items:
        raise RuntimeError("RSS: لم يتم العثور على أي item")

    os.makedirs(OUT_DIR, exist_ok=True)

    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    saved = 0
    for it in items:
        title = (it.findtext("title", default="") or "").strip()
        link = (it.findtext("link", default="") or "").strip()
        desc = (it.findtext("description", default="") or "").strip()
        pub = (it.findtext("pubDate", default="") or "").strip()

        if not link:
            # بدون رابط لا نقدر نضمن id ثابت
            continue

        news_id = make_id(link)
        image_url = pick_image_url(it)

        data = {
            "id": news_id,
            "type": "normal",  # لاحقًا سنحدد عاجل/عادي بقواعد بسيطة
            "source_rss": RSS_URL,
            "title": title,
            "link": link,
            "description": clean_html(desc),
            "image_url": image_url,              # إن وجدت، وإلا null
            "fallback_image": "assets/fallback.png",
            "published_at": pub,
            "fetched_at_utc": now_utc
        }

        filename = f"{news_id}__{safe_filename(title)}.json"
        path = os.path.join(OUT_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        saved += 1

    # (اختياري) نكتب أيضًا ملف “آخر دفعة” للمراجعة
    latest_path = "news_latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump({"count": saved, "fetched_at_utc": now_utc}, f, ensure_ascii=False, indent=2)

    print(f"Saved {saved} files into: {OUT_DIR}")
    print("Updated:", latest_path)

if __name__ == "__main__":
    main()
