#!/usr/bin/env python3
"""
Retry para bairros que falharam na primeira rodada.
"""
import json
import time
import urllib.request
import urllib.parse
import urllib.error

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bairros que retornaram 0 por erro (não por ausência real de dados)
RETRY_BAIRROS = {
    "Estreito": (-27.5753, -48.5811),
    "Capoeiras": (-27.5980, -48.5620),
    "Saco dos Limoes": (-27.6300, -48.5050),
    "Roçado": (-27.6283, -48.5120),
    "Morro das Pedras": (-27.6830, -48.4850),
    "Campinas": (-27.5830, -48.5670),
    "Centro": (-27.5969, -48.5495),
    "Trindade": (-27.5997, -48.5224),
    "Agronômica": (-27.5883, -48.5356),
    "Itacorubi": (-27.5800, -48.5037),
    "Ribeirão da Ilha": (-27.7700, -48.5467),
    "Tapera": (-27.6817, -48.5400),
    "Rio Tavares": (-27.6550, -48.4750),
    "Santinho": (-27.4183, -48.3983),
    "Ponta das Canas": (-27.4507, -48.4772),
    "Vargem do Bom Jesus": (-27.4550, -48.4450),
    "Daniela": (-27.4717, -48.5383),
    "Praia Brava": (-27.4217, -48.4400),
    "Cachoeira do Bom Jesus": (-27.4383, -48.4350),
    "Lagoa da Conceição": (-27.6067, -48.4567),
    "Barra da Lagoa": (-27.5767, -48.4200),
}

def build_query(lat, lng, radius=1500):
    return f"""
[out:json][timeout:15];
(
  node["amenity"~"clinic|doctors|hospital|health_post"](around:{radius},{lat},{lng});
  way["amenity"~"clinic|doctors|hospital|health_post"](around:{radius},{lat},{lng});
  node["healthcare"](around:{radius},{lat},{lng});
  way["healthcare"](around:{radius},{lat},{lng});
  node["amenity"="school"](around:{radius},{lat},{lng});
  way["amenity"="school"](around:{radius},{lat},{lng});
  node["amenity"="kindergarten"](around:{radius},{lat},{lng});
  way["amenity"="kindergarten"](around:{radius},{lat},{lng});
  node["childcare"](around:{radius},{lat},{lng});
  way["childcare"](around:{radius},{lat},{lng});
  node["leisure"="park"](around:{radius},{lat},{lng});
  way["leisure"="park"](around:{radius},{lat},{lng});
  relation["leisure"="park"](around:{radius},{lat},{lng});
  node["leisure"~"garden|square"](around:{radius},{lat},{lng});
  way["leisure"~"garden|square"](around:{radius},{lat},{lng});
);
out tags;
"""

def query_overpass(lat, lng, bairro_name, retries=3):
    result = {"ubs": 0, "escola": 0, "creche": 0, "parque": 0, "praca": 0}
    
    for attempt in range(retries):
        query = build_query(lat, lng)
        data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        
        try:
            req = urllib.request.Request(
                OVERPASS_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
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
                
                if amenity in ("clinic", "doctors", "hospital", "health_post") or healthcare:
                    ids_saude.add(uid)
                elif amenity == "school":
                    ids_escola.add(uid)
                elif amenity == "kindergarten" or childcare:
                    ids_creche.add(uid)
                elif leisure == "park":
                    ids_parque.add(uid)
                elif leisure in ("garden", "square"):
                    ids_praca.add(uid)
            
            result["ubs"] = len(ids_saude)
            result["escola"] = len(ids_escola)
            result["creche"] = len(ids_creche)
            result["parque"] = len(ids_parque)
            result["praca"] = len(ids_praca)
            
            print(f"  ✓ {bairro_name}: saúde={result['ubs']}, escola={result['escola']}, creche={result['creche']}, parque={result['parque']}, praça={result['praca']}")
            return result
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 8 * (attempt + 1)
                print(f"  ⏳ {bairro_name}: 429 rate limit, aguardando {wait}s (tentativa {attempt+1})")
                time.sleep(wait)
            else:
                wait = 5 * (attempt + 1)
                print(f"  ⏳ {bairro_name}: HTTP {e.code}, aguardando {wait}s (tentativa {attempt+1})")
                time.sleep(wait)
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"  ⏳ {bairro_name}: {e}, aguardando {wait}s (tentativa {attempt+1})")
            time.sleep(wait)
    
    print(f"  ✗ {bairro_name}: FALHOU após {retries} tentativas — mantendo zeros")
    return result

def main():
    # Carregar dados existentes
    with open("/root/projects/floripa-patrimonio/data/osm_equipamentos.json", "r") as f:
        existing = json.load(f)
    
    bairros_list = list(RETRY_BAIRROS.items())
    total = len(bairros_list)
    
    print(f"Retry de {total} bairros com falha...\n")
    
    for i, (nome, (lat, lng)) in enumerate(bairros_list, 1):
        print(f"[{i}/{total}] {nome}")
        equipamentos = query_overpass(lat, lng, nome)
        existing[nome]["equipamentos"] = equipamentos
        
        if i < total:
            time.sleep(2.0)  # rate limiting mais conservador
    
    out_path = "/root/projects/floripa-patrimonio/data/osm_equipamentos.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados atualizados em {out_path}")

if __name__ == "__main__":
    main()
