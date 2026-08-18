#!/usr/bin/env python3
"""
scripts/normalize_slide_names.py
--------------------------------
Normaliza os nomes de todas as fotos reais para 'slide 1.png', 'slide 2.png', 'slide 3.png'...
e posiciona 'qualidade.png' e 'GARANTIA.png' no final de cada pasta com numeração sequencial perfeita.
"""

import os
import sys
import shutil
from PIL import Image

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

IMAGES_DIR = "images"
MASTER_QUALIDADE = os.path.join(IMAGES_DIR, "qualidade.png")
MASTER_GARANTIA = os.path.join(IMAGES_DIR, "GARANTIA.png")


def normalize_all():
    qualidade_size = os.path.getsize(MASTER_QUALIDADE)
    garantia_size = os.path.getsize(MASTER_GARANTIA)

    folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith("PECA_") and os.path.isdir(os.path.join(IMAGES_DIR, f))]
    folders.sort(key=lambda x: int(x.split("_")[1]))

    for folder in folders:
        folder_path = os.path.join(IMAGES_DIR, folder)
        files = os.listdir(folder_path)

        real_photos = []
        for f in files:
            f_lower = f.lower()
            if f_lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
                fp = os.path.join(folder_path, f)
                f_size = os.path.getsize(fp)
                if f_size != qualidade_size and f_size != garantia_size:
                    real_photos.append(f)
                else:
                    os.remove(fp)

        if not real_photos:
            continue

        real_photos.sort()
        temp_renames = []

        # 1. Renomeia para nomes temporários para evitar conflitos de sobreposição
        for idx, rf in enumerate(real_photos, start=1):
            src = os.path.join(folder_path, rf)
            tmp_name = f"__temp_slide_{idx}.png"
            tmp_path = os.path.join(folder_path, tmp_name)
            
            # Converte qualquer formato (WEBP/JPG) para PNG de alta qualidade
            try:
                with Image.open(src) as img:
                    img.save(tmp_path, "PNG")
                if src != tmp_path and os.path.exists(src):
                    os.remove(src)
                temp_renames.append(tmp_path)
            except Exception as e:
                # Se falhar a conversão PIL, move o arquivo
                os.rename(src, tmp_path)
                temp_renames.append(tmp_path)

        # 2. Renomeia de temporário para 'slide X.png'
        for idx, tmp_p in enumerate(temp_renames, start=1):
            final_p = os.path.join(folder_path, f"slide {idx}.png")
            if os.path.exists(final_p):
                os.remove(final_p)
            os.rename(tmp_p, final_p)

        # 3. Adiciona os slides master no final
        next_idx = len(temp_renames) + 1
        shutil.copy2(MASTER_QUALIDADE, os.path.join(folder_path, f"slide {next_idx}.png"))
        shutil.copy2(MASTER_GARANTIA, os.path.join(folder_path, f"slide {next_idx + 1}.png"))

    print("[✓] Todas as fotos reais foram normalizadas para 'slide 1.png', 'slide 2.png'... em alta definição!")


if __name__ == "__main__":
    normalize_all()
