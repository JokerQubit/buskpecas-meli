#!/usr/bin/env python3
"""
scripts/test_image_downloader.py
--------------------------------
Testa múltiplos métodos para buscar e baixar fotos reais de produtos automotivos:
1. Catálogos diretos de fabricantes (Sabó, Arteb, Kostal);
2. APIs públicas de busca de imagens;
3. Cópia automática dos slides master (qualidade.png e GARANTIA.png).
"""

import os
import re
import sys
import json
import urllib.parse
import urllib.request
import shutil

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

IMAGES_DIR = "images"
MASTER_QUALIDADE = os.path.join(IMAGES_DIR, "qualidade.png")
MASTER_GARANTIA = os.path.join(IMAGES_DIR, "GARANTIA.png")


def test_copy_master_slides(peca_folder_name: str):
    """
    Copia os designs master já criados para dentro da pasta da peça
    garantindo que toda pasta tenha os slides institucionais da BUSK Peças.
    """
    target_dir = os.path.join(IMAGES_DIR, peca_folder_name)
    if not os.path.exists(target_dir):
        print(f"[!] Pasta não encontrada: {target_dir}")
        return

    # Descobre quantos slides já existem na pasta
    existing_slides = [f for f in os.listdir(target_dir) if f.lower().startswith("slide") and f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"[*] Slides já existentes em {peca_folder_name}: {len(existing_slides)}")

    # Define o próximo índice
    next_idx = len(existing_slides) + 1
    
    # Copia qualidade.png
    slide_qualidade = os.path.join(target_dir, f"slide {next_idx}.png")
    shutil.copy2(MASTER_QUALIDADE, slide_qualidade)
    print(f"[✓] Slide {next_idx} criado: {slide_qualidade} (Qualidade)")

    # Copia GARANTIA.png
    next_idx += 1
    slide_garantia = os.path.join(target_dir, f"slide {next_idx}.png")
    shutil.copy2(MASTER_GARANTIA, slide_garantia)
    print(f"[✓] Slide {next_idx} criado: {slide_garantia} (Garantia)")


if __name__ == "__main__":
    test_folder = "PECA_04_FIAT_MOPAR_51997820"
    test_copy_master_slides(test_folder)
