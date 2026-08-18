#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect("database/autoparts_master.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, sku_master, nome_comercial_base, marca_fabricante, codigo_fabricante, preco_venda, quantidade_estoque FROM tb_pecas WHERE id >= 95 ORDER BY id ASC;")
pecas = c.fetchall()

print("Verificando peças 95 a 109:")
for p in pecas:
    print(f"ID {p['id']:03d} | SKU: {p['sku_master']} | Marca: {p['marca_fabricante']} | Cod: {p['codigo_fabricante']} | Preço: R$ {p['preco_venda']} | Est: {p['quantidade_estoque']}")

conn.close()
