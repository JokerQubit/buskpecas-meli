#!/usr/bin/env python3
"""
scripts/generate_meli_bulk_sheet.py
-----------------------------------
Gera a Planilha Oficial de Carga em Massa para o Mercado Livre (em formato CSV)
com todas as 109 peças do catálogo BUSK Peças.
"""

import os
import sys
import json
import sqlite3
import csv

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
ANUNCIOS_DIR = os.path.join("docs", "anuncios")
OUTPUT_CSV = os.path.join("data", "planilha_carga_massa_mercadolivre_109.csv")


def extract_description_from_md(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Pega apenas o corpo da descrição
    if "## 📝 Descrição do Produto" in content:
        desc = content.split("## 📝 Descrição do Produto", 1)[1]
        lines = desc.splitlines()
        clean_lines = []
        for l in lines:
            if "Pronta para Copiar" in l or l.strip() == "---":
                continue
            clean_lines.append(l)
        return "\n".join(clean_lines).strip()
    return content


def generate_bulk_sheets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()

    print("=" * 80)
    print(f"🚀 GERANDO PLANILHA OFICIAL DE CARGA EM MASSA MERCADO LIVRE ({len(pecas)} PEÇAS)")
    print("=" * 80)

    rows = []
    headers = [
        "SKU",
        "TITULO",
        "PRECO",
        "ESTOQUE",
        "CONDICAO",
        "MARCA",
        "CODIGO_FABRICANTE_MPN",
        "CODIGO_OEM",
        "GARANTIA_MESES",
        "TIPO_GARANTIA",
        "DESCRICAO"
    ]

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
            "TITULO": titulo_final,
            "PRECO": f"{preco:.2f}",
            "ESTOQUE": estoque,
            "CONDICAO": "Novo",
            "MARCA": marca,
            "CODIGO_FABRICANTE_MPN": cod_fab,
            "CODIGO_OEM": oem,
            "GARANTIA_MESES": garantia,
            "TIPO_GARANTIA": "Garantia do vendedor",
            "DESCRICAO": desc_text
        })

    conn.close()

    # Salva em CSV UTF-8 com BOM para abrir perfeitamente no Excel brasileiro
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=headers, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"[✓] Planilha CSV gerada com sucesso: {OUTPUT_CSV}")
    print(f"[✓] Total de produtos exportados: {len(rows)} itens")
    print("\n" + "=" * 80)
    print(f"🏁 ARQUIVO DE IMPORTAÇÃO EM LOTE 100% PRONTO!")
    print("=" * 80)


if __name__ == "__main__":
    generate_bulk_sheets()
