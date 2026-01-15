import requests
import xml.etree.ElementTree as ET

rss_url = "https://www.shafaq.com/rss/ar/%D9%85%D8%AC%D8%AA%D9%80%D9%85%D8%B9"

print(f"Fetching RSS from: {rss_url}")

response = requests.get(rss_url, timeout=15)
xml_data = response.text

root = ET.fromstring(xml_data)

# البحث عن أول عنصر <item>
item = root.find(".//item")
if item is None:
    print("لم يتم العثور على أي خبر في الـ RSS")
else:
    title = item.find("title").text if item.find("title") is not None else "بدون عنوان"
    link = item.find("link").text if item.find("link") is not None else "بدون رابط"

    print("أول خبر في الـ RSS:")
    print("العنوان:", title)
    print("الرابط:", link)
