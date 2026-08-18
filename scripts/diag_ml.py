#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

url = "https://lista.mercadolivre.com.br/10013879"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.string if soup.title else "No title")
print("Sample HTML:", r.text[:500])
