#!/usr/bin/env python3
import urllib.request
import re
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

url = "https://kostalbrasil.com.br/produto/28/chave-de-seta-1450065"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='replace')

soup = BeautifulSoup(html, "html.parser")
print("All img tags in product page:")
for img in soup.find_all("img"):
    print("  IMG src:", img.get("src"), "data-src:", img.get("data-src"), "class:", img.get("class"))

print("\nLooking for background-image or slider data in HTML:")
bg_matches = re.findall(r'url\([\'"]?([^\'")\s]+)[\'"]?\)', html)
for bg in bg_matches:
    print("  BG:", bg)

print("\nLooking for image extensions in HTML:")
all_imgs = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|png|webp|jpeg)', html, re.IGNORECASE)
for ai in all_imgs:
    print("  EXT:", ai)
