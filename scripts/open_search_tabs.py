#!/usr/bin/env python3
"""
scripts/open_search_tabs.py
---------------------------
Abre automaticamente no seu navegador padrão as abas de busca do Google Imagens
e Mercado Livre para um lote específico de peças (ex: Peças 7 a 16).

Uso:
  python scripts/open_search_tabs.py --start 7 --end 16
  python scripts/open_search_tabs.py --next 10
  python scripts/open_search_tabs.py --top-revenue
"""

import os
import sys
import json
import sqlite3
import argparse
import webbrowser
import urllib.parse

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
IMAGES_DIR = "images"


def get_pending_pieces():
    """
    Retorna a lista de peças que ainda não possuem fotos reais salvas na pasta.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()
    conn.close()

    pending = []
    for p in pecas:
        p_id = p["id"]
        # Encontra a pasta
        folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith(f"PECA_{p_id:02d}_")]
        if folders:
            folder_path = os.path.join(IMAGES_DIR, folders[0])
            files = [f for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            if len(files) == 0:
                pending.append((p, folders[0]))
        else:
            pending.append((p, None))
    return pending


def open_tabs(start_id: int = None, end_id: int = None, count: int = 10, source: str = "google"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if start_id and end_id:
        c.execute("SELECT id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante FROM tb_pecas WHERE id BETWEEN ? AND ? ORDER BY id ASC;", (start_id, end_id))
        items = c.fetchall()
    else:
        pending = get_pending_pieces()
        items = [p[0] for p in pending[:count]]

    conn.close()

    if not items:
        print("[!] Nenhuma peça pendente encontrada.")
        return

    print(f"[*] Abrindo {len(items)} abas no seu navegador padrão...")

    for item in items:
        p_id = item["id"]
        marca = item["marca_fabricante"]
        cod = item["codigo_fabricante"]
        nome = item["nome_comercial_base"]

        # Constrói a busca ideal
        # Ex: "Kostal 10013879" ou "Sabó 80270"
        query_text = f"{marca} {cod} {nome}"
        query_encoded = urllib.parse.quote(query_text)
        
        if source == "ml":
            url = f"https://lista.mercadolivre.com.br/{urllib.parse.quote(f'{marca} {cod}')}"
        else:
            # Google Imagens
            url = f"https://www.google.com/search?tbm=isch&q={query_encoded}"

        print(f"  [Item {p_id:02d}] Abrindo: {marca} {cod} ({url[:60]}...)")
        webbrowser.open_new_tab(url)

    print(f"\n[✓] {len(items)} abas abertas no seu navegador com sucesso!")
    print(f"    - Salve as fotos reais na pasta 'images/PECA_[ID].../' como 'slide 1.png' e 'slide 2.png'.")
    print(f"    - Em seguida, rode 'python scripts/clean_and_sync_slides.py' para sincronizar os slides de garantia e qualidade!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abre abas de busca para as peças.")
    parser.add_argument("--start", type=int, default=None, help="ID inicial")
    parser.add_argument("--end", type=int, default=None, help="ID final")
    parser.add_argument("--count", type=int, default=10, help="Quantidade de abas para abrir")
    parser.add_argument("--source", type=str, default="google", choices=["google", "ml"], help="Origem da busca")
    args = parser.parse_args()

    open_tabs(start_id=args.start, end_id=args.end, count=args.count, source=args.source)
