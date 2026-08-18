#!/usr/bin/env python3
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Teste Sabó
code = "80270"
urls_to_test = [
    f"https://www.sabo.com.br/?s={code}",
    f"https://catalogo.sabo.com.br/busca?q={code}",
    f"https://sabo.com.br/produtos/{code}"
]

for u in urls_to_test:
    print(f"[*] Testando URL Sabó: {u}")
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  [✓] Status OK: {resp.status} (Length: {len(resp.read())})")
    except Exception as e:
        print(f"  [!] Erro: {e}")
