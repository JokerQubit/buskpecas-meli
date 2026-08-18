#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("database/autoparts_master.db")
c = conn.cursor()
c.execute("PRAGMA table_info(tb_compatibilidade_veicular);")
for col in c.fetchall():
    print(col)
c.execute("PRAGMA table_info(tb_pecas);")
for col in c.fetchall():
    print(col)
conn.close()
