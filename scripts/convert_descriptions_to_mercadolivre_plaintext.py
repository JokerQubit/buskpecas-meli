#!/usr/bin/env python3
"""
scripts/convert_descriptions_to_mercadolivre_plaintext.py
---------------------------------------------------------
Converte as descrições de Markdown para TEXTO PURO MODERNO & MINIMALISTA,
eliminando linhas de '====', usando espaçamento limpo, marcadores elegantes
e estrutura moderna focada em legibilidade mobile.
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


def clean_json_or_text(val):
    if not val:
        return ""
    if isinstance(val, list):
        return ", ".join(str(x) for x in val)
    if isinstance(val, str):
        val_str = val.strip()
        if (val_str.startswith("[") and val_str.endswith("]")) or (val_str.startswith("{") and val_str.endswith("}")):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return ", ".join(str(x) for x in parsed)
                elif isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return val_str
    return str(val)


def clean_alerts_list(val):
    if not val:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str):
        val_str = val.strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        lines = [line.strip().lstrip("-").lstrip("*").strip() for line in val_str.splitlines() if line.strip()]
        return lines
    return [str(val)]


def build_meli_modern_description(peca, compats):
    nome_base = peca["nome_comercial_base"]
    marca = peca["marca_fabricante"]
    cod_fab = peca["codigo_fabricante"]
    garantia = peca["garantia_meses"]
    oem_clean = clean_json_or_text(peca["codigos_oem"]) or "Consulte catálogo"
    oem_cruz_clean = clean_json_or_text(peca["codigos_cruzados"]) or ""
    alertas_list = clean_alerts_list(peca["alertas_compatibilidade"])
    
    specs = peca["especificacoes_tecnicas"] or "{}"
    if isinstance(specs, str):
        try:
            specs_dict = json.loads(specs)
        except Exception:
            specs_dict = {}
    else:
        specs_dict = specs

    # Monta lista de aplicação veicular limpa
    app_lines = []
    if compats:
        for c in compats:
            mont = c["montadora"]
            mod = c["veiculo_modelo"]
            vers = c["versao"] or "Todas as Versões"
            mot = c["motorizacao"] or "Padrão"
            comb = c["combustivel"] or "Flex / Gasolina"
            anos = f"{c['ano_inicio']} a {c['ano_fim']}" if c['ano_fim'] else f"{c['ano_inicio']} em diante"
            app_lines.append(f"• {mont} {mod} ({vers}) — Motor {mot} {comb} ({anos})")
    else:
        app_lines.append("• Universal / Multimarcas — Linha Automotiva (Conforme especificações)")

    app_text = "\n".join(app_lines)

    # Monta alertas limpos
    alerts_lines = []
    if alertas_list:
        for a in alertas_list:
            alerts_lines.append(f"• {a}")
    alerts_lines.append("• Recomendamos comparar o código gravado na sua peça com os códigos informados abaixo.")
    alerts_lines.append("• Em caso de dúvidas sobre ano/versão, pergunte no campo abaixo antes de comprar!")
    alerts_text = "\n".join(alerts_lines)

    # Monta especificações
    specs_lines = []
    specs_lines.append(f"• Fabricante: {marca}")
    specs_lines.append(f"• Código da Peça: {cod_fab}")
    specs_lines.append(f"• Código Original (OEM): {oem_clean}")
    if oem_cruz_clean and oem_cruz_clean != "N/A":
        specs_lines.append(f"• Códigos Similares: {oem_cruz_clean}")
    
    if isinstance(specs_dict, dict) and specs_dict:
        for k, v in specs_dict.items():
            k_clean = k.replace("_", " ").title()
            v_clean = clean_json_or_text(v)
            specs_lines.append(f"• {k_clean}: {v_clean}")

    specs_lines.append("• Condição: Produto 100% novo, lacrado na embalagem original")
    specs_text = "\n".join(specs_lines)

    # Template Moderno Minimalista (Sem linhas ascii pesadas)
    desc = f"""🚗 APLICAÇÃO VEICULAR
Confira os modelos e anos compatíveis:

{app_text}


⚠️ ALERTAS DE COMPATIBILIDADE
{alerts_text}


⚙️ ESPECIFICAÇÕES TÉCNICAS
{specs_text}


📦 CONTEÚDO & GARANTIA
• 01 {nome_base} ({marca} {cod_fab})
• Acompanha Nota Fiscal Eletrônica (PF e PJ)
• Garantia de {garantia} meses contra defeitos de fabricação


❓ DÚVIDAS FREQUENTES
• Pronta Entrega: Sim, todos os produtos anunciados estão em estoque físico para envio imediato.
• Frete e Prazo: Calculados automaticamente pelo Mercado Envios digitando seu CEP no anúncio.
• Instalação: Recomendamos que a montagem seja feita por profissional especializado.


