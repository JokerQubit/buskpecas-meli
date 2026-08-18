#!/usr/bin/env python3
"""
scripts/setup_images_structure.py
---------------------------------
Cria a estrutura de pastas organizada para as 51 peças em 'images/':
- Uma pasta individual para cada peça nomeada no padrão:
  images/PECA_[ID:02d]_[MARCA]_[CODIGO]/
- Dentro de cada pasta, cria um arquivo 'INFO_IMAGENS.md' com:
  - SKU, Marca, Part Number, Códigos OEM;
  - Tabela de compatibilidade veicular resumida;
  - Guia de slots recomendados para os slides do usuário (Foto 01 até Foto 07);
  - Links de busca direta no Google Imagens / Catálogos Oficiais (Kostal, Bosch, etc.) para download rápido das fotos de fábrica.
"""

import os
import re
import sys
import json
import urllib.parse
import unicodedata

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ENRICHED_JSON_PATH = os.path.join("data", "enriched_catalog_51.json")
IMAGES_DIR = os.path.join("images")


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().upper()
    text = re.sub(r'[-\s]+', '_', text)
    return text[:35]


def setup_folders():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    with open(ENRICHED_JSON_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    items = catalog.get("itens", [])
    folders_created = []

    for item in items:
        item_id = item["id"]
        brand_code = slugify(f"{item['marca_fabricante']}_{item['codigo_fabricante']}")
        folder_name = f"PECA_{item_id:02d}_{brand_code}"
        folder_path = os.path.join(IMAGES_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Links de busca direta para facilitar o download das imagens oficiais
        query_brand = urllib.parse.quote(f"{item['marca_fabricante']} {item['codigo_fabricante']} catalogo")
        query_oem = urllib.parse.quote(f"{item['codigos_oem'][0]} {item['marca_fabricante']}") if item.get("codigos_oem") else query_brand

        info_content = f"""# 📁 GUIA DE IMAGENS: {item['nome_comercial_base']}

> **SKU Master:** `{item['sku_master']}`  
> **Fabricante:** **{item['marca_fabricante']}**  
> **Código do Fabricante (Part Number):** `{item['codigo_fabricante']}`  
> **Códigos Originais da Montadora (OEM):** `{', '.join(item['codigos_oem'])}`  
> **Preço de Tabela:** R$ {item['preco_venda']:.2f} (Comissão 10%: R$ {item['comissao_10_pct']:.2f})

---

### 🔍 Links Rápidos para Encontrar as Fotos Oficiais de Fábrica:
- 🌐 [Buscar Fotos Oficiais do Fabricante no Google](https://www.google.com/search?tbm=isch&q={query_brand})
- 🌐 [Buscar Fotos pelo Código OEM da Montadora](https://www.google.com/search?tbm=isch&q={query_oem})

---

### 📸 Nomenclatura Recomendada para os Arquivos desta Pasta:
Ao baixar as fotos oficiais da marca ou criar seus designs, salve os arquivos nesta pasta seguindo este padrão:

- `01_capa_fundo_branco.jpg` (Foto principal isolada em fundo branco)
- `02_detalhes_acabamento.jpg` (Close na gravação do código/marca)
- `03_conector_pinagem.jpg` (Foto traseira mostrando os pinos/plugue)
- `04_aplicacao_veiculos.jpg` (Slide com os carros compatíveis)
- `05_alerta_compatibilidade.jpg` (Slide com dicas para não comprar errado)
- `06_ficha_tecnica.jpg` (Slide com medidas, voltagem e códigos OEM)
- `07_garantia_envio.jpg` (Slide com selos de envio 24h e NF-e)

---

### 🚗 Veículos Compatíveis Principais:
{chr(10).join([f"- **{c['montadora']} {c['veiculo_modelo']}** ({c['ano_inicio']} a {c.get('ano_fim') or 'Atual'}) - {c.get('motorizacao') or 'Padrão'}" for c in item['compatibilidade_veicular']])}
"""

        info_file = os.path.join(folder_path, "INFO_IMAGENS.md")
        with open(info_file, "w", encoding="utf-8") as inf:
            inf.write(info_content)

        folders_created.append((item_id, folder_name, folder_path))

    # Cria README principal na pasta images/
    index_md = f"""# 📦 REPOSITÓRIO CENTRAL DE IMAGENS DAS 51 PEÇAS
## Organização de Imagens Oficiais & Slides para Mercado Livre

Cada uma das 51 pastas abaixo contém um guia técnico (`INFO_IMAGENS.md`) com os códigos de fábrica, códigos OEM e links diretos para coletar as imagens oficiais dos fabricantes (Kostal, Bosch, Magneti Marelli, Fiat, etc.).

---

### 📂 Lista das 51 Pastas de Imagens:

| # | Pasta da Peça | Fabricante | Part Number | Código OEM | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
"""
    for item in items:
        brand_code = slugify(f"{item['marca_fabricante']}_{item['codigo_fabricante']}")
        fname = f"PECA_{item['id']:02d}_{brand_code}"
        oem_main = item['codigos_oem'][0] if item.get('codigos_oem') else '-'
        index_md += f"| {item['id']:02d} | [`images/{fname}/`](file:///c:/Users/pichau/Documents/antigravity/delightful-hopper/images/{fname}/) | **{item['marca_fabricante']}** | `{item['codigo_fabricante']}` | `{oem_main}` | `Aguardando Fotos` |\n"

    with open(os.path.join(IMAGES_DIR, "README.md"), "w", encoding="utf-8") as rf:
        rf.write(index_md)

    print(f"[✓] Sucesso! Criadas {len(folders_created)} pastas de peças em '{IMAGES_DIR}/' com guias de imagem.")


if __name__ == "__main__":
    setup_folders()
