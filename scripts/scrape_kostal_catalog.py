#!/usr/bin/env python3
"""
scripts/scrape_kostal_catalog.py
--------------------------------
Automação para buscar e baixar todas as imagens de alta resolução
diretamente do catálogo oficial Kostal Brasil (https://kostalbrasil.com.br/).

Varre as peças Kostal cadastradas no banco de dados (Peças 16 a 43)
e salva as imagens em 'images/PECA_[ID].../slide 1.png', 'slide 2.png'...
seguidas dos slides master de qualidade e garantia!
"""

import os
import re
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from PIL import Image

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
IMAGES_DIR = "images"
MASTER_QUALIDADE = os.path.join(IMAGES_DIR, "qualidade.png")
MASTER_GARANTIA = os.path.join(IMAGES_DIR, "GARANTIA.png")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9"
}


def search_kostal_product(codigo: str):
    """
    Busca o produto no catálogo da Kostal pelo código e retorna a lista de URLs de imagens em alta resolução.
    """
    search_url = f"https://kostalbrasil.com.br/busca?q={urllib.parse.quote(codigo)}"
    print(f"[*] Buscando no catálogo Kostal: {search_url}")
    
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[!] Erro ao buscar no catálogo Kostal para '{codigo}': {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Procura links de produtos na página de busca
    prod_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/produto/" in href:
            if href.startswith("http"):
                prod_links.append(href)
            else:
                prod_links.append(f"https://kostalbrasil.com.br{href}")

    # Se encontrou links de produto, acessa a página do produto
    image_urls = []
    
    if prod_links:
        # Pega o primeiro produto compatível
        target_prod_url = prod_links[0]
        print(f"[✓] Página do produto encontrada: {target_prod_url}")
        
        prod_req = urllib.request.Request(target_prod_url, headers=HEADERS)
        try:
            with urllib.request.urlopen(prod_req, timeout=15) as prod_resp:
                prod_html = prod_resp.read().decode("utf-8", errors="replace")
                prod_soup = BeautifulSoup(prod_html, "html.parser")
                
                # Procura todas as imagens na página do produto (upload_arquivos)
                for img in prod_soup.find_all("img"):
                    src = img.get("src") or img.get("data-src")
                    if src and "upload_arquivos" in src:
                        if not src.startswith("http"):
                            src = f"https://kostalbrasil.com.br{src}"
                        if src not in image_urls:
                            image_urls.append(src)
        except Exception as e:
            print(f"[!] Erro ao acessar página do produto Kostal: {e}")

    # Método de fallback: busca todas as imagens com 'upload_arquivos' no HTML de busca
    if not image_urls:
        matches = re.findall(r'https?://kostalbrasil\.com\.br/upload_arquivos/[^"\'\s]+\.(?:jpg|png|webp|jpeg)', html)
        for m in matches:
            if m not in image_urls and "logo" not in m.lower() and "banner" not in m.lower():
                image_urls.append(m)

    return image_urls


def download_and_save_images(folder_path: str, image_urls: list):
    """
    Baixa as imagens, converte para PNG e organiza como 'slide 1.png', 'slide 2.png'...
    adicionando 'qualidade.png' e 'GARANTIA.png' no final.
    """
    if not image_urls:
        return False

    temp_files = []
    for idx, url in enumerate(image_urls, start=1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            
            temp_path = os.path.join(folder_path, f"__temp_{idx}.png")
            with open(temp_path, "wb") as f:
                f.write(data)
            
            # Converte com PIL para PNG padronizado
            with Image.open(temp_path) as img:
                img.save(temp_path, "PNG")
            
            temp_files.append(temp_path)
        except Exception as e:
            print(f"[!] Erro ao baixar imagem {url}: {e}")

    if not temp_files:
        return False

    # Remove slides antigos da pasta
    qualidade_size = os.path.getsize(MASTER_QUALIDADE)
    garantia_size = os.path.getsize(MASTER_GARANTIA)
    
    for f in os.listdir(folder_path):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".url")):
            fp = os.path.join(folder_path, f)
            if not f.startswith("__temp_"):
                os.remove(fp)

    # Renomeia para slide 1.png, slide 2.png...
    for idx, tmp_p in enumerate(temp_files, start=1):
        final_p = os.path.join(folder_path, f"slide {idx}.png")
        os.rename(tmp_p, final_p)

    # Adiciona slides master no final
    next_idx = len(temp_files) + 1
    shutil.copy2(MASTER_QUALIDADE, os.path.join(folder_path, f"slide {next_idx}.png"))
    shutil.copy2(MASTER_GARANTIA, os.path.join(folder_path, f"slide {next_idx + 1}.png"))

    print(f"[✓] {len(temp_files)} fotos oficiais Kostal baixadas + 2 slides master vinculados em {folder_path}!")
    return True


if __name__ == "__main__":
    test_code = "1450065"
    imgs = search_kostal_product(test_code)
    print(f"Resultado para {test_code}: {len(imgs)} imagens encontradas:")
    for i in imgs:
        print("  -", i)
