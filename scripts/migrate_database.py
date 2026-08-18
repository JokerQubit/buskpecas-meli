#!/usr/bin/env python3
"""
scripts/migrate_database.py
---------------------------
Cria e popula o banco de dados relacional SQLite 'database/autoparts_master.db'.
Executa o DDL estritamente tipado com chaves estrangeiras, índices e constraints.
Lê 'data/enriched_catalog_51.json' e insere todas as 51 peças e suas relações N:N.
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
ENRICHED_JSON_PATH = os.path.join("data", "enriched_catalog_51.json")


def init_database():
    print(f"[*] Inicializando migração do banco de dados relacional em: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if not os.path.exists(ENRICHED_JSON_PATH):
        raise FileNotFoundError(f"Arquivo enriquecido não encontrado: {ENRICHED_JSON_PATH}. Execute enrich_catalog_data.py primeiro.")

    with open(ENRICHED_JSON_PATH, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    items = catalog_data.get("itens", [])
    if len(items) != 51:
        raise ValueError(f"Divergência: esperava 51 itens, encontrou {len(items)}.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ativa integridade de chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Drop tables anteriores para garantir idempotência limpa
    cursor.execute("DROP TABLE IF EXISTS tb_compatibilidade_veicular;")
    cursor.execute("DROP TABLE IF EXISTS tb_pecas;")

    # Criação da tabela tb_pecas
    cursor.execute("""
    CREATE TABLE tb_pecas (
        id INTEGER PRIMARY KEY,
        sku_master TEXT UNIQUE NOT NULL,
        nome_comercial_base TEXT NOT NULL,
        marca_fabricante TEXT NOT NULL,
        codigo_fabricante TEXT NOT NULL,
        codigos_oem JSON NOT NULL,
        codigos_cruzados JSON NOT NULL,
        categoria_nivel_1 TEXT NOT NULL,
        categoria_nivel_2 TEXT NOT NULL,
        posicao_instalacao TEXT,
        quantidade_estoque INTEGER NOT NULL DEFAULT 1,
        preco_venda REAL NOT NULL,
        comissao_10_pct REAL NOT NULL,
        garantia_meses INTEGER NOT NULL DEFAULT 3,
        especificacoes_tecnicas JSON NOT NULL,
        termos_seo JSON NOT NULL,
        diferenciais_competitivos JSON NOT NULL,
        alertas_compatibilidade JSON NOT NULL,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Criação da tabela tb_compatibilidade_veicular
    cursor.execute("""
    CREATE TABLE tb_compatibilidade_veicular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER NOT NULL,
        montadora TEXT NOT NULL,
        veiculo_modelo TEXT NOT NULL,
        versao TEXT,
        motorizacao TEXT,
        combustivel TEXT,
        ano_inicio INTEGER NOT NULL,
        ano_fim INTEGER,
        notas_especiais TEXT,
        FOREIGN KEY (peca_id) REFERENCES tb_pecas(id) ON DELETE CASCADE
    );
    """)

    # Criação de índices de alta performance
    cursor.execute("CREATE INDEX idx_pecas_codigo ON tb_pecas(codigo_fabricante);")
    cursor.execute("CREATE INDEX idx_pecas_sku ON tb_pecas(sku_master);")
    cursor.execute("CREATE INDEX idx_compat_busca ON tb_compatibilidade_veicular(montadora, veiculo_modelo, ano_inicio);")
    cursor.execute("CREATE INDEX idx_compat_peca_id ON tb_compatibilidade_veicular(peca_id);")

    print("[+] Esquema DDL e índices criados com sucesso.")

    # Inserção em transação única
    pecas_inseridas = 0
    compat_inseridas = 0

    for item in items:
        cursor.execute("""
        INSERT INTO tb_pecas (
            id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante,
            codigos_oem, codigos_cruzados, categoria_nivel_1, categoria_nivel_2,
            posicao_instalacao, quantidade_estoque, preco_venda, comissao_10_pct,
            garantia_meses, especificacoes_tecnicas, termos_seo, diferenciais_competitivos, alertas_compatibilidade
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
            item["posicao_instalacao"],
            item["quantidade_estoque"],
            item["preco_venda"],
            item["comissao_10_pct"],
            item["garantia_meses"],
            json.dumps(item["especificacoes_tecnicas"], ensure_ascii=False),
            json.dumps(item["termos_seo"], ensure_ascii=False),
            json.dumps(item["diferenciais_competitivos"], ensure_ascii=False),
            json.dumps(item["alertas_compatibilidade"], ensure_ascii=False)
        ))
        pecas_inseridas += 1

        for compat in item["compatibilidade_veicular"]:
            cursor.execute("""
            INSERT INTO tb_compatibilidade_veicular (
                peca_id, montadora, veiculo_modelo, versao, motorizacao,
                combustivel, ano_inicio, ano_fim, notas_especiais
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                item["id"],
                compat["montadora"],
                compat["veiculo_modelo"],
                compat.get("versao"),
                compat.get("motorizacao"),
                compat.get("combustivel"),
                compat["ano_inicio"],
                compat.get("ano_fim"),
                compat.get("notas_especiais")
            ))
            compat_inseridas += 1

    conn.commit()
    conn.close()

    print(f"[✓] Migração concluída com sucesso!")
    print(f"    - Peças inseridas em 'tb_pecas': {pecas_inseridas}")
    print(f"    - Relações inseridas em 'tb_compatibilidade_veicular': {compat_inseridas}")
    print(f"    - Banco pronto para subagentes e consultas em: {DB_PATH}")


if __name__ == "__main__":
    init_database()
