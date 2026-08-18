#!/usr/bin/env python3
import urllib.request
import re
import sys
from bs4 import BeautifulSoup

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

url = "https://www.sabo.com.br/?s=80270"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='replace')

soup = BeautifulSoup(html, "html.parser")
print("Title:", soup.title.string if soup.title else "No title")

# Procura links e imagens
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "sabo.com.br" in href and any(k in href for k in ["produto", "catalogo", "80270"]):
        print("Link:", href)

imgs = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|png|webp)', html)
print("Images found:", len(imgs))
for i in imgs[:5]:
    print("  ->", i)
