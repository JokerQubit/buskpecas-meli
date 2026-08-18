#!/usr/bin/env python3
"""
scripts/sync_master_branding_slides.py
--------------------------------------
Sincroniza automaticamente os slides institucionais criados pelo usuário:
- 'images/qualidade.png' -> (Slide de Apresentação de Qualidade e Padrão)
- 'images/GARANTIA.png'  -> (Slide Final de Fechamento de Venda, Envio 24h e Garantia)

Para cada uma das 109 pastas de peças em 'images/':
1. Detecta as fotos reais de produto existentes (slide 1.png, slide 2.png...);
2. Remove cópias antigas dos slides institucionais se houver;
3. Adiciona 'qualidade.png' e 'GARANTIA.png' com a numeração sequencial correta.
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


def sync_branding_to_all_folders():
    if not os.path.exists(MASTER_QUALIDADE) or not os.path.exists(MASTER_GARANTIA):
        print(f"[!] Erro: Arquivos master 'qualidade.png' ou 'GARANTIA.png' não encontrados na raiz de '{IMAGES_DIR}'.")
        return

    qualidade_size = os.path.getsize(MASTER_QUALIDADE)
    garantia_size = os.path.getsize(MASTER_GARANTIA)

    folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith("PECA_") and os.path.isdir(os.path.join(IMAGES_DIR, f))]
    folders.sort(key=lambda x: int(x.split("_")[1]))

    print(f"[*] Sincronizando slides master de branding em {len(folders)} pastas...")

    total_synced = 0

    for folder in folders:
        folder_path = os.path.join(IMAGES_DIR, folder)
        
        # Lista todos os arquivos existentes
        files = os.listdir(folder_path)
        
        # Identifica quais são fotos reais do produto (excluindo os masters que já foram copiados)
        product_slides = []
        for f in files:
            f_lower = f.lower()
            if f_lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
                fp = os.path.join(folder_path, f)
                f_size = os.path.getsize(fp)
                # Se não for idêntico ao master de qualidade ou garantia, é foto real do produto
                if f_size != qualidade_size and f_size != garantia_size:
                    product_slides.append(f)
                else:
                    # Remove versão anterior do master para renumerar com perfeição
                    os.remove(fp)

        # Ordena as fotos do produto
        product_slides.sort()

        # Adiciona qualidade.png e GARANTIA.png no final da sequência
        next_idx = len(product_slides) + 1
        slide_qualidade_path = os.path.join(folder_path, f"slide {next_idx}.png")
        shutil.copy2(MASTER_QUALIDADE, slide_qualidade_path)

        next_idx += 1
        slide_garantia_path = os.path.join(folder_path, f"slide {next_idx}.png")
        shutil.copy2(MASTER_GARANTIA, slide_garantia_path)

        total_synced += 1

    print(f"[✓] {total_synced} pastas sincronizadas com sucesso!")
    print(f"    - 'qualidade.png' e 'GARANTIA.png' inseridos no final de todos os carrosséis.")


if __name__ == "__main__":
    sync_branding_to_all_folders()
