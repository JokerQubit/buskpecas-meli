#!/usr/bin/env python3
"""
scripts/generate_batch2_dossiers.py
-----------------------------------
Gera os 58 Dossiês Técnicos Granulares do Lote 2 (Peças 52 a 109) em 'docs/pecas/'.
Formato: Markdown com YAML frontmatter estruturado, tabela de compatibilidade veicular,
códigos OEM, part numbers cruzados e especificações técnicas de montadora.
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
OUTPUT_DOSSIERS_DIR = os.path.join("docs", "pecas")


def sanitize_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


def generate_dossiers():
    os.makedirs(OUTPUT_DOSSIERS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Seleciona apenas os itens do Lote 2 (52 a 109)
    c.execute("SELECT * FROM tb_pecas WHERE id >= 52 ORDER BY id ASC;")
    pecas = c.fetchall()

    print(f"[*] Gerando {len(pecas)} dossiês técnicos do Lote 2...")

    for peca in pecas:
        peca_id = peca["id"]
        sku = peca["sku_master"]
        nome = peca["nome_comercial_base"]
        marca = peca["marca_fabricante"]
        codigo = peca["codigo_fabricante"]
        cat1 = peca["categoria_nivel_1"]
        cat2 = peca["categoria_nivel_2"]
        posicao = peca["posicao_instalacao"]
        qtd = peca["quantidade_estoque"]
        preco = peca["preco_venda"]
        comissao = peca["comissao_10_pct"]
        faturamento_estoque = peca["faturamento_total_estoque"]
        comissao_estoque = peca["comissao_total_estoque"]
        garantia = peca["garantia_meses"]
        
        oem_list = json.loads(peca["codigos_oem"])
        cross_list = json.loads(peca["codigos_cruzados"])
        tech_dict = json.loads(peca["especificacoes_tecnicas"])
        alertas = json.loads(peca["alertas_compatibilidade"])
        diferenciais = json.loads(peca["diferenciais_competitivos"])
        origem = json.loads(peca["origem_dados"])

        # Busca compatibilidade veicular
        c.execute("SELECT * FROM tb_compatibilidade_veicular WHERE peca_id = ? ORDER BY montadora, veiculo_modelo, ano_inicio;", (peca_id,))
        veiculos = c.fetchall()

        slug_marca = sanitize_filename(marca.upper().replace(" ", "_").replace("/", "_"))
        slug_cod = sanitize_filename(codigo.upper())
        filename = f"PECA_{peca_id:02d}_{slug_marca}_{slug_cod}.md"
        filepath = os.path.join(OUTPUT_DOSSIERS_DIR, filename)

        # Monta YAML frontmatter
        md = "---\n"
        md += f"id: {peca_id}\n"
        md += f"sku_master: \"{sku}\"\n"
        md += f"nome_comercial_base: \"{nome}\"\n"
        md += f"marca_fabricante: \"{marca}\"\n"
        md += f"codigo_fabricante: \"{codigo}\"\n"
        md += f"categoria_nivel_1: \"{cat1}\"\n"
        md += f"categoria_nivel_2: \"{cat2}\"\n"
        md += f"posicao_instalacao: \"{posicao}\"\n"
        md += f"quantidade_estoque: {qtd}\n"
        md += f"preco_venda: {preco:.2f}\n"
        md += f"comissao_10_pct: {comissao:.2f}\n"
        md += f"faturamento_total_estoque: {faturamento_estoque:.2f}\n"
        md += f"comissao_total_estoque: {comissao_estoque:.2f}\n"
        md += f"garantia_meses: {garantia}\n"
        md += "codigos_oem:\n"
        for o in oem_list:
            md += f"  - \"{o}\"\n"
        md += "codigos_cruzados:\n"
        for cr in cross_list:
            md += f"  - \"{cr}\"\n"
        md += "---\n\n"

        # Corpo Markdown
        md += f"# Dossiê Técnico: {nome}\n\n"
        md += f"**SKU Master:** `{sku}`  \n"
        md += f"**Fabricante Oficial:** {marca} | **Part Number:** `{codigo}`  \n"
        md += f"**Categoria:** {cat1} > {cat2}  \n"
        md += f"**Posição de Instalação:** {posicao}  \n"
        md += f"**Garantia:** {garantia} Meses  \n\n"

        md += "## 💰 Métricas Comerciais e Estoque\n\n"
        md += f"- **Preço Unitário de Venda:** R$ {preco:,.2f}\n"
        md += f"- **Comissão Unitária (10%):** R$ {comissao:,.2f}\n"
        md += f"- **Quantidade Física em Estoque:** {qtd} unidades\n"
        md += f"- **Faturamento Bruto Total do Estoque:** R$ {faturamento_estoque:,.2f}\n"
        md += f"- **Comissão Líquida Total (10%):** R$ {comissao_estoque:,.2f}\n\n"

        md += "## ⚙️ Especificações Técnicas de Fábrica\n\n"
        for k, v in tech_dict.items():
            k_format = k.replace("_", " ").title()
            md += f"- **{k_format}:** {v}\n"
        md += "\n"

        md += "## 🚗 Tabela de Compatibilidade Veicular Detalhada\n\n"
        if veiculos:
            md += "| Montadora | Modelo | Versão | Motorização | Combustível | Anos Compatíveis | Notas Técnicas |\n"
            md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for v in veiculos:
                ano_str = f"{v['ano_inicio']} a {v['ano_fim'] if v['ano_fim'] else 'Atual'}"
                md += f"| {v['montadora']} | {v['veiculo_modelo']} | {v['versao'] or 'Todas'} | {v['motorizacao'] or 'Padrão'} | {v['combustivel'] or 'Flex'} | {ano_str} | {v['notas_especiais'] or 'Encaixe direto'} |\n"
        else:
            md += "*Compatibilidade universal / sob consulta de chassis.*\n"
        md += "\n"

        md += "## ⚠️ Alertas Críticos de Compatibilidade\n\n"
        for a in alertas:
            md += f"- ⚠️ {a}\n"
        md += "\n"

        md += "## 🛡️ Diferenciais Competitivos de Fábrica\n\n"
        for d in diferenciais:
            md += f"- 💎 {d}\n"
        md += "\n"

        md += "## 🔍 Referências Cruzadas & OEM\n\n"
        md += f"- **Códigos OEM Originais de Montadora:** {', '.join([f'`{o}`' for o in oem_list])}\n"
        md += f"- **Códigos Cruzados Equivalentes:** {', '.join([f'`{cr}`' for cr in cross_list])}\n"
        md += f"- **Origem no Arquivo de Estoque:** `{origem.get('arquivo_fonte')}` (Linha {origem.get('linha_arquivo')})\n"

        with open(filepath, "w", encoding="utf-8") as out_f:
            out_f.write(md)

    conn.close()
    print(f"[✓] {len(pecas)} dossiês técnicos do Lote 2 gerados em: {OUTPUT_DOSSIERS_DIR}")


if __name__ == "__main__":
    generate_dossiers()
