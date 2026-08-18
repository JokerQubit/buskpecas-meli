#!/usr/bin/env python3
"""
scripts/clean_and_sync_slides.py
--------------------------------
Limpa as pastas que NÃO possuem fotos reais de produtos (evitando que 'qualidade.png' e 'GARANTIA.png'
fiquem como slide 1 e slide 2).

Quando o usuário adiciona fotos reais do produto (ex: 'slide 1.png', 'foto1.jpg', etc.),
o script sincroniza automaticamente 'qualidade.png' e 'GARANTIA.png' como os ÚLTIMOS slides da sequência.
"""

import os
import sys
import shutil

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

IMAGES_DIR = "images"
MASTER_QUALIDADE = os.path.join(IMAGES_DIR, "qualidade.png")
MASTER_GARANTIA = os.path.join(IMAGES_DIR, "GARANTIA.png")


def clean_and_sync():
    if not os.path.exists(MASTER_QUALIDADE) or not os.path.exists(MASTER_GARANTIA):
        print(f"[!] Erro: Master slides não encontrados em '{IMAGES_DIR}'.")
        return

    qualidade_size = os.path.getsize(MASTER_QUALIDADE)
    garantia_size = os.path.getsize(MASTER_GARANTIA)

    folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith("PECA_") and os.path.isdir(os.path.join(IMAGES_DIR, f))]
    folders.sort(key=lambda x: int(x.split("_")[1]))

    print(f"[*] Verificando e organizando {len(folders)} pastas de imagens...")

    folders_with_real_photos = 0
    folders_cleaned = 0

    for folder in folders:
        folder_path = os.path.join(IMAGES_DIR, folder)
        files = os.listdir(folder_path)

        real_product_photos = []
        master_copies = []

        for f in files:
            f_lower = f.lower()
            if f_lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
                fp = os.path.join(folder_path, f)
                f_size = os.path.getsize(fp)
                if f_size == qualidade_size or f_size == garantia_size:
                    master_copies.append(fp)
                else:
                    real_product_photos.append(f)

        # Remove todas as cópias antigas de master para reordenar limpo
        for mc in master_copies:
            os.remove(mc)

        # Se houver fotos reais do produto colocadas pelo usuário:
        if real_product_photos:
            folders_with_real_photos += 1
            real_product_photos.sort()
            next_idx = len(real_product_photos) + 1
            
            # Adiciona qualidade.png e GARANTIA.png no final da fila
            shutil.copy2(MASTER_QUALIDADE, os.path.join(folder_path, f"slide {next_idx}.png"))
            shutil.copy2(MASTER_GARANTIA, os.path.join(folder_path, f"slide {next_idx + 1}.png"))
            print(f"[✓] {folder}: {len(real_product_photos)} fotos reais + 2 slides master adicionados.")
        else:
            folders_cleaned += 1

    print(f"\n[✓] Organização concluída!")
    print(f"    - Pastas com fotos reais sincronizadas: {folders_with_real_photos}")
    print(f"    - Pastas vazias limpas e prontas para receber fotos: {folders_cleaned}")


if __name__ == "__main__":
    clean_and_sync()
