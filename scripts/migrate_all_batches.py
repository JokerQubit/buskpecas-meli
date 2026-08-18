#!/usr/bin/env python3
"""
scripts/migrate_all_batches.py
------------------------------
Consolida o Lote 1 (51 peças) e o Lote 2 (58 peças) totalizando 109 SKUs:
1. Cria 'data/enriched_catalog_master_109.json';
2. Recria e migra o banco relacional 'database/autoparts_master.db' com 109 registros em 'tb_pecas'
   e todas as relações veiculares N:N em 'tb_compatibilidade_veicular'.
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

ENRICHED_BATCH1_PATH = os.path.join("data", "enriched_catalog_51.json")
ENRICHED_BATCH2_PATH = os.path.join("data", "enriched_catalog_batch2.json")
MASTER_JSON_PATH = os.path.join("data", "enriched_catalog_master_109.json")
DB_PATH = os.path.join("database", "autoparts_master.db")


def consolidate_and_migrate():
    print("[*] Consolidando Lote 1 e Lote 2...")
    with open(ENRICHED_BATCH1_PATH, "r", encoding="utf-8") as f1:
        data1 = json.load(f1)
    with open(ENRICHED_BATCH2_PATH, "r", encoding="utf-8") as f2:
        data2 = json.load(f2)

    items1 = data1.get("itens", [])
    items2 = data2.get("itens", [])

    for i in items1:
        if "origem_dados" not in i or not i["origem_dados"]:
            i["origem_dados"] = {"arquivo_fonte": "lista_51_itens_corrigida.pdf", "lote": 1}

    all_items = items1 + items2

    if len(all_items) != 109:
        print(f"[!] Atenção: Total de itens combinados é {len(all_items)} (esperava-se 109)")

    total_unidades = sum(i["quantidade_estoque"] for i in all_items)
    total_gmv = sum(i["preco_venda"] * i["quantidade_estoque"] for i in all_items)
    total_comissao = sum(i["comissao_10_pct"] * i["quantidade_estoque"] for i in all_items)

    master_data = {
        "metadata": {
            "total_skus_cadastrados": len(all_items),
            "total_unidades_fisicas_estoque": total_unidades,
            "faturamento_bruto_potencial_total_brl": round(total_gmv, 2),
            "comissao_liquida_10_pct_total_brl": round(total_comissao, 2),
            "lotes_integrados": [
                {"lote": 1, "arquivo": "lista_51_itens_corrigida.pdf", "skus": len(items1)},
                {"lote": 2, "arquivo": "Novo Documento de Texto.txt", "skus": len(items2)}
            ]
        },
        "itens": all_items
    }

    with open(MASTER_JSON_PATH, "w", encoding="utf-8") as mf:
        json.dump(master_data, mf, indent=2, ensure_ascii=False)
    print(f"[✓] Dataset mestre salvo em: {MASTER_JSON_PATH}")

    # Migração no SQLite
    print(f"[*] Populando banco de dados SQLite: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    # Schema
    c.execute("""
    CREATE TABLE tb_pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_master TEXT UNIQUE NOT NULL,
        nome_comercial_base TEXT NOT NULL,
        marca_fabricante TEXT NOT NULL,
        codigo_fabricante TEXT NOT NULL,
        codigos_oem TEXT NOT NULL,
        codigos_cruzados TEXT NOT NULL,
        categoria_nivel_1 TEXT NOT NULL,
        categoria_nivel_2 TEXT NOT NULL,
        posicao_instalacao TEXT,
        quantidade_estoque INTEGER NOT NULL DEFAULT 1,
        preco_venda REAL NOT NULL,
        comissao_10_pct REAL NOT NULL,
        faturamento_total_estoque REAL NOT NULL,
        comissao_total_estoque REAL NOT NULL,
        garantia_meses INTEGER NOT NULL DEFAULT 3,
        especificacoes_tecnicas TEXT NOT NULL,
        alertas_compatibilidade TEXT NOT NULL,
        diferenciais_competitivos TEXT NOT NULL,
        origem_dados TEXT NOT NULL,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    c.execute("""
    CREATE TABLE tb_compatibilidade_veicular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER NOT NULL REFERENCES tb_pecas(id) ON DELETE CASCADE,
        montadora TEXT NOT NULL,
        veiculo_modelo TEXT NOT NULL,
        versao TEXT,
        motorizacao TEXT,
        combustivel TEXT,
        ano_inicio INTEGER NOT NULL,
        ano_fim INTEGER,
        notas_especiais TEXT,
        FOREIGN KEY (peca_id) REFERENCES tb_pecas(id)
    );
    """)

    c.execute("CREATE INDEX idx_pecas_codigo ON tb_pecas(codigo_fabricante);")
    c.execute("CREATE INDEX idx_pecas_sku ON tb_pecas(sku_master);")
    c.execute("CREATE INDEX idx_compat_busca ON tb_compatibilidade_veicular(montadora, veiculo_modelo, ano_inicio);")
    c.execute("CREATE INDEX idx_compat_peca_id ON tb_compatibilidade_veicular(peca_id);")

    total_relations = 0
    for item in all_items:
        faturamento_item = round(item["preco_venda"] * item["quantidade_estoque"], 2)
        comissao_item = round(item["comissao_10_pct"] * item["quantidade_estoque"], 2)

        c.execute("""
        INSERT INTO tb_pecas (
            id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante,
            codigos_oem, codigos_cruzados, categoria_nivel_1, categoria_nivel_2,
            posicao_instalacao, quantidade_estoque, preco_venda, comissao_10_pct,
            faturamento_total_estoque, comissao_total_estoque, garantia_meses,
            especificacoes_tecnicas, alertas_compatibilidade, diferenciais_competitivos,
            origem_dados
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            item["id"],
            item["sku_master"],
            item["nome_comercial_base"],
            item["marca_fabricante"],
            item["codigo_fabricante"],
            json.dumps(item["codigos_oem"], ensure_ascii=False),
            json.dumps(item["codigos_cruzados"], ensure_ascii=False),
            item["categoria_nivel_1"],
            item["categoria_nivel_2"],
            item.get("posicao_instalacao") or "Conforme Aplicação",
            item["quantidade_estoque"],
            item["preco_venda"],
            item["comissao_10_pct"],
            faturamento_item,
            comissao_item,
            item["garantia_meses"],
            json.dumps(item["especificacoes_tecnicas"], ensure_ascii=False),
            json.dumps(item.get("alertas_compatibilidade", []), ensure_ascii=False),
            json.dumps(item.get("diferenciais_competitivos", []), ensure_ascii=False),
            json.dumps(item.get("origem_dados", {}), ensure_ascii=False)
        ))

        db_peca_id = item["id"]
        for comp in item.get("compatibilidade_veicular", []):
            c.execute("""
            INSERT INTO tb_compatibilidade_veicular (
                peca_id, montadora, veiculo_modelo, versao, motorizacao, combustivel, ano_inicio, ano_fim, notas_especiais
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                db_peca_id,
                comp["montadora"],
                comp["veiculo_modelo"],
                comp.get("versao"),
                comp.get("motorizacao"),
                comp.get("combustivel"),
                comp["ano_inicio"],
                comp.get("ano_fim"),
                comp.get("notas_especiais")
            ))
            total_relations += 1

    conn.commit()
    conn.close()

    print(f"[✓] Banco de dados SQLite populado com sucesso!")
    print(f"    - Total de Peças em 'tb_pecas': {len(all_items)}")
    print(f"    - Total de Aplicações em 'tb_compatibilidade_veicular': {total_relations}")
    print(f"    - Total de Unidades Físicas em Estoque: {total_unidades}")
    print(f"    - GMV Bruto Consolidado: R$ {total_gmv:,.2f}")
    print(f"    - Comissão Líquida 10% Consolidada: R$ {total_comissao:,.2f}")


if __name__ == "__main__":
    consolidate_and_migrate()
