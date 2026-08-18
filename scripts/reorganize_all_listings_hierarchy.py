#!/usr/bin/env python3
"""
scripts/reorganize_all_listings_hierarchy.py
--------------------------------------------
Reorganiza a hierarquia das descrições em todos os 109 anúncios do Mercado Livre
em 'docs/anuncios/', colocando O MAIS IMPORTANTE NO TOPO:

1. 🚗 APLICAÇÃO VEICULAR COMPLETA (Tabela de Carros, Versões, Motores e Anos)
2. ⚠️ ALERTAS CRÍTICOS DE COMPATIBILIDADE (Lado LD/LE, Pinagem, Restrições)
3. ⚙️ FICHA TÉCNICA, CÓDIGOS OEM E ESPECIFICAÇÕES DO FABRICANTE
4. 📦 CONTEÚDO DA EMBALAGEM, NOTA FISCAL E GARANTIA
5. ❓ DÚVIDAS FREQUENTES E SUPORTE BUSK PEÇAS
"""

import os
import sys
import json
import sqlite3

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
ANUNCIOS_DIR = os.path.join("docs", "anuncios")


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


def clean_alerts(val):
    if not val:
        return ""
    if isinstance(val, list):
        return "\n".join(f"- **Atenção:** {x}" for x in val)
    if isinstance(val, str):
        val_str = val.strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return "\n".join(f"- **Atenção:** {x}" for x in parsed)
            except Exception:
                pass
        lines = [line.strip() for line in val_str.splitlines() if line.strip()]
        out = []
        for l in lines:
            if not l.startswith("-"):
                out.append(f"- **Atenção:** {l}")
            else:
                out.append(l)
        return "\n".join(out)
    return str(val)


def format_listing(peca, compat_list, existing_title=None):
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
    oem_cruz_clean = clean_json_or_text(peca["codigos_cruzados"]) or "N/A"
    alertas_clean = clean_alerts(peca["alertas_compatibilidade"])
    
    specs = peca["especificacoes_tecnicas"] or "{}"
    if isinstance(specs, str):
        try:
            specs_dict = json.loads(specs)
        except Exception:
            specs_dict = {}
    else:
        specs_dict = specs

    # Mantém o título validado pelo Red Team se existir, senão gera um <= 60 chars
    t_ppal = existing_title or f"{nome_base[:50]} {cod_fab}"
    if len(t_ppal) > 60:
        t_ppal = t_ppal[:60].strip()

    t_alt1 = f"{nome_base} {marca} {cod_fab} OEM {oem_clean.split(',')[0].strip()}"
    t_alt2 = f"{nome_base} {cod_fab} {marca}"

    # Monta a tabela de compatibilidade veicular
    if compat_list:
        table_rows = []
        for c in compat_list:
            mont = c["montadora"]
            mod = c["veiculo_modelo"]
            vers = c["versao"] or "Todas as Versões"
            mot = c["motorizacao"] or "Padrão"
            comb = c["combustivel"] or "Flex / Gasolina"
            anos = f"{c['ano_inicio']} a {c['ano_fim']}" if c['ano_fim'] else f"{c['ano_inicio']}+"
            table_rows.append(f"| **{mont}** | **{mod}** | {vers} | {mot} | {comb} | {anos} |")
        compat_table_md = "\n".join(table_rows)
    else:
        compat_table_md = "| **Universal / Multimarcas** | Linha Automotiva | Universal | Conforme especificações | Flex / Diesel / Gas. | Todos os anos |"

    # Monta lista de especificações técnicas
    specs_lines = []
    if isinstance(specs_dict, dict) and specs_dict:
        for k, v in specs_dict.items():
            k_clean = k.replace("_", " ").title()
            specs_lines.append(f"- **{k_clean}:** {v}")
    if not specs_lines:
        specs_lines.append(f"- **Tipo de Peça:** {nome_base}")
        specs_lines.append(f"- **Padrão:** 100% Original e Normatizado")

    specs_formatted = "\n".join(specs_lines)

    # Monta o arquivo markdown completo
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

## 📝 Descrição do Produto (Pronta para Copiar e Colar no Mercado Livre)

---

### 🚗 1. APLICAÇÃO VEICULAR (CONFIRA SE SERVE NO SEU CARRO)

Confira abaixo a lista detalhada de veículos compatíveis antes de realizar a compra:

