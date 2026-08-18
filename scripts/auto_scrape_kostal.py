#!/usr/bin/env python3
"""
scripts/auto_scrape_kostal.py
-----------------------------
Automação completa para extrair e baixar todas as fotos oficiais em alta resolução
do catálogo oficial Kostal Brasil (https://kostalbrasil.com.br/) para todas as peças Kostal.

1. Varre o banco de dados 'database/autoparts_master.db' buscando peças da marca Kostal;
2. Consulta o endpoint 'https://kostalbrasil.com.br/busca-avancada2/busca/?codigo={codigo}';
3. Extrai todas as imagens da galeria oficial (/upload_arquivos/...);
4. Salva em 'images/PECA_[ID].../' como 'slide 1.png', 'slide 2.png'...;
5. Anexa automaticamente 'qualidade.png' e 'GARANTIA.png' no final do carrossel!
"""

import os
import re
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
import shutil
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9"
}


def get_kostal_gallery_urls(codigo: str):
    """
    Busca o produto no endpoint da Kostal e extrai todas as URLs de imagens da galeria.
    """
    search_url = f"https://kostalbrasil.com.br/busca-avancada2/busca/?codigo={urllib.parse.quote(codigo)}"
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [!] Erro na busca Kostal ({codigo}): {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    
    # Encontra o link do produto
    prod_url = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/produto/" in href:
            if not href.startswith("http"):
                prod_url = f"https://kostalbrasil.com.br{href}"
            else:
                prod_url = href
            break

    if not prod_url:
        # Fallback: busca imagens diretas no HTML de busca
        imgs = re.findall(r'/upload_arquivos/[^\s"\'<>]+\.(?:jpg|png|webp|jpeg)', html, re.IGNORECASE)
        clean_imgs = []
        for img_rel in imgs:
            full_url = f"https://kostalbrasil.com.br{img_rel}"
            if full_url not in clean_imgs:
                clean_imgs.append(full_url)
        return clean_imgs

    # Acessa a página do produto
    try:
        p_req = urllib.request.Request(prod_url, headers=HEADERS)
        with urllib.request.urlopen(p_req, timeout=15) as p_resp:
            p_html = p_resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [!] Erro ao abrir página do produto ({prod_url}): {e}")
        return []

    # Extrai imagens de background e de img tags
    bg_matches = re.findall(r'/upload_arquivos/[^\s"\'()<>]+\.(?:jpg|png|webp|jpeg)', p_html, re.IGNORECASE)
    
    gallery = []
    for m in bg_matches:
        full_u = f"https://kostalbrasil.com.br{m}"
        if full_u not in gallery:
            gallery.append(full_u)

    return gallery


def scrape_all_kostal():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Seleciona todas as peças Kostal cadastradas
    c.execute("SELECT id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante FROM tb_pecas WHERE marca_fabricante LIKE '%Kostal%' ORDER BY id ASC;")
    pecas = c.fetchall()
    conn.close()

    print("=" * 80)
    print(f"🚀 INICIANDO SCRAPER AUTOMATIZADO KOSTAL BRASIL ({len(pecas)} PEÇAS)")
    print("=" * 80)

    sucesso = 0
    falhas = 0

    for peca in pecas:
        p_id = peca["id"]
        cod = peca["codigo_fabricante"]
        nome = peca["nome_comercial_base"]

        # Encontra a pasta da peça em images/
        matching_folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith(f"PECA_{p_id:02d}_")]
        if not matching_folders:
            print(f"[!] Pasta não encontrada para a Peça {p_id:02d}")
            continue

        folder_name = matching_folders[0]
        folder_path = os.path.join(IMAGES_DIR, folder_name)

        print(f"\n[Peça {p_id:02d}] Buscando: Kostal {cod} ({nome[:40]}...)")
        img_urls = get_kostal_gallery_urls(cod)

        if not img_urls:
            print(f"  ⚠️ Nenhuma foto encontrada para Kostal {cod}")
            falhas += 1
            continue

        print(f"  [✓] Encontradas {len(img_urls)} fotos oficiais no catálogo Kostal:")
        
        # Baixa as imagens
        temp_files = []
        for idx, u in enumerate(img_urls, start=1):
            try:
                img_req = urllib.request.Request(u, headers=HEADERS)
                with urllib.request.urlopen(img_req, timeout=15) as resp:
                    raw_bytes = resp.read()
                
                temp_path = os.path.join(folder_path, f"__temp_{idx}.png")
                with open(temp_path, "wb") as tf:
                    tf.write(raw_bytes)
                
                # Converte com PIL para PNG
                with Image.open(temp_path) as im:
                    im.save(temp_path, "PNG")

                temp_files.append(temp_path)
                print(f"    📸 Foto {idx} baixada: {u.split('/')[-1]}")
            except Exception as e:
                print(f"    [!] Falha no download de {u}: {e}")

        if not temp_files:
            print(f"  ⚠️ Falha ao salvar fotos para Peça {p_id:02d}")
            falhas += 1
            continue

        # Limpa arquivos antigos da pasta
        for f in os.listdir(folder_path):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".url")):
                if not f.startswith("__temp_"):
                    os.remove(os.path.join(folder_path, f))

        # Renomeia para slide 1.png, slide 2.png...
        for idx, tmp_p in enumerate(temp_files, start=1):
            final_name = f"slide {idx}.png"
            os.rename(tmp_p, os.path.join(folder_path, final_name))

        # Adiciona slides master no final
        next_idx = len(temp_files) + 1
        shutil.copy2(MASTER_QUALIDADE, os.path.join(folder_path, f"slide {next_idx}.png"))
        shutil.copy2(MASTER_GARANTIA, os.path.join(folder_path, f"slide {next_idx + 1}.png"))

        print(f"  ✅ Galeria montada com sucesso: {len(temp_files)} fotos de fábrica + 2 slides master!")
        sucesso += 1

    print("\n" + "=" * 80)
    print(f"🏁 SCRAPER KOSTAL CONCLUÍDO:")
    print(f"   - Peças atualizadas com sucesso: {sucesso}")
    print(f"   - Peças sem fotos no catálogo: {falhas}")
    print("=" * 80)


if __name__ == "__main__":
    scrape_all_kostal()
