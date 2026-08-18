#!/usr/bin/env python3
import urllib.request
import re
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

url = "https://kostalbrasil.com.br/"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='replace')

soup = BeautifulSoup(html, "html.parser")
print("Title:", soup.title.string if soup.title else "No title")

# Procura forms e inputs
forms = soup.find_all("form")
print("Forms found:", len(forms))
for f in forms:
    print("Form action:", f.get("action"), "method:", f.get("method"))
    for inp in f.find_all(["input", "select"]):
        print("  Input:", inp.get("name"), inp.get("type"))

# Procura links com /produto/
links = soup.find_all("a", href=True)
prod_links = [a["href"] for a in links if "/produto" in a["href"]]
print("Sample product links:", prod_links[:5])
