#!/usr/bin/env python3
"""
scripts/validate_downloaded_images.py
-------------------------------------
1. Converte automaticamente qualquer atalho '.url' arrastado pelo usuário
   no arquivo de imagem real (.jpg/.png) em alta resolução;
2. Valida a integridade das imagens salvas (dimensões, tamanho, se abre sem corromper);
3. Sincroniza a numeração 'slide 1', 'slide 2'... + 'qualidade.png' + 'GARANTIA.png'.
"""

import os
import re
import sys
import json
import sqlite3
import urllib.request
import shutil
from PIL import Image

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

IMAGES_DIR = "images"
DB_PATH = os.path.join("database", "autoparts_master.db")
MASTER_QUALIDADE = os.path.join(IMAGES_DIR, "qualidade.png")
MASTER_GARANTIA = os.path.join(IMAGES_DIR, "GARANTIA.png")


def download_url_shortcuts():
    """
    Varre todas as pastas e baixa os arquivos de imagem a partir de arquivos .url.
    """
    folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith("PECA_") and os.path.isdir(os.path.join(IMAGES_DIR, f))]
    converted = 0

    for folder in folders:
        folder_path = os.path.join(IMAGES_DIR, folder)
        url_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".url")]

        for idx, uf in enumerate(url_files, start=1):
            uf_path = os.path.join(folder_path, uf)
            try:
                with open(uf_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                match = re.search(r"URL=(https?://[^\r\n]+)", content)
                if match:
                    img_url = match.group(1).strip()
                    print(f"[*] Baixando imagem real de atalho .url em {folder}: {img_url}")
                    
                    # Nome do arquivo de saída
                    ext = ".jpg"
                    if ".png" in img_url.lower():
                        ext = ".png"
                    elif ".webp" in img_url.lower():
                        ext = ".webp"
                    
                    out_img_name = f"slide {idx}{ext}"
                    out_img_path = os.path.join(folder_path, out_img_name)
                    
                    req = urllib.request.Request(img_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        with open(out_img_path, "wb") as out_f:
                            out_f.write(resp.read())
                    
                    # Remove o atalho .url
                    os.remove(uf_path)
                    converted += 1
                    print(f"[✓] Imagem salva com sucesso: {out_img_name}")
            except Exception as e:
                print(f"[!] Erro ao baixar atalho {uf} em {folder}: {e}")

    if converted > 0:
        print(f"[✓] Total de atalhos .url convertidos em imagens reais: {converted}")


def audit_images_01_to_18():
    download_url_shortcuts()

    # Roda clean_and_sync
    qualidade_size = os.path.getsize(MASTER_QUALIDADE)
    garantia_size = os.path.getsize(MASTER_GARANTIA)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    report = []
    print("\n" + "=" * 80)
    print("🔍 AUDITORIA VISUAL DAS PEÇAS 01 A 18")
    print("=" * 80)

    for peca_id in range(1, 19):
        c.execute("SELECT id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante FROM tb_pecas WHERE id = ?;", (peca_id,))
        peca = c.fetchone()
        if not peca:
            continue

        folder_name = [f for f in os.listdir(IMAGES_DIR) if f.startswith(f"PECA_{peca_id:02d}_")][0]
        folder_path = os.path.join(IMAGES_DIR, folder_name)
        files = os.listdir(folder_path)

        real_photos = []
        master_photos = []

        for f in files:
            f_lower = f.lower()
            if f_lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
                fp = os.path.join(folder_path, f)
                f_size = os.path.getsize(fp)
                if f_size == qualidade_size or f_size == garantia_size:
                    master_photos.append(f)
                else:
                    try:
                        with Image.open(fp) as img:
                            w, h = img.size
                            fmt = img.format
                            real_photos.append((f, f"{w}x{h}", fmt, f_size))
                    except Exception as e:
                        real_photos.append((f, "CORROMPIDA", "ERR", f_size))

        # Reorganiza masters
        for mf in master_photos:
            os.remove(os.path.join(folder_path, mf))

        if real_photos:
            next_idx = len(real_photos) + 1
            shutil.copy2(MASTER_QUALIDADE, os.path.join(folder_path, f"slide {next_idx}.png"))
            shutil.copy2(MASTER_GARANTIA, os.path.join(folder_path, f"slide {next_idx + 1}.png"))
            total_slides = len(real_photos) + 2
        else:
            total_slides = 0

        status_str = f"✅ {len(real_photos)} fotos reais + 2 slides master ({total_slides} slides no total)" if real_photos else "⚠️ Vazia"
        print(f"\n[Peça {peca_id:02d}] {peca['marca_fabricante']} {peca['codigo_fabricante']} - {peca['nome_comercial_base'][:45]}...")
        print(f"  Status: {status_str}")
        for rf_name, rf_dims, rf_fmt, rf_size in real_photos:
            print(f"    📸 {rf_name} -> Resolução: {rf_dims} | Formato: {rf_fmt} | Tamanho: {rf_size / 1024:.1f} KB")

        report.append({
            "id": peca_id,
            "sku": peca["sku_master"],
            "marca": peca["marca_fabricante"],
            "codigo": peca["codigo_fabricante"],
            "nome": peca["nome_comercial_base"],
            "fotos_reais_count": len(real_photos),
            "fotos_detalhes": real_photos,
            "total_slides": total_slides
        })

    conn.close()
    return report


if __name__ == "__main__":
    audit_images_01_to_18()
