#!/usr/bin/env python3
"""
scripts/generate_native_excel_sheets.py
---------------------------------------
Gera planilhas nativas em formato .XLSX e .XLS (Excel 97-2003)
com os cabeçalhos padrão oficiais do Mercado Livre Brasil para Carga em Massa:

Colunas:
- SKU
- Título
- Preço
- Quantidade
- Condição (Novo)
- Descrição
- Código universal de produto (EAN / OEM)
- Marca
- Modelo
- Garantia
- Tipo de garantia
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
OUTPUT_XLSX = os.path.join("data", "planilha_carga_massa_mercadolivre_109.xlsx")
OUTPUT_XLS = os.path.join("data", "planilha_carga_massa_mercadolivre_109.xls")


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


def generate_excel():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()

    print("=" * 80)
    print(f"🚀 GERANDO PLANILHAS NATIVAS .XLS E .XLSX MERCADO LIVRE ({len(pecas)} PEÇAS)")
    print("=" * 80)

    rows = []

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

        # Pega o arquivo markdown correspondente
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

        rows.append({
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

    df = pd.DataFrame(rows)

    # 1. Salva XLSX (Excel Moderno)
    df.to_excel(OUTPUT_XLSX, index=False, engine="openpyxl")
    print(f"[✓] Planilha XLSX gerada: {OUTPUT_XLSX}")

    # 2. Salva XLS (Excel 97-2003) via xlwt
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Anúncios Mercado Livre')

    headers = list(rows[0].keys())
    for col_idx, h in enumerate(headers):
        ws.write(0, col_idx, h)

    for row_idx, r in enumerate(rows, start=1):
        for col_idx, h in enumerate(headers):
            val = r[h]
            ws.write(row_idx, col_idx, val)

    wb.save(OUTPUT_XLS)
    print(f"[✓] Planilha XLS (Excel 97-2003) gerada: {OUTPUT_XLS}")

    print("\n" + "=" * 80)
    print("🏁 ARQUIVOS EXCEL .XLS E .XLSX GERADOS COM 100% DE SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    generate_excel()
