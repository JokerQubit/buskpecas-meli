#!/usr/bin/env python3
import urllib.request
import re

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://catalogo.sabo.com.br/main.13220236f8b988a0.js"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    js = resp.read().decode('utf-8', errors='replace')

matches = set(re.findall(r'https?://[a-zA-Z0-9\.\-_/]+', js))
for m in matches:
    if "sabo" in m.lower() or "catalogo" in m.lower() or "aws" in m.lower():
        print("URL Match:", m)
