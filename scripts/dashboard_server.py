#!/usr/bin/env python3
"""
scripts/dashboard_server.py
---------------------------
Servidor HTTP local leve para o Dashboard BUSK Peças.
Serve o frontend visual interativo, as imagens locais e fornece APIs REST:
- GET /api/pecas : retorna todas as 109 peças com fotos, dados e descrições
- GET /api/open_folder?id=X : abre a pasta de imagens correspondente no Windows Explorer
- GET /api/download_csv : baixa a planilha de carga em massa do Mercado Livre
"""

import os
import sys
import json
import sqlite3
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Forçar stdout UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PORT = 8088
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "autoparts_master.db")
ANUNCIOS_DIR = os.path.join(BASE_DIR, "docs", "anuncios")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DATA_DIR = os.path.join(BASE_DIR, "data")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")


class BuskDashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API: Lista de Peças
        if path == "/api/pecas":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM tb_pecas ORDER BY id ASC;")
            pecas = c.fetchall()

            data = []
            for p in pecas:
                p_id = p["id"]
                c.execute("SELECT * FROM tb_compatibilidade_veicular WHERE peca_id = ? ORDER BY montadora ASC, veiculo_modelo ASC, ano_inicio ASC;", (p_id,))
                compats = [dict(row) for row in c.fetchall()]

                # Busca fotos na pasta
                matching_folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith(f"PECA_{p_id:02d}_")]
                photos = []
                folder_name = ""
                if matching_folders:
                    folder_name = matching_folders[0]
                    fp = os.path.join(IMAGES_DIR, folder_name)
                    slides = [f for f in os.listdir(fp) if f.lower().startswith("slide") and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
                    slides.sort(key=lambda x: int(x.lower().replace("slide", "").replace(".png", "").replace(".jpg", "").replace(".webp", "").strip()))
                    for s in slides:
                        photos.append(f"/images/{folder_name}/{s}")

                # Busca anúncio markdown
                desc_text = ""
                titulo_final = p["nome_comercial_base"]
                anuncio_files = [f for f in os.listdir(ANUNCIOS_DIR) if f.startswith(f"ANUNCIO_{p_id:02d}_")]
                if anuncio_files:
                    af_path = os.path.join(ANUNCIOS_DIR, anuncio_files[0])
                    with open(af_path, "r", encoding="utf-8") as af:
                        desc_text = af.read()
                    for line in desc_text.splitlines():
                        if line.startswith("titulo_ml_principal:"):
                            titulo_final = line.replace("titulo_ml_principal:", "").strip().strip('"').strip("'")
                            break

                p_dict = dict(p)
                p_dict["compatibilidades"] = compats
                p_dict["fotos"] = photos
                p_dict["pasta_nome"] = folder_name
                p_dict["titulo_ml"] = titulo_final
                p_dict["anuncio_completo_md"] = desc_text
                data.append(p_dict)

            conn.close()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        # API: Abrir Pasta no Windows Explorer
        if path == "/api/open_folder":
            p_id = query.get("id", [None])[0]
            if p_id:
                p_id_int = int(p_id)
                matching_folders = [f for f in os.listdir(IMAGES_DIR) if f.startswith(f"PECA_{p_id_int:02d}_")]
                if matching_folders:
                    target_path = os.path.join(IMAGES_DIR, matching_folders[0])
                    if sys.platform == "win32":
                        os.startfile(target_path)
                    else:
                        subprocess.Popen(["xdg-open", target_path])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            return

        # Rota de Imagens locais
        if path.startswith("/images/"):
            rel_path = urllib.parse.unquote(path[len("/images/"):])
            full_path = os.path.join(IMAGES_DIR, rel_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if full_path.lower().endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif full_path.lower().endswith((".jpg", ".jpeg")):
                    self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                with open(full_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # Download da Planilha
        if path == "/data/planilha_carga_massa_mercadolivre_109.csv":
            csv_path = os.path.join(DATA_DIR, "planilha_carga_massa_mercadolivre_109.csv")
            if os.path.exists(csv_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8-sig")
                self.send_header("Content-Disposition", "attachment; filename=planilha_carga_massa_mercadolivre_109.csv")
                self.end_headers()
                with open(csv_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # Rota Padrão: Dashboard HTML
        index_path = os.path.join(DASHBOARD_DIR, "index.html")
        if os.path.exists(index_path):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(index_path, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_error(404, "Arquivo nao encontrado")


def start_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, BuskDashboardHandler)
    print("=" * 80)
    print(f"🚀 DASHBOARD BUSK PEÇAS INICIADO COM SUCESSO!")
    print(f"👉 Acesse no navegador: http://localhost:{PORT}")
    print("=" * 80)
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