🛡️ BUSK Peças — Qualidade, Agilidade & Confiança"""

    return desc


def format_full_markdown_file(peca, compats, existing_title=None):
    p_id = peca["id"]
    sku = peca["sku_master"]
    marca = peca["marca_fabricante"]
    cod_fab = peca["codigo_fabricante"]
    nome_base = peca["nome_comercial_base"]
    preco = peca["preco_venda"]
    comissao = peca["comissao_10_pct"]
    estoque = peca["quantidade_estoque"]
    garantia = peca["garantia_meses"]
    oem_clean = clean_json_or_text(peca["codigos_oem"]) or "N/A"

    t_ppal = existing_title or f"{nome_base[:50]} {cod_fab}"
    if len(t_ppal) > 60:
        t_ppal = t_ppal[:60].strip()

    t_alt1 = f"{nome_base} {marca} {cod_fab} OEM {oem_clean.split(',')[0].strip()}"
    t_alt2 = f"{nome_base} {cod_fab} {marca}"

    desc_plain = build_meli_modern_description(peca, compats)

    md = f"""---
id: {p_id}
sku_master: "{sku}"
titulo_ml_principal: "{t_ppal}"
titulo_ml_alternativo_oem: "{t_alt1}"
titulo_ml_long_tail: "{t_alt2}"
categoria_nivel_1: "{peca['categoria_nivel_1'] or 'Auto Peças'}"
categoria_nivel_2: "{peca['categoria_nivel_2'] or 'Componentes Automotivos'}"
preco_venda_brl: {preco:.2f}
comissao_10_pct_brl: {comissao:.2f}
quantidade_estoque: {estoque}
garantia_meses: {garantia}
status_anuncio: "PRONTO_PARA_PUBLICACAO"
---

# 📦 ANÚNCIO: {nome_base} — {marca} ({cod_fab})

> **SKU Master:** `{sku}` | **Código Fabricante:** `{cod_fab}` | **Estoque Físico:** `{estoque} Unidade(s)` | **Disponível para Envio Imediato**

---

### 🏷️ Sugestões de Título para o Mercado Livre

1. **Opção 1 (SEO Principal - Máximo 60 Caracteres):**
   `{t_ppal}`  
   *📏 Comprimento: {len(t_ppal)} caracteres (otimizado para busca mobile no app do Mercado Livre)*

2. **Opção 2 (Busca por Código Original OEM):**
   `{t_alt1}`

3. **Opção 3 (Busca Long-Tail):**
   `{t_alt2}`

---

## 📝 Descrição do Produto (Formato Moderno Mercado Livre)

```text
{desc_plain}
```
"""
    return md, desc_plain, t_ppal


def get_existing_title(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    for line in content.splitlines():
        if line.startswith("titulo_ml_principal:"):
            t = line.replace("titulo_ml_principal:", "").strip().strip('"').strip("'")
            return t
    return None


def convert_all():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()

    print("=" * 80)
    print(f"🚀 ATUALIZANDO 109 DESCRIÇÕES PARA FORMATO MODERNO & MINIMALISTA")
    print("=" * 80)

    bulk_rows = []
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
        c.execute("SELECT * FROM tb_compatibilidade_veicular WHERE peca_id = ? ORDER BY montadora ASC, veiculo_modelo ASC, ano_inicio ASC;", (p_id,))
        compats = c.fetchall()

        files = [f for f in os.listdir(ANUNCIOS_DIR) if f.startswith(f"ANUNCIO_{p_id:02d}_")]
        existing_title = None
        if files:
            fp = os.path.join(ANUNCIOS_DIR, files[0])
            existing_title = get_existing_title(fp)

        md_content, plain_desc, final_title = format_full_markdown_file(p, compats, existing_title)

        if files:
            fp = os.path.join(ANUNCIOS_DIR, files[0])
            with open(fp, "w", encoding="utf-8") as af:
                af.write(md_content)

        oem_clean = clean_json_or_text(p["codigos_oem"]) or ""

        bulk_rows.append({
            "SKU": p["sku_master"],
            "TITULO": final_title,
            "PRECO": f"{p['preco_venda']:.2f}",
            "ESTOQUE": p["quantidade_estoque"],
            "CONDICAO": "Novo",
            "MARCA": p["marca_fabricante"],
            "CODIGO_FABRICANTE_MPN": p["codigo_fabricante"],
            "CODIGO_OEM": oem_clean,
            "GARANTIA_MESES": p["garantia_meses"],
            "TIPO_GARANTIA": "Garantia do vendedor",
            "DESCRICAO": plain_desc
        })

    conn.close()

    # Salva Planilha Oficial ML
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=headers, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in bulk_rows:
            writer.writerow(r)

    print(f"[✓] 109 Anúncios em 'docs/anuncios/' atualizados com formato Moderno.")
    print(f"[✓] Planilha de Carga em Massa '{OUTPUT_CSV}' 100% atualizada.")
    print("\n" + "=" * 80)
    print("🏁 FORMATO MODERNO APLICADO COM SUCESSO EM TODA A BASE!")
    print("=" * 80)


if __name__ == "__main__":
    convert_all()
