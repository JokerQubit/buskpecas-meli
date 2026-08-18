#!/usr/bin/env python3
"""
scripts/generate_dossiers.py
----------------------------
Gera os 51 Dossiês Técnicos Granulares em 'docs/pecas/PECA_[ID]_[SLUG].md'.
Cada arquivo contém:
- YAML Frontmatter parseável por máquina para consumo imediato de subagentes na Fase 2;
- Ficha técnica completa de engenharia;
- Tabela de compatibilidade veicular exaustiva;
- Diretrizes de instalação e diagnóstico elétrico/mecânico;
- Metadados SEO para Mercado Livre e alertas contra devoluções;
- Telemetria comercial (preço, comissão 10%, estoque = 1).
"""

import os
import re
import sys
import json
import unicodedata

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ENRICHED_JSON_PATH = os.path.join("data", "enriched_catalog_51.json")
DOCS_PECAS_DIR = os.path.join("docs", "pecas")


def slugify(text: str) -> str:
    """Gera um slug limpo para nomes de arquivo a partir de texto."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().upper()
    text = re.sub(r'[-\s]+', '_', text)
    return text[:35]


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_dossier_markdown(item: dict) -> str:
    tech = item["especificacoes_tecnicas"]
    oem_list = item["codigos_oem"]
    cross_list = item["codigos_cruzados"]
    compat_list = item["compatibilidade_veicular"]
    seo_list = item["termos_seo"]
    diff_list = item["diferenciais_competitivos"]
    alerts_list = item["alertas_compatibilidade"]

    # Constrói resumo YAML
    yaml_lines = [
        "---",
        f"id: {item['id']}",
        f"sku_master: \"{item['sku_master']}\"",
        f"nome_comercial_base: \"{item['nome_comercial_base']}\"",
        f"marca_fabricante: \"{item['marca_fabricante']}\"",
        f"codigo_fabricante: \"{item['codigo_fabricante']}\"",
        f"categoria_nivel_1: \"{item['categoria_nivel_1']}\"",
        f"categoria_nivel_2: \"{item['categoria_nivel_2']}\"",
        f"posicao_instalacao: \"{item['posicao_instalacao']}\"",
        f"preco_venda_brl: {item['preco_venda']:.2f}",
        f"comissao_10_pct_brl: {item['comissao_10_pct']:.2f}",
        f"quantidade_estoque: {item['quantidade_estoque']}",
        f"garantia_meses: {item['garantia_meses']}",
        "codigos_oem:",
    ]
    for oem in oem_list:
        yaml_lines.append(f"  - \"{oem}\"")

    yaml_lines.append("codigos_cruzados:")
    for cross in cross_list:
        yaml_lines.append(f"  - \"{cross}\"")

    yaml_lines.append("termos_busca_seo:")
    for term in seo_list:
        yaml_lines.append(f"  - \"{term}\"")

    yaml_lines.append("---")
    yaml_header = "\n".join(yaml_lines)

    # Tabela de especificações
    spec_rows = []
    for k, v in tech.items():
        key_label = k.replace("_", " ").title()
        if isinstance(v, list):
            val_str = "<br>• " + "<br>• ".join(v)
        else:
            val_str = str(v)
        spec_rows.append(f"| **{key_label}** | {val_str} |")
    spec_table = "\n".join(spec_rows)

    # Tabela de compatibilidade
    compat_rows = []
    for c in compat_list:
        ano_fim_str = str(c["ano_fim"]) if c.get("ano_fim") else "Atual"
        versao_str = c.get("versao") or "Todas as versões"
        motor_str = c.get("motorizacao") or "Padrão"
        comb_str = c.get("combustivel") or "Flex"
        notas_str = c.get("notas_especiais") or "Aplicação direta sem adaptação"
        compat_rows.append(
            f"| **{c['montadora']}** | **{c['veiculo_modelo']}** | {versao_str} | {motor_str} | {comb_str} | {c['ano_inicio']} a {ano_fim_str} | {notas_str} |"
        )
    compat_table = "\n".join(compat_rows)

    # Diferenciais e Alertas
    diff_bullets = "\n".join([f"- {d}" for d in diff_list])
    alert_bullets = "\n".join([f"- ⚠️ **ATENÇÃO:** {a}" for a in alerts_list])
    seo_bullets = "\n".join([f"1. `{t}`" for t in seo_list])

    # Sugestões de Título SEO Mercado Livre (Máx 60 caracteres)
    titulo_ml_1 = f"{item['nome_comercial_base'][:60]}"
    
    # Montagem do Markdown completo
    md_content = f"""{yaml_header}

# 📋 Dossiê Técnico Enterprise: {item['nome_comercial_base']}

> **SKU Master:** `{item['sku_master']}` | **Código Fabricante:** `{item['codigo_fabricante']}` | **Status Estoque:** `1 unidade física disponível`

---

## 🏛️ 1. Ficha Técnica & Engenharia do Componente

A peça **{item['nome_comercial_base']}** (código `{item['codigo_fabricante']}`), fabricada pela renomada marca **{item['marca_fabricante']}**, foi desenvolvida para atender rigorosamente aos padrões de qualidade das principais montadoras globais. Sua fabricação emprega ligas metálicas nobres e polímeros estruturais de alta densidade resistentes a variações térmicas severas, fadiga mecânica e estresse elétrico.

