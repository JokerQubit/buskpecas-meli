#!/usr/bin/env python3
"""
scripts/setup_batch2_images.py
------------------------------
Cria as 58 pastas de imagens para as peças do Lote 2 (Peças 52 a 109) em 'images/'.
Gera para cada uma o arquivo 'INFO_IMAGENS.md' contendo:
- Metadados completos da peça (SKU, Part Number, OEM, Fabricante, Preço, Quantidade);
- Links diretos para busca de fotos em catálogos e Google Imagens;
- Convenção de nomenclatura de fotos e slides para upload no Mercado Livre;
- Atualiza o repositório mestre em 'images/README.md'.
"""

import os
import sys
import json
import sqlite3
import urllib.parse

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join("database", "autoparts_master.db")
IMAGES_DIR = "images"


def sanitize_folder_name(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


def setup_batch2_images():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas WHERE id >= 52 ORDER BY id ASC;")
    pecas = c.fetchall()

    print(f"[*] Criando pastas de imagens para {len(pecas)} peças do Lote 2...")

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
        garantia = peca["garantia_meses"]
        oem_list = json.loads(peca["codigos_oem"])
        cross_list = json.loads(peca["codigos_cruzados"])

        slug_marca = sanitize_folder_name(marca.upper().replace(" ", "_").replace("/", "_"))
        slug_cod = sanitize_folder_name(codigo.upper())
        folder_name = f"PECA_{peca_id:02d}_{slug_marca}_{slug_cod}"
        folder_path = os.path.join(IMAGES_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        query_google = urllib.parse.quote(f"{marca} {codigo} {nome}")
        link_google = f"https://www.google.com/search?tbm=isch&q={query_google}"
        query_ml = urllib.parse.quote(f"{marca} {codigo}")
        link_ml = f"https://lista.mercadolivre.com.br/{query_ml}"

        info_md = f"# 📷 Repositório de Imagens: {nome}\n\n"
        info_md += f"**ID Interno:** `{peca_id}` | **SKU Master:** `{sku}`  \n"
        info_md += f"**Fabricante:** {marca} | **Código (Part Number):** `{codigo}`  \n"
        info_md += f"**Categoria:** {cat1} > {cat2}  \n"
        info_md += f"**Posição / Lado:** {posicao}  \n"
        info_md += f"**Estoque Físico:** {qtd} unidades | **Preço de Venda:** R$ {preco:,.2f}  \n\n"

        info_md += "## 🔍 Links Diretos para Busca de Fotos Oficiais de Catálogo\n\n"
        info_md += f"- 🌐 [Buscar Fotos Oficiais no Google Imagens]({link_google})\n"
        info_md += f"- 🛍️ [Ver Concorrentes e Fotos no Mercado Livre]({link_ml})\n\n"

        info_md += "## 📋 Convenção de Nomenclatura de Arquivos para Esta Pasta\n\n"
        info_md += "Salve os arquivos das fotos desta peça com os nomes padronizados abaixo:\n\n"
        info_md += "| Arquivo Sugerido | Finalidade no Mercado Livre | Formato |\n"
        info_md += "| :--- | :--- | :--- |\n"
        info_md += "| `01_capa_fundo_branco.jpg` | **Foto 1 (Obrigatória):** Peça frontal/3D em fundo branco puro `#FFFFFF` | JPG / PNG |\n"
        info_md += "| `02_conector_pinagem.jpg` | **Foto 2:** Close do conector elétrico, plugue, flange ou espessura | JPG / PNG |\n"
        info_md += "| `03_codigo_gravado_etiqueta.jpg` | **Foto 3:** Close do código e logotipo original gravado | JPG / PNG |\n"
        info_md += "| `04_outro_angulo_embalagem.jpg` | **Foto 4:** Vista lateral ou na caixa original lacrada | JPG / PNG |\n"
        info_md += "| `05_slide_busk_pecas.jpg` | **Foto 5:** Slide Institucional da BUSK Peças (*Qualidade / Garantia*) | JPG / PNG |\n\n"

        info_md += "## 🔍 Códigos de Referência para Validação Visual\n\n"
        info_md += f"- **Códigos OEM de Montadora:** {', '.join([f'`{o}`' for o in oem_list])}\n"
        info_md += f"- **Códigos Cruzados Equivalentes:** {', '.join([f'`{cr}`' for cr in cross_list])}\n"

        with open(os.path.join(folder_path, "INFO_IMAGENS.md"), "w", encoding="utf-8") as inf:
            inf.write(info_md)

    # Atualiza images/README.md consolidado com todas as 109 peças
    c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
    all_pecas = c.fetchall()

    readme_md = "# 🖼️ Repositório Central de Imagens e Ativos Visuais — BUSK Peças\n\n"
    readme_md += "Este diretório organiza as pastas de imagens para todos os **109 SKUs cadastrados** no catálogo da BUSK Peças.\n\n"
    readme_md += "## 📁 Estrutura de Diretórios (109 Pastas Individuais)\n\n"
    readme_md += "| ID | SKU | Fabricante | Part Number | Categoria | Estoque | Preço | Pasta Local | Guia de Fotos |\n"
    readme_md += "| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |\n"

    for p in all_pecas:
        p_id = p["id"]
        p_sku = p["sku_master"]
        p_marca = p["marca_fabricante"]
        p_cod = p["codigo_fabricante"]
        p_cat2 = p["categoria_nivel_2"]
        p_qtd = p["quantidade_estoque"]
        p_preco = p["preco_venda"]
        slug_m = sanitize_folder_name(p_marca.upper().replace(" ", "_").replace("/", "_"))
        slug_c = sanitize_folder_name(p_cod.upper())
        p_folder = f"PECA_{p_id:02d}_{slug_m}_{slug_c}"
        readme_md += f"| {p_id:02d} | `{p_sku}` | {p_marca} | `{p_cod}` | {p_cat2} | {p_qtd} un | R$ {p_preco:,.2f} | [`{p_folder}/`](file:///{IMAGES_DIR.replace('\\', '/')}/{p_folder}/) | [INFO](file:///{IMAGES_DIR.replace('\\', '/')}/{p_folder}/INFO_IMAGENS.md) |\n"

    readme_md += "\n---\n\n"
    readme_md += "## 🎯 Padrão de Carrossel de Imagens no Mercado Livre\n\n"
    readme_md += "1. **Foto 1 (Principal):** Peça em fundo branco puro `#FFFFFF` (sem textos nem bordas).\n"
    readme_md += "2. **Foto 2 (Detalhe Construtivo):** Conector, plugue, flange ou pinagem.\n"
    readme_md += "3. **Foto 3 (Gravação OEM):** Código de fábrica gravado no corpo da peça.\n"
    readme_md += "4. **Foto 4 (Embalagem Oficial):** Peça na caixa lacrada da marca.\n"
    readme_md += "5. **Foto 5 (Slide BUSK Peças):** Slide de Confiança, Envio Rápido e Garantia.\n"

    with open(os.path.join(IMAGES_DIR, "README.md"), "w", encoding="utf-8") as rmf:
        rmf.write(readme_md)

    conn.close()
    print(f"[✓] {len(pecas)} pastas de imagens criadas em '{IMAGES_DIR}/' e 'images/README.md' atualizado com 109 peças!")


if __name__ == "__main__":
    setup_batch2_images()
