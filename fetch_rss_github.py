import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

RSS_URL = "https://www.shafaq.com/rss/ar/%D9%85%D8%AC%D8%AA%D9%80%D9%85%D8%B9"

def clean_html(text: str) -> str:
    if not text:
        return ""
    # تنظيف بسيط جدًا بدون مكتبات إضافية
    return (text.replace("<p", " ").replace("</p>", " ")
                .replace("<br>", " ").replace("&nbsp;", " ")
                .replace("&amp;", "&").replace("&quot;", '"')
                .replace("&lt;", "<").replace("&gt;", ">"))

def main():
    r = requests.get(RSS_URL, timeout=30)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    channel = root.find("channel")
    item = channel.find("item")

    title = item.findtext("title", default="").strip()
    link = item.findtext("link", default="").strip()
    desc = item.findtext("description", default="").strip()

    data = {
        "source_rss": RSS_URL,
        "title": title,
        "link": link,
        "description": clean_html(desc),
        "fetched_at_utc": datetime.utcnow().isoformat() + "Z"
    }

    # حفظ داخل المستودع
    with open("news_latest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved: news_latest.json")
    print("Title:", title)

if __name__ == "__main__":
    main()
