#!/usr/bin/env python3
"""
Coleta dados de equipamentos públicos via Overpass API (OSM)
para bairros de Florianópolis num raio de 1500m.
"""
import json
import time
import urllib.request
import urllib.parse
import urllib.error

BAIRROS = {
    "Estreito": (-27.5753, -48.5811),
    "Canasvieiras": (-27.4313, -48.4645),
    "Capoeiras": (-27.5980, -48.5620),
    "Ingleses": (-27.4383, -48.3923),
    "Coqueiros": (-27.5700, -48.5650),
    "Campeche": (-27.6743, -48.4669),
    "Saco dos Limoes": (-27.6300, -48.5050),
    "Roçado": (-27.6283, -48.5120),
    "Morro das Pedras": (-27.6830, -48.4850),
    "Armacao": (-27.7455, -48.5040),
    "Campinas": (-27.5830, -48.5670),
    "Centro": (-27.5969, -48.5495),
    "Trindade": (-27.5997, -48.5224),
    "Agronômica": (-27.5883, -48.5356),
    "Itacorubi": (-27.5800, -48.5037),
    "Córrego Grande": (-27.5947, -48.5009),
    "Costeira do Pirajubaé": (-27.6400, -48.5250),
    "Pântano do Sul": (-27.7917, -48.5017),
    "Ribeirão da Ilha": (-27.7700, -48.5467),
    "Carianos": (-27.6700, -48.5550),
    "Tapera": (-27.6817, -48.5400),
    "Rio Tavares": (-27.6550, -48.4750),
    "Santinho": (-27.4183, -48.3983),
    "Ponta das Canas": (-27.4507, -48.4772),
    "Vargem Grande": (-27.4683, -48.4350),
    "Vargem do Bom Jesus": (-27.4550, -48.4450),
    "Daniela": (-27.4717, -48.5383),
    "Jurerê Internacional": (-27.4467, -48.5317),
    "Praia Brava": (-27.4217, -48.4400),
    "Cachoeira do Bom Jesus": (-27.4383, -48.4350),
    "Ratones": (-27.5050, -48.5683),
    "Santo Antônio de Lisboa": (-27.5133, -48.5450),
    "Lagoa da Conceição": (-27.6067, -48.4567),
    "Barra da Lagoa": (-27.5767, -48.4200),
    "Não Identificado": (-27.5969, -48.5495),
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def build_query(lat, lng, radius=1500):
    """Monta query OverpassQL para todos os equipamentos de interesse."""
    return f"""
[out:json][timeout:10];
(
  // UBS / Saúde
  node["amenity"="clinic"](around:{radius},{lat},{lng});
  way["amenity"="clinic"](around:{radius},{lat},{lng});
  node["amenity"="doctors"](around:{radius},{lat},{lng});
  way["amenity"="doctors"](around:{radius},{lat},{lng});
  node["amenity"="hospital"](around:{radius},{lat},{lng});
  way["amenity"="hospital"](around:{radius},{lat},{lng});
  node["amenity"="health_post"](around:{radius},{lat},{lng});
  way["amenity"="health_post"](around:{radius},{lat},{lng});
  node["healthcare"](around:{radius},{lat},{lng});
  way["healthcare"](around:{radius},{lat},{lng});
  
  // Escolas
  node["amenity"="school"](around:{radius},{lat},{lng});
  way["amenity"="school"](around:{radius},{lat},{lng});
  
  // Creches
  node["amenity"="kindergarten"](around:{radius},{lat},{lng});
  way["amenity"="kindergarten"](around:{radius},{lat},{lng});
  node["childcare"](around:{radius},{lat},{lng});
  way["childcare"](around:{radius},{lat},{lng});
  
  // Parques
  node["leisure"="park"](around:{radius},{lat},{lng});
  way["leisure"="park"](around:{radius},{lat},{lng});
  relation["leisure"="park"](around:{radius},{lat},{lng});
  
  // Praças
  node["leisure"="garden"](around:{radius},{lat},{lng});
  way["leisure"="garden"](around:{radius},{lat},{lng});
  node["leisure"="square"](around:{radius},{lat},{lng});
  way["leisure"="square"](around:{radius},{lat},{lng});
);
out tags;
"""

def query_overpass(lat, lng, bairro_name):
    """Executa query na Overpass API e retorna contagens por tipo."""
    result = {"ubs": 0, "escola": 0, "creche": 0, "parque": 0, "praca": 0}
    
    query = build_query(lat, lng)
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    
    try:
        req = urllib.request.Request(
            OVERPASS_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            
        ids_saude = set()
        ids_escola = set()
        ids_creche = set()
        ids_parque = set()
        ids_praca = set()
        
        for el in parsed.get("elements", []):
            uid = f"{el['type']}_{el['id']}"
            tags = el.get("tags", {})
            amenity = tags.get("amenity", "")
            healthcare = tags.get("healthcare", "")
            leisure = tags.get("leisure", "")
            childcare = tags.get("childcare", "")
            
            # Saúde
            if amenity in ("clinic", "doctors", "hospital", "health_post") or healthcare:
                ids_saude.add(uid)
            # Escola
            elif amenity == "school":
                ids_escola.add(uid)
            # Creche
            elif amenity == "kindergarten" or childcare:
                ids_creche.add(uid)
            # Parque
            elif leisure == "park":
                ids_parque.add(uid)
            # Praça
            elif leisure in ("garden", "square"):
                ids_praca.add(uid)
        
        result["ubs"] = len(ids_saude)
        result["escola"] = len(ids_escola)
        result["creche"] = len(ids_creche)
        result["parque"] = len(ids_parque)
        result["praca"] = len(ids_praca)
        
        print(f"  ✓ {bairro_name}: saúde={result['ubs']}, escola={result['escola']}, creche={result['creche']}, parque={result['parque']}, praça={result['praca']}")
        
    except Exception as e:
        print(f"  ✗ {bairro_name}: ERRO — {e} — usando zeros")
    
    return result

def main():
    output = {}
    bairros_list = list(BAIRROS.items())
    total = len(bairros_list)
    
    print(f"Iniciando coleta OSM para {total} bairros...\n")
    
    for i, (nome, (lat, lng)) in enumerate(bairros_list, 1):
        print(f"[{i}/{total}] {nome}")
        equipamentos = query_overpass(lat, lng, nome)
        output[nome] = {
            "lat": lat,
            "lng": lng,
            "equipamentos": equipamentos
        }
        
        if i < total:
            time.sleep(0.8)  # rate limiting
    
    out_path = "/root/projects/floripa-patrimonio/data/osm_equipamentos.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados salvos em {out_path}")
    return output

if __name__ == "__main__":
    main()
