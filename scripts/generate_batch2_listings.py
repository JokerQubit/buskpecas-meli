#!/usr/bin/env python3
"""
scripts/generate_batch2_listings.py
-----------------------------------
Gera os 58 Anúncios Comerciais Completos do Mercado Livre para o Lote 2 (Itens 52 a 109)
seguindo rigorosamente o template em 'docs/TEMPLATE_ANUNCIO_MERCADO_LIVRE.md'.

Garante:
- Título principal com limite estrito <= 60 caracteres;
- Tabela de compatibilidade veicular completa;
- Alertas práticos de lado e encaixe para evitar devoluções;
- Tom de especialista de balcão de autopeças;
- Salva em 'docs/anuncios/ANUNCIO_[ID]_[MARCA]_[CODIGO].md'.
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
OUTPUT_LISTINGS_DIR = os.path.join("docs", "anuncios")


def sanitize_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


def craft_seo_titles(marca: str, codigo: str, cat2: str, veiculos: list, posicao: str, tech: dict) -> tuple:
    """
    Gera 3 opções de títulos SEO para Mercado Livre garantindo que a Opção 1 tenha <= 60 caracteres.
    """
    # Identifica o carro principal
    if veiculos:
        carro_principal = f"{veiculos[0]['montadora']} {veiculos[0]['veiculo_modelo']}".replace("Volkswagen", "VW").replace("Chevrolet", "GM")
    else:
        carro_principal = "Universal"

    # Lado / Posição enxuta
    pos_curta = ""
    if "Direito" in posicao or "LD" in codigo:
        pos_curta = "Direito"
    elif "Esquerdo" in posicao or "LE" in codigo:
        pos_curta = "Esquerdo"

    # Constrói Opção 1 (Primária <= 60 chars)
    if "Farol" in cat2:
        if "Milha" in cat2 or "Neblina" in cat2:
            t1 = f"Farol Milha {carro_principal} {pos_curta} {marca} {codigo}".strip()
        else:
            t1 = f"Farol {carro_principal} {pos_curta} {marca} {codigo}".strip()
    elif "Junta" in cat2:
        if "Cabeçote" in cat2:
            t1 = f"Junta Cabeçote Aço {carro_principal} Sabó {codigo}".strip()
        elif "Tampa" in cat2:
            t1 = f"Junta Tampa Válvulas {carro_principal} Sabó {codigo}".strip()
        else:
            t1 = f"Jogo Juntas Motor {carro_principal} Sabó {codigo}".strip()
    elif "Retentor" in cat2:
        if "Flange" in cat2 or "07340" in codigo or "05590" in codigo:
            t1 = f"Retentor Flange Virabrequim {carro_principal} Sabó {codigo}".strip()
        elif "Comando" in cat2 or "01884" in codigo:
            t1 = f"Retentor Comando Válvulas {carro_principal} Sabó {codigo}".strip()
        else:
            t1 = f"Retentor Motor {carro_principal} Sabó {codigo}".strip()
    else:
        t1 = f"Peça {carro_principal} {marca} {codigo}".strip()

    # Encurta se passar de 60 chars
    if len(t1) > 60:
        t1 = t1.replace("Sabó ", "").replace("Volkswagen ", "VW ").replace("Chevrolet ", "GM ")
    if len(t1) > 60:
        t1 = t1[:60].strip()

    # Opções 2 e 3 para teste A/B
    t2 = f"{t1} Original Novo"[:60].strip()
    t3 = f"{t1} Pronta Entrega"[:60].strip()

    return t1, t2, t3


def generate_listings():
    os.makedirs(OUTPUT_LISTINGS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM tb_pecas WHERE id >= 52 ORDER BY id ASC;")
    pecas = c.fetchall()

    print(f"[*] Gerando {len(pecas)} anúncios comerciais para o Lote 2...")

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
        tech_dict = json.loads(peca["especificacoes_tecnicas"])
        alertas = json.loads(peca["alertas_compatibilidade"])
        diferenciais = json.loads(peca["diferenciais_competitivos"])

        c.execute("SELECT * FROM tb_compatibilidade_veicular WHERE peca_id = ? ORDER BY montadora, veiculo_modelo, ano_inicio;", (peca_id,))
        veiculos = c.fetchall()

        t1, t2, t3 = craft_seo_titles(marca, codigo, cat2, veiculos, posicao, tech_dict)

        slug_marca = sanitize_filename(marca.upper().replace(" ", "_").replace("/", "_"))
        slug_cod = sanitize_filename(codigo.upper())
        filename = f"ANUNCIO_{peca_id:02d}_{slug_marca}_{slug_cod}.md"
        filepath = os.path.join(OUTPUT_LISTINGS_DIR, filename)

        # Categoria ML
        if "Farol" in cat2:
            ml_cat = "MLB1807 - Faróis Automotivos"
        elif "Junta" in cat2:
            ml_cat = "MLB1815 - Juntas de Motor"
        else:
            ml_cat = "MLB1820 - Retentores e Vedação"

        # Monta anúncio
        md = "---\n"
        md += f"id: {peca_id}\n"
        md += f"sku: \"{sku}\"\n"
        md += f"codigo_fabricante: \"{codigo}\"\n"
        md += f"fabricante: \"{marca}\"\n"
        md += f"categoria_ml: \"{ml_cat}\"\n"
        md += f"preco_venda: {preco:.2f}\n"
        md += f"quantidade_estoque: {qtd}\n"
        md += f"garantia_meses: {garantia}\n"
        md += f"titulo_ml_principal: \"{t1}\"\n"
        md += f"comprimento_titulo_principal: {len(t1)}\n"
        md += "titulos_alternativos:\n"
        md += f"  - \"{t2}\"\n"
        md += f"  - \"{t3}\"\n"
        md += "---\n\n"

        md += f"# {t1}\n\n"
        md += f"**Part Number Oficial:** `{codigo}` | **Fabricante:** {marca}  \n"
        md += f"**Condição:** Produto 100% Novo, na Embalagem Lacrada  \n"
        md += f"**Disponibilidade:** Estoque a Pronta Entrega ({qtd} unidades disponíveis)  \n"
        md += f"**Garantia:** {garantia} Meses contra defeitos de fabricação  \n\n"

        md += "---\n\n"
        md += "## 📝 Descrição Geral do Produto\n\n"
        md += f"O **{nome}** é a escolha definitiva para quem busca máxima durabilidade, segurança e encaixe milimétrico original no veículo.\n\n"
        md += f"Fabricado pela **{marca}**, fornecedora reconhecida e homologada pelas maiores montadoras do país, este componente elimina qualquer risco de adaptações forçadas, folgas ou retrabalho na oficina.\n\n"

        md += "### 💎 Principais Diferenciais:\n\n"
        for d in diferenciais:
            md += f"- 🔩 **{d}**\n"
        md += "- 📦 **Embalagem reforçada:** Peça despachada com proteção extra para chegar 100% intacta.\n"
        md += "- 🧾 **Nota Fiscal Eletrônica (NF-e):** Emitida no ato da compra para CPF ou CNPJ.\n\n"

        md += "---\n\n"
        md += "## 🚗 Aplicação Veicular Detalhada\n\n"
        md += "Confira abaixo os veículos 100% compatíveis com esta peça:\n\n"
        if veiculos:
            md += "| Montadora | Modelo | Versão / Motor | Anos Compatíveis | Observações de Instalação |\n"
            md += "| :--- | :--- | :--- | :--- | :--- |\n"
            for v in veiculos:
                ano_str = f"{v['ano_inicio']} a {v['ano_fim'] if v['ano_fim'] else 'Atual'}"
                versao_motor = f"{v['versao'] or 'Todas'} ({v['motorizacao'] or 'Padrão'})"
                md += f"| **{v['montadora']}** | {v['veiculo_modelo']} | {versao_motor} | {ano_str} | {v['notas_especiais'] or 'Plug & Play'} |\n"
        else:
            md += "*Compatibilidade universal / sob consulta de chassi.*\n"
        md += "\n"

        md += "⚠️ **Dica de Especialista:** Se o seu carro estiver na lista acima e com o motor especificado, a compatibilidade é garantida. Se ainda tiver qualquer dúvida, envie uma pergunta informando o modelo, ano e motor do seu veículo que nossa equipe técnica valida para você na hora!\n\n"

        md += "---\n\n"
        md += "## ⚙️ Ficha Técnica do Fabricante\n\n"
        md += f"- **Marca:** {marca}\n"
        md += f"- **Código do Fabricante (Part Number):** `{codigo}`\n"
        md += f"- **Posição / Lado de Instalação:** {posicao}\n"
        for k, v in tech_dict.items():
            k_format = k.replace("_", " ").title()
            md += f"- **{k_format}:** {v}\n"
        md += f"- **Códigos Originais de Montadora (OEM):** {', '.join([f'`{o}`' for o in oem_list])}\n"
        md += f"- **Códigos Cruzados Equivalentes:** {', '.join([f'`{cr}`' for cr in cross_list])}\n\n"

        md += "---\n\n"
        md += "## 🛠️ Recomendações Importantes de Instalação\n\n"
        for a in alertas:
            md += f"- ⚠️ **{a}**\n"
        md += "- 🔧 Recomendamos sempre que a instalação seja feita por um profissional mecânico ou eletricista capacitado.\n"
        md += "- 🚫 Não force encaixes nem realize cortes em chicotes ou carcaças originais.\n\n"

        md += "---\n\n"
        md += "## ❓ Perguntas Frequentes (FAQ)\n\n"
        md += "**1. O produto é novo e original?**  \n"
        md += f"Sim! Trabalhamos apenas com produtos 100% novos, lacrados na caixa oficial {marca} e com procedência comprovada.\n\n"
        md += "**2. Acompanha Nota Fiscal?**  \n"
        md += "Sim! Todos os nossos pedidos acompanham Nota Fiscal Eletrônica (NF-e) emitida no nome do comprador (CPF ou CNPJ).\n\n"
        md += "**3. Em quanto tempo é feito o envio?**  \n"
        md += f"Temos estoque físico a pronta entrega ({qtd} unidades). Pedidos confirmados são despachados em até 24 horas úteis via Mercado Envios com código de rastreamento.\n\n"
        md += "**4. Como tenho certeza que serve no meu carro?**  \n"
        md += "Basta conferir a tabela de aplicação acima ou comparar o código gravado na sua peça antiga. Se precisar, envie uma pergunta no anúncio com o ano e modelo do seu carro que ajudamos na hora!\n\n"

        md += "---\n\n"
        md += "## 🛡️ Garantia e Suporte BUSK Peças\n\n"
        md += f"- **Garantia:** {garantia} Meses de garantia oficial contra defeitos de fabricação.\n"
        md += "- **Devolução:** Devolução grátis em até 30 dias caso o produto não seja o esperado, conforme as políticas do Mercado Livre.\n"
        md += "- **Atendimento:** Suporte técnico pré e pós-venda para esclarecer dúvidas e auxiliar na sua compra.\n"

        with open(filepath, "w", encoding="utf-8") as out_f:
            out_f.write(md)

    conn.close()
    print(f"[✓] {len(pecas)} anúncios comerciais do Lote 2 gerados em: {OUTPUT_LISTINGS_DIR}")


if __name__ == "__main__":
    generate_listings()
