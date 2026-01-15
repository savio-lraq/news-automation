import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

RSS_URL = "https://www.shafaq.com/rss/ar/%D9%85%D8%AC%D8%AA%D9%80%D9%85%D8%B9"

def clean_html(text: str) -> str:
    """
    تنظيف الوصف من HTML وخصائص مثل style=
    بدون أي مكتبات إضافية.
    """
    if not text:
        return ""

    # فك أشهر الـ HTML entities
    text = (text.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&lt;", "<")
                .replace("&gt;", ">"))

    # إزالة أي style="..." أو style='...'
    text = re.sub(r'\sstyle=(".*?"|\'.*?\')', '', text, flags=re.IGNORECASE)

    # تحويل <br> و <p> إلى سطور/مسافات
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*p[^>]*>", "", text, flags=re.IGNORECASE)

    # إزالة أي وسوم HTML أخرى
    text = re.sub(r"<[^>]+>", "", text)

    # تنظيف المسافات الزائدة والأسطر الفارغة
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    return text

def main():
    r = requests.get(RSS_URL, timeout=30)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("RSS: لم يتم العثور على channel")

    item = channel.find("item")
    if item is None:
        raise RuntimeError("RSS: لم يتم العثور على أي item")

    title = (item.findtext("title", default="") or "").strip()
    link = (item.findtext("link", default="") or "").strip()
    desc = (item.findtext("description", default="") or "").strip()

    data = {
        "source_rss": RSS_URL,
        "title": title,
        "link": link,
        "description": clean_html(desc),
        "fetched_at_utc": datetime.utcnow().isoformat() + "Z"
    }

    with open("news_latest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved: news_latest.json")
    print("Title:", title)

if __name__ == "__main__":
    main()
