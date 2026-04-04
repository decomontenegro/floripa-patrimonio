#!/usr/bin/env python3
"""
Geocode top100.json usando Nominatim (OpenStreetMap) — gratuito, sem API key.
Estratégia por prioridade:
  1. Busca por finalidade + bairro + Florianópolis SC
  2. Busca por caracterizacao + bairro + Florianópolis SC
  3. Busca por bairro + Florianópolis SC (fallback — centróide do bairro)
"""

import json, time, urllib.request, urllib.parse, sys, os

INPUT  = os.path.join(os.path.dirname(__file__), "data/top100.json")
OUTPUT = os.path.join(os.path.dirname(__file__), "data/top100.json")
BACKUP = os.path.join(os.path.dirname(__file__), "data/top100_backup.json")

HEADERS = {"User-Agent": "floripa-patrimonio-geocoder/1.0 (github.com/decomontenegro/floripa-patrimonio)"}

def geocode(query):
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "br",
        "viewbox": "-48.65,-27.80,-48.35,-27.40",
        "bounded": 1
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name","")
    except Exception as e:
        print(f"  ERR: {e}")
    return None, None, None

def build_queries(item):
    bairro = item.get("bairro","")
    cidade = f"{bairro}, Florianópolis, SC, Brasil"
    finalidade = (item.get("finalidade") or "").strip()
    caract = (item.get("caracterizacao") or "").strip()
    
    queries = []
    # Tenta com finalidade específica
    if finalidade and finalidade not in ("", "N/A") and len(finalidade) > 3:
        skip = {"ACI", "ACI 1", "ACI 2", "ACI 3", "AVL", "AV - 02", "AV - 03", "AVL - 01",
                "ACI - Área Comunitária Institucional", "Area A3", "Area 4", "Area 5", "Área 1"}
        if finalidade not in skip:
            queries.append(f"{finalidade}, {cidade}")
    # Tenta com caracterização específica
    if caract and caract.lower() not in ("sem uso", "sem Uso", "outros", "n/a") and len(caract) > 5:
        queries.append(f"{caract}, {cidade}")
    # Fallback: centróide do bairro
    queries.append(f"{bairro}, Florianópolis, SC, Brasil")
    return queries

with open(INPUT) as f:
    data = json.load(f)

# Backup
with open(BACKUP, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Backup salvo em {BACKUP}")

# Mapa de centróides já conhecidos (fallback quando tudo falhar)
CENTROIDS = {
    "Lagoa da Conceição":     (-27.6008, -48.4688),
    "Coqueiros":              (-27.5639, -48.5828),
    "Campeche":               (-27.6791, -48.4880),
    "Armacao":                (-27.7264, -48.5033),
    "Barra da Lagoa":         (-27.5744, -48.4319),
    "Canasvieiras":           (-27.4744, -48.4672),
    "Jurere Internacional":   (-27.4628, -48.5015),
    "Sambaqui":               (-27.4944, -48.5478),
    "Ingleses":               (-27.4367, -48.3990),
    "Cachoeira do Bom Jesus": (-27.4600, -48.4500),
    "Vargem Grande":          (-27.4717, -48.4278),
    "Estreito":               (-27.5753, -48.5811),
    "Ratones":                (-27.4950, -48.5050),
    "Itacorubi":              (-27.5817, -48.4978),
    "Morro das Pedras":       (-27.7017, -48.5067),
}

# Detectar quais imóveis têm coordenadas genéricas (centróide)
centroid_latlngs = set((v[0], v[1]) for v in CENTROIDS.values())

updated = 0
skipped = 0

for i, item in enumerate(data):
    lat = item.get("lat")
    lng = item.get("lng")
    is_generic = (lat, lng) in centroid_latlngs if lat and lng else True
    
    if not is_generic:
        print(f"[{i+1:3d}] fid={item['fid']} OK (coord específica) — pulando")
        skipped += 1
        continue

    print(f"[{i+1:3d}] fid={item['fid']} bairro={item.get('bairro')} — geocodificando...", end=" ", flush=True)
    
    queries = build_queries(item)
    new_lat, new_lng, display = None, None, None
    used_query = None
    
    for q in queries:
        new_lat, new_lng, display = geocode(q)
        used_query = q
        time.sleep(1.1)  # Nominatim: max 1 req/s
        if new_lat:
            break
    
    if new_lat:
        item["lat"] = round(new_lat, 6)
        item["lng"] = round(new_lng, 6)
        item["geocode_source"] = "nominatim"
        item["geocode_query"] = used_query
        print(f"✅ ({item['lat']}, {item['lng']}) via: {used_query[:60]}")
        updated += 1
    else:
        # Mantém centróide mas marca como aproximado
        item["geocode_source"] = "centroid_fallback"
        print(f"⚠️  fallback centróide — sem resultado Nominatim")

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Concluído: {updated} atualizados, {skipped} já tinham coord específica")
print(f"Arquivo salvo: {OUTPUT}")