| Montadora | Modelo | Versão / Detalhes | Motorização | Combustível | Anos de Aplicação |
| :--- | :--- | :--- | :--- | :--- | :--- |
{compat_table_md}

---

### ⚠️ 2. ATENÇÃO E ALERTAS DE COMPATIBILIDADE (LEIA ANTES DE COMPRAR)

{alertas_clean if alertas_clean else '- **Verificação Importante:** Compare sempre o código gravado na sua peça antiga e o modelo exato do conector/fixação com as fotos reais do nosso anúncio para garantir 100% de compatibilidade.'}
- **Evite Devoluções:** Em caso de qualquer dúvida sobre versão, lado de montagem ou motorização, envie sua pergunta no campo abaixo informando o modelo, ano e motor do seu veículo. Nossa equipe técnica responde rápido!

---

### ⚙️ 3. FICHA TÉCNICA & CÓDIGOS ORIGINAIS (OEM)

- **Marca / Fabricante:** {marca}
- **Código do Fabricante (Part Number):** `{cod_fab}`
- **Código Original da Montadora (OEM):** `{oem_clean}`
- **Códigos Cruzados / Similares:** `{oem_cruz_clean}`
{specs_formatted}
- **Condição do Item:** Produto 100% Novo, lacrado na embalagem original de fábrica.
- **Procedência:** Peça de reposição genuína/normatizada com padrão de linha de montagem.

---

### 📦 4. CONTEÚDO DA EMBALAGEM, NOTA FISCAL & GARANTIA

- **Conteúdo da Embalagem:** 01 {nome_base} ({marca} `{cod_fab}`)
- **Nota Fiscal:** Acompanha Nota Fiscal Eletrônica (NFe) em nome do comprador (emitida tanto para Pessoa Física quanto Jurídica).
- **Garantia:** {garantia} Meses de garantia legal e de fábrica contra qualquer defeito de fabricação.

---

### ❓ 5. DÚVIDAS FREQUENTES (FAQ)

- **O produto está disponível em estoque?**  
  Sim! Todos os nossos produtos anunciados possuem estoque físico real e estão prontos para postagem imediata.
- **Qual é o prazo e valor do frete?**  
  O frete e o prazo de entrega são calculados automaticamente pelo Mercado Envios. Basta inserir o seu CEP no campo correspondente logo abaixo do preço do anúncio.
- **Como garantir que a peça é a correta para o meu carro?**  
  Basta verificar a tabela de aplicação no topo da descrição e conferir o código gravado na sua peça usada.
- **Recomendação de Instalação:**  
  Recomendamos que a instalação seja feita sempre por um profissional mecânico/eletricista qualificado. Não nos responsabilizamos por montagens inadequadas ou adaptações indevidas.

---

🛡️ **BUSK Peças — Qualidade Comprovada, Agilidade & Confiança no Seu Carro!**
"""
    return md


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


def reorganize_all():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    pecas = c.fetchall()

    print("=" * 80)
    print(f"🚀 REORGANIZANDO HIERARQUIA DAS DESCRIÇÕES DE TODOS OS {len(pecas)} ANÚNCIOS")
    print("=" * 80)

    count = 0
    for p in pecas:
        p_id = p["id"]
        c.execute("SELECT * FROM tb_compatibilidade_veicular WHERE peca_id = ? ORDER BY montadora ASC, veiculo_modelo ASC, ano_inicio ASC;", (p_id,))
        compats = c.fetchall()

        files = [f for f in os.listdir(ANUNCIOS_DIR) if f.startswith(f"ANUNCIO_{p_id:02d}_")]
        if files:
            file_name = files[0]
            file_path = os.path.join(ANUNCIOS_DIR, file_name)
            existing_title = get_existing_title(file_path)
            md_content = format_listing(p, compats, existing_title)
            with open(file_path, "w", encoding="utf-8") as af:
                af.write(md_content)
            count += 1
            print(f"[✓] Anúncio {p_id:02d} reorganizado: {file_name}")

    conn.close()

    print("\n" + "=" * 80)
    print(f"🏁 CONCLUÍDO COM SUCESSO: {count} / {len(pecas)} ANÚNCIOS REORGANIZADOS!")
    print("=" * 80)


if __name__ == "__main__":
    reorganize_all()
