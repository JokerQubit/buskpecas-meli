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

url = "https://catalogo.sabo.com.br/"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    print("Catalog HTML length:", len(html))
    # Procura scripts e APIs
    scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
    print("Scripts found:", len(scripts))
    for s in scripts[:5]:
        print("  JS:", s)
except Exception as e:
    print("Erro Sabo catalogo:", e)
