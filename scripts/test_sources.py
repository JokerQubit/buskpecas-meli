#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import re
import sys

# Forçar stdout UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def test_ddg_images(query: str):
    print(f"[*] Testando busca DuckDuckGo Images para: '{query}'")
    # DuckDuckGo Image Search token & query
    url = f"https://duckduckgo.com/i.js?q={urllib.parse.quote(query)}&o=json&p=1&s=0&u=bing&f=,,,&l=br-pt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://duckduckgo.com/"
    }
    
    # 1. Pega vqd token
    token_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(token_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            match = re.search(r'vqd=([\d-]+)', html) or re.search(r'vqd="([^"]+)"', html)
            if match:
                vqd = match.group(1)
                print(f"[✓] VQD Token obtido: {vqd}")
                
                img_url = f"https://duckduckgo.com/i.js?q={urllib.parse.quote(query)}&o=json&p=1&s=0&u=bing&f=,,,&l=br-pt&vqd={vqd}"
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                    data = json.loads(img_resp.read().decode('utf-8', errors='replace'))
                    results = data.get("results", [])
                    print(f"[✓] Resultados encontrados: {len(results)}")
                    for idx, r in enumerate(results[:4], start=1):
                        print(f"    Foto {idx}: {r.get('image')[:90]}... (Dimensões: {r.get('width')}x{r.get('height')})")
                    return [r.get('image') for r in results[:4]]
            else:
                print("[!] VQD Token não encontrado no HTML.")
    except Exception as e:
        print(f"[!] Erro no DuckDuckGo: {e}")
    return []


if __name__ == "__main__":
    test_ddg_images("Kostal 10013879 Celta")
    test_ddg_images("Sabó 80270")
    test_ddg_images("Arteb 160818 Astra")
