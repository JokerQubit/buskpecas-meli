#!/usr/bin/env python3
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

code = "1450065"
url = f"https://kostalbrasil.com.br/busca-avancada2/busca/?codigo={code}"
print(f"[*] Buscando na Kostal: {url}")

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='replace')

soup = BeautifulSoup(html, "html.parser")
print("Title:", soup.title.string if soup.title else "No title")

# Procura links de produto
prod_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/produto/" in href:
        if not href.startswith("http"):
            href = f"https://kostalbrasil.com.br{href}"
        if href not in prod_links:
            prod_links.append(href)

print("Product links found:", len(prod_links))
for pl in prod_links:
    print("  ->", pl)

# Procura imagens de produto na página
imgs = []
for img in soup.find_all("img"):
    src = img.get("src") or img.get("data-src")
    if src and "upload_arquivos" in src:
        if not src.startswith("http"):
            src = f"https://kostalbrasil.com.br{src}"
        if src not in imgs:
            imgs.append(src)

print("Direct images in search:", len(imgs))
for i in imgs:
    print("  IMG:", i)

# Se tiver link de produto, entra e pega todas as fotos da galeria
if prod_links:
    target_url = prod_links[0]
    print(f"\n[*] Acessando página do produto: {target_url}")
    p_req = urllib.request.Request(target_url, headers=headers)
    with urllib.request.urlopen(p_req, timeout=15) as p_resp:
        p_html = p_resp.read().decode('utf-8', errors='replace')
    p_soup = BeautifulSoup(p_html, "html.parser")
    
    gallery_imgs = []
    for img in p_soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and "upload_arquivos" in src:
            if not src.startswith("http"):
                src = f"https://kostalbrasil.com.br{src}"
            if src not in gallery_imgs:
                gallery_imgs.append(src)
    
    print(f"Gallery images found ({len(gallery_imgs)}):")
    for gi in gallery_imgs:
        print("  ->", gi)
