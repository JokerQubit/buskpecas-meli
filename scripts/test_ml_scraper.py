#!/usr/bin/env python3
"""
scripts/test_ml_scraper.py
--------------------------
Testa a extração e download de imagens em alta resolução do Mercado Livre
para uma peça de teste (ex: PECA_01 Kostal 10013879).
"""

import os
import re
import sys
import json
import requests
from bs4 import BeautifulSoup

# Headers simulando um navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}


def search_and_get_ml_images(query: str, max_images: int = 4):
    url = f"https://lista.mercadolivre.com.br/{requests.utils.quote(query)}"
    print(f"[*] Buscando no Mercado Livre: {url}")
    
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"[!] Erro ao acessar busca ML: status {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Encontra o primeiro anúncio da lista
    links = soup.find_all("a", href=True)
    product_url = None
    for a in links:
        href = a["href"]
        if "/MLB-" in href or "/p/MLB" in href:
            product_url = href.split("?")[0]
            break

    if not product_url:
        print(f"[!] Nenhum link de produto MLB encontrado para a busca '{query}'.")
        return []

    print(f"[✓] Produto encontrado: {product_url}")
    
    # Acessa a página do produto
    prod_resp = requests.get(product_url, headers=HEADERS, timeout=15)
    if prod_resp.status_code != 200:
        print(f"[!] Erro ao acessar página do produto: status {prod_resp.status_code}")
        return []

    prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
    
    # Busca todas as imagens de alta resolução da galeria (D_NQ_NP_2X_... ou D_NQ_NP_...-O.webp)
    image_urls = []
    
    # Método 1: Busca em tags img com data-zoom ou src de alta resolução
    for img in prod_soup.find_all("img"):
        src = img.get("data-zoom") or img.get("src") or img.get("data-src")
        if src and "http2.mlstatic.com/D_NQ_NP" in src:
            # Converte para resolução máxima (2X ou -O / -F)
            high_res = re.sub(r"/D_NQ_NP_\d+_", "/D_NQ_NP_2X_", src)
            high_res = re.sub(r"-\w\.(webp|jpg|png)", "-O.webp", high_res)
            if high_res not in image_urls:
                image_urls.append(high_res)

    # Método 2: Regex no JSON embutido na página (__PRELOADED_STATE__ ou initial-state)
    if not image_urls:
        matches = re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[^"\',]+\.(?:webp|jpg|png)', prod_resp.text)
        for m in matches:
            high_res = re.sub(r"/D_NQ_NP_\d+_", "/D_NQ_NP_2X_", m)
            high_res = re.sub(r"-\w\.(webp|jpg|png)", "-O.webp", high_res)
            if high_res not in image_urls:
                image_urls.append(high_res)

    print(f"[✓] Encontradas {len(image_urls)} imagens em alta resolução.")
    return image_urls[:max_images]


if __name__ == "__main__":
    test_query = "Kostal 10013879 Celta"
    imgs = search_and_get_ml_images(test_query)
    for idx, img in enumerate(imgs, start=1):
        print(f"  Slide {idx}: {img}")
