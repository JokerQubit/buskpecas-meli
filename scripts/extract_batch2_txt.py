#!/usr/bin/env python3
"""
scripts/extract_batch2_txt.py
-----------------------------
Processa o arquivo 'Novo Documento de Texto.txt' contendo o Lote 2 de peças
(Faróis, Juntas Sabó, Retentores Sabó) fornecido pelo atendente Kaique Neres.

Extrai:
- Categoria (Faróis, Juntas Sabó, Retentores Sabó);
- Código / Part Number bruto;
- Descrição preliminar e lado (LD/LE);
- Quantidade física em estoque (ex: 180 unidades, 91 unidades, etc.);
- Preço unitário em R$ e cálculo da comissão de 10%;
- Salva o dataset bruto em 'data/raw/ingested_catalog_batch2.json'.
"""

import os
import re
import sys
import json

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TXT_PATH = "Novo Documento de Texto.txt"
OUTPUT_RAW_PATH = os.path.join("data", "raw", "ingested_catalog_batch2.json")


def clean_price(price_str: str) -> float:
    cleaned = re.sub(r"[^\d,\.]", "", price_str).replace(".", "").replace(",", ".")
    return float(cleaned)


def extract_batch2():
    print(f"[*] Lendo arquivo: {TXT_PATH}")
    if not os.path.exists(TXT_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {TXT_PATH}")

    with open(TXT_PATH, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    current_category = "Geral"
    raw_items = []
    item_index = 52  # Começa após as 51 peças do Lote 1

    for line_idx, line in enumerate(lines, start=1):
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("*") or line_clean.startswith("Produtos"):
            continue

        # Detecta mudança de categoria
        if line_clean.upper() in ["FARÓIS", "FAROIS"]:
            current_category = "Faróis e Iluminação"
            continue
        elif "JUNTAS" in line_clean.upper():
            current_category = "Juntas de Motor Sabó"
            continue
        elif "RETENTORES" in line_clean.upper():
            current_category = "Retentores Sabó"
            continue

        # Regex para extrair item:
        # Exemplos:
        # "160818 Farol Astra LD - 1 unidade - R$ 680"
        # "80270 - 91 unidades - R$ 430"
        # "79410FLEX - 49 unidades - R$ 170"
        # "07340 - 63 unidades - R$ 210"
        # "160711 Farol Gol G5 LE 2 unidade - R$480"
        
        # Padrão com ' - ' ou espaço para separadores
        match = re.search(r"^([A-Za-z0-9]+)\s*(.*?)\s*[-–—]?\s*(\d+)\s*unidades?\s*[-–—]?\s*R\$\s*([\d\.,]+)", line_clean, re.IGNORECASE)
        if match:
            code = match.group(1).strip()
            desc_raw = match.group(2).strip(" -")
            qty = int(match.group(3))
            price = clean_price(match.group(4))
        else:
            # Fallback para linhas sem traço antes de unidade
            match2 = re.search(r"^([A-Za-z0-9]+)\s*(.*?)\s+(\d+)\s*unidades?\s*[-–—]?\s*R\$\s*([\d\.,]+)", line_clean, re.IGNORECASE)
            if match2:
                code = match2.group(1).strip()
                desc_raw = match2.group(2).strip(" -")
                qty = int(match2.group(3))
                price = clean_price(match2.group(4))
            else:
                print(f"[!] Linha não reconhecida (linha {line_idx}): {line_clean}")
                continue

        # Determina fabricante provável
        if "SABÓ" in current_category.upper() or "SABO" in current_category.upper():
            fabricante = "Sabó"
        elif code.startswith("160") or code.startswith("0160"):
            fabricante = "Arteb"
        elif code.startswith("FORT") or code.startswith("FL") or code.startswith("FF"):
            fabricante = "Fortluz"
        elif code.startswith("FW"):
            fabricante = "Fitam"
        elif code.startswith("MG"):
            fabricante = "Orgus / Megavox"
        elif code.startswith("MSL"):
            fabricante = "Microluz"
        elif code.startswith("1T0"):
            fabricante = "Volkswagen / Magneti Marelli"
        elif code.startswith("AL"):
            fabricante = "Autopoli / Universal LED"
        elif code.startswith("IA") or code.startswith("578"):
            fabricante = "Orgus / Arteb"
        else:
            fabricante = "Aftermarket Automotivo"

        comissao = round(price * 0.10, 2)
        total_estoque_valor = round(price * qty, 2)
        total_comissao_estoque = round(comissao * qty, 2)

        raw_item = {
            "id": item_index,
            "sku_master": f"SKU-{item_index:03d}-{fabricante[:3].upper()}-{code}",
            "codigo_bruto": code,
            "descricao_bruta": desc_raw,
            "categoria_bruta": current_category,
            "fabricante_detectado": fabricante,
            "quantidade_estoque": qty,
            "preco_unitario_brl": price,
            "comissao_unitario_10_pct_brl": comissao,
            "total_faturamento_estoque_brl": total_estoque_valor,
            "total_comissao_estoque_brl": total_comissao_estoque,
            "origem_linha": line_idx,
            "linha_original_texto": line_clean
        }

        raw_items.append(raw_item)
        item_index += 1

    os.makedirs(os.path.dirname(OUTPUT_RAW_PATH), exist_ok=True)
    with open(OUTPUT_RAW_PATH, "w", encoding="utf-8") as out:
        json.dump({
            "metadata": {
                "total_itens_lote_2": len(raw_items),
                "total_unidades_fisicas_lote_2": sum(i["quantidade_estoque"] for i in raw_items),
                "faturamento_bruto_potencial_lote_2_brl": sum(i["total_faturamento_estoque_brl"] for i in raw_items),
                "comissao_total_10_pct_lote_2_brl": sum(i["total_comissao_estoque_brl"] for i in raw_items)
            },
            "itens": raw_items
        }, out, indent=2, ensure_ascii=False)

    print(f"[✓] Extração do Lote 2 concluída com sucesso!")
    print(f"    - Total de SKUs Lote 2: {len(raw_items)} peças")
    print(f"    - Total de Unidades Físicas: {sum(i['quantidade_estoque'] for i in raw_items)} unidades em estoque")
    print(f"    - Faturamento Potencial Lote 2: R$ {sum(i['total_faturamento_estoque_brl'] for i in raw_items):,.2f}")
    print(f"    - Comissão Líquida 10%: R$ {sum(i['total_comissao_estoque_brl'] for i in raw_items):,.2f}")
    print(f"    - Arquivo gerado em: {OUTPUT_RAW_PATH}")
    return raw_items


if __name__ == "__main__":
    extract_batch2()