| Parâmetro Técnico | Especificação Homologada |
| :--- | :--- |
| **SKU Corporativo** | `{item['sku_master']}` |
| **Marca / Fabricante** | **{item['marca_fabricante']}** |
| **Part Number Oficial** | `{item['codigo_fabricante']}` |
| **Categoria Primária** | {item['categoria_nivel_1']} |
| **Subcategoria** | {item['categoria_nivel_2']} |
| **Posição de Instalação** | {item['posicao_instalacao']} |
| **Garantia Legal / Fabril** | {item['garantia_meses']} meses ({item['garantia_meses']} meses com cobertura nacional) |
| **Códigos OEM (Montadora)** | `{', '.join(oem_list)}` |
| **Referências Cruzadas** | {', '.join(cross_list)} |
{spec_table}

---

## 🚗 2. Matriz Completa de Aplicação Veicular

Abaixo está o mapeamento exaustivo de compatibilidade com modelos, anos, motorizações e versões homologadas para este componente:

| Montadora | Modelo | Versão | Motorização | Combustível | Anos de Aplicação | Notas Técnicas de Aplicação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{compat_table}

---

## 🔧 3. Diretrizes de Instalação, Diagnóstico e Manuseio

### 📋 Recomendações Pré-Instalação:
1. **Desconexão da Bateria:** Antes de iniciar a desmontagem ou manipulação de componentes elétricos e eletrônicos, desconecte obrigatoriamente o polo negativo da bateria do veículo para evitar picos de corrente (surges) ou curto-circuitos na central eletrônica (ECU / BCM).
2. **Inspeção Visual e Limpeza:** Limpe a área de assentamento e verifique a integridade do chicote elétrico e dos conectores fêmea. Remova qualquer vestígio de oxidação ou zinabre com limpa-contato automotivo de secagem rápida.
3. **Alinhamento e Encaixe:** Encaixe a peça suavemente nas guias e travas originais sem forçar as alavancas ou os pinos do conector. Nunca aplique solventes abrasivos na carcaça.
4. **Verificação Funcional Pós-Montagem:** Realize o teste operacional completo (piscas esquerdo/direito, retorno mecânico no volante, farol alto/baixo, limpadores em todas as velocidades, esguicho, temporizador e botões auxiliares) antes de fechar a capa de acabamento da coluna.

---

## 🚀 4. Estratégia de Copywriting & SEO para Mercado Livre (Fase 2)

### 🎯 Sugestões de Título SEO (Otimizados para Busca no ML):
- **Opção Principal:** `{titulo_ml_1}`
- **Opção Alternativa (Long-Tail):** `{item['marca_fabricante']} {item['codigo_fabricante']} Original {compat_list[0]['veiculo_modelo']} {compat_list[0]['ano_inicio']}-{compat_list[0].get('ano_fim') or 'Atual'}`

### 🔍 Termos de Busca Reais dos Compradores (Search Volume):
{seo_bullets}

### 💎 Diferenciais Competitivos da Peça:
{diff_bullets}

### ⚠️ Alertas Críticos de Compatibilidade (Prevenção de Devoluções):
{alert_bullets}

---

## 💰 5. Telemetria Financeira & Parâmetros Comerciais

| Indicador Comercial | Valor Parametrizado |
| :--- | :--- |
| **Preço de Tabela / Venda Final** | **{format_currency(item['preco_venda'])}** |
| **Estoque Físico Registrado** | **{item['quantidade_estoque']} unidade** |
| **Taxa de Comissão Fixada** | **10.00%** |
| **Valor Líquido da Comissão** | **{format_currency(item['comissao_10_pct'])}** |
| **Origem do Dado Físico** | Página {item['source_metadata']['page']} / Linha {item['source_metadata']['line_index']} do PDF Oficial |

---
*Dossiê gerado automaticamente pelo Sistema Corporativo Autônomo de Inteligência e Engenharia de Dados de Auto Peças.*
"""
    return md_content


def generate_all_dossiers():
    print(f"[*] Iniciando geração dos 51 Dossiês Técnicos em: {DOCS_PECAS_DIR}")
    os.makedirs(DOCS_PECAS_DIR, exist_ok=True)

    if not os.path.exists(ENRICHED_JSON_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {ENRICHED_JSON_PATH}")

    with open(ENRICHED_JSON_PATH, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    items = catalog_data.get("itens", [])
    if len(items) != 51:
        raise ValueError(f"Esperava-se 51 itens, mas foram encontrados {len(items)}.")

    dossiers_created = []

    for item in items:
        item_id = item["id"]
        brand_code = slugify(f"{item['marca_fabricante']}_{item['codigo_fabricante']}")
        filename = f"PECA_{item_id:02d}_{brand_code}.md"
        filepath = os.path.join(DOCS_PECAS_DIR, filename)

        md_content = generate_dossier_markdown(item)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        dossiers_created.append(filepath)

    print(f"[✓] Sucesso! Foram gerados exatamente {len(dossiers_created)} dossiês técnicos em '{DOCS_PECAS_DIR}'.")
    return dossiers_created


if __name__ == "__main__":
    generate_all_dossiers()
