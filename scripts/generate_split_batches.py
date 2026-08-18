#!/usr/bin/env python3
"""
scripts/generate_split_batches.py
---------------------------------
Divide o catálogo de 109 peças em 2 Lotes menores e 100% compatíveis com o limite
do validador do Mercado Livre (que costuma limitar a 50-100 produtos por carga):

1. Lote 1 (Itens 01 a 55): 55 produtos (Elétrica Leve, Bobinas, Chaves Kostal, Sensores e Milhas)
2. Lote 2 (Itens 56 a 109): 54 produtos (Faróis Principais Arteb/Fitam/Orgus, Juntas e Retentores Sabó)

Gera em formato .XLSX e .XLS para ambos os lotes!
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import openpyxl
import xlwt

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
ANUNCIOS_DIR = os.path.join("docs", "anuncios")
DATA_DIR = "data"


def extract_description_from_md(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "## 📝 Descrição do Produto" in content:
        desc = content.split("## 📝 Descrição do Produto", 1)[1]
        lines = desc.splitlines()
        clean_lines = []
        in_code_block = False
        for l in lines:
            if l.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if "Formato" in l or l.strip() == "---":
                continue
            clean_lines.append(l)
        return "\n".join(clean_lines).strip()
    return content


def generate_batches():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()

    print("=" * 80)
    print(f"🚀 GERANDO LOTES DIVIDIDOS PARA CARGA NO MERCADO LIVRE ({len(pecas)} PEÇAS)")
    print("=" * 80)

    all_rows = []

    for p in pecas:
        p_id = p["id"]
        sku = p["sku_master"]
        marca = p["marca_fabricante"]
        cod_fab = p["codigo_fabricante"]
        nome_base = p["nome_comercial_base"]
        preco = p["preco_venda"]
        estoque = p["quantidade_estoque"]
        garantia = p["garantia_meses"]
        oem = p["codigos_oem"] or ""
        if oem.startswith("[") and oem.endswith("]"):
            try:
                oem = ", ".join(json.loads(oem))
            except Exception:
                pass

        files = [f for f in os.listdir(ANUNCIOS_DIR) if f.startswith(f"ANUNCIO_{p_id:02d}_")]
        desc_text = ""
        titulo_final = f"{nome_base[:50]} {cod_fab}"
        if files:
            fp = os.path.join(ANUNCIOS_DIR, files[0])
            desc_text = extract_description_from_md(fp)
            with open(fp, "r", encoding="utf-8") as f:
                for line in f.read().splitlines():
                    if line.startswith("titulo_ml_principal:"):
                        titulo_final = line.replace("titulo_ml_principal:", "").strip().strip('"').strip("'")
                        break

        if len(titulo_final) > 60:
            titulo_final = titulo_final[:60].strip()

        all_rows.append({
            "SKU": sku,
            "Título": titulo_final,
            "Preço": round(preco, 2),
            "Quantidade": int(estoque),
            "Condição": "Novo",
            "Marca": marca,
            "Modelo": cod_fab,
            "Código universal de produto": oem.split(",")[0].strip() if oem else "",
            "Garantia": f"{garantia} meses",
            "Tipo de garantia": "Garantia do vendedor",
            "Descrição": desc_text
        })

    conn.close()

    # Divide em Lote 1 (0 a 55) e Lote 2 (55 a 109)
    lote1_rows = all_rows[:55]
    lote2_rows = all_rows[55:]

    batches = [
        ("LOTE_1_itens_01_a_55", lote1_rows),
        ("LOTE_2_itens_56_a_109", lote2_rows)
    ]

    for name, rows in batches:
        xlsx_path = os.path.join(DATA_DIR, f"{name}.xlsx")
        xls_path = os.path.join(DATA_DIR, f"{name}.xls")
        csv_path = os.path.join(DATA_DIR, f"{name}.csv")

        # Salva XLSX
        df = pd.DataFrame(rows)
        df.to_excel(xlsx_path, index=False, engine="openpyxl")
        print(f"[✓] {name} XLSX gerado ({len(rows)} itens): {xlsx_path}")

        # Salva XLS (97-2003)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Anúncios')
        headers = list(rows[0].keys())
        for col_idx, h in enumerate(headers):
            ws.write(0, col_idx, h)
        for row_idx, r in enumerate(rows, start=1):
            for col_idx, h in enumerate(headers):
                ws.write(row_idx, col_idx, r[h])
        wb.save(xls_path)
        print(f"[✓] {name} XLS gerado ({len(rows)} itens): {xls_path}")

        # Salva CSV UTF-8-sig
        df.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")

    print("\n" + "=" * 80)
    print(f"🏁 LOTES DIVIDIDOS (55 e 54 ITENS) GERADOS COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    generate_batches()
