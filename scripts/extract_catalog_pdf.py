#!/usr/bin/env python3
"""
scripts/extract_catalog_pdf.py
------------------------------
Módulo de Ingestão Dinâmica e Parsing do PDF de Catálogo (Zero-Mock).
Lê o arquivo 'lista_51_itens_corrigida.pdf', extrai linha por linha os 51 itens,
seus códigos brutos, preços e metadados de rastreabilidade (página/linha).
Gera o dataset estruturado em 'data/raw/ingested_catalog_51.json'.
"""

import os
import re
import sys
import json
import pypdf

# Garante saída UTF-8 no terminal Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PDF_PATH = "lista_51_itens_corrigida.pdf"
OUTPUT_JSON = os.path.join("data", "raw", "ingested_catalog_51.json")


def clean_price(price_str: str) -> float:
    """Converte string de preço no formato 'R$ 459,90' para float 459.90."""
    cleaned = price_str.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".").strip()
    return float(cleaned)


def extract_catalog():
    print(f"[*] Iniciando extração física do PDF: {PDF_PATH}")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"Arquivo PDF não encontrado no caminho: {PDF_PATH}")

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    reader = pypdf.PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    print(f"[*] Total de páginas detectadas: {total_pages}")

    items = []
    
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detecta o início de um item numérico (1 a 51)
            if re.match(r"^\d+$", line):
                item_num = int(line)
                if 1 <= item_num <= 51:
                    # O próximo elemento deve ser o código e em seguida o preço
                    if i + 2 < len(lines):
                        code_str = lines[i + 1].strip()
                        price_str = lines[i + 2].strip()
                        
                        # Verifica se o preço tem padrão R$ ou valor
                        if "R$" in price_str or re.search(r"\d+,\d{2}", price_str):
                            numeric_price = clean_price(price_str)
                            item_data = {
                                "id": item_num,
                                "raw_code": code_str,
                                "raw_price": price_str,
                                "preco_venda": numeric_price,
                                "comissao_10_pct": round(numeric_price * 0.10, 2),
                                "quantidade_estoque": 1,
                                "source_metadata": {
                                    "source_file": PDF_PATH,
                                    "page": page_idx + 1,
                                    "line_index": i
                                }
                            }
                            items.append(item_data)
                            i += 3
                            continue
            i += 1

    # Ordena por ID
    items = sorted(items, key=lambda x: x["id"])
    print(f"[+] Total de itens extraídos com sucesso: {len(items)}")

    if len(items) != 51:
        raise ValueError(f"Divergência crítica: esperava-se 51 itens, mas foram extraídos {len(items)}.")

    catalog_payload = {
        "status": "SUCCESS",
        "total_items": len(items),
        "fase": "FASE_1_INGESTAO_BRUTA",
        "timestamp_extracao": "2026-08-17T15:05:00Z",
        "arquivo_origem": PDF_PATH,
        "itens": items
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog_payload, f, indent=2, ensure_ascii=False)

    print(f"[✓] Dataset bruto salvo com sucesso em: {OUTPUT_JSON}")
    return items


if __name__ == "__main__":
    extract_catalog()
