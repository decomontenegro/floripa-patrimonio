#!/usr/bin/env python3
"""
Motor de vocação patrimonial de Florianópolis
Gera data/vocacao.json a partir de:
  - data/osm_equipamentos.json
  - data/imoveis.json
  - data/bairros_stats.json
"""

import json
import math

# ---------- Configurações ----------
POPULACOES = {
    "Centro": 42000, "Estreito": 28000, "Capoeiras": 22000, "Campinas": 18000,
    "Coqueiros": 15000, "Agronômica": 14000, "Trindade": 20000, "Itacorubi": 16000,
    "Córrego Grande": 8000, "Canasvieiras": 12000, "Ingleses": 35000, "Campeche": 28000,
    "Saco dos Limoes": 11000, "Roçado": 9000, "Morro das Pedras": 7000, "Armacao": 6000,
    "Tapera": 5000, "Carianos": 4000, "Rio Tavares": 8000, "Lagoa da Conceição": 9000,
    "Barra da Lagoa": 4000, "Costeira do Pirajubaé": 6000, "Ribeirão da Ilha": 8000,
    "Pântano do Sul": 3000, "Daniela": 5000, "Jurerê Internacional": 8000,
    "Ratones": 3000, "Santo Antônio de Lisboa": 4000, "Ponta das Canas": 6000,
    "Santinho": 3000, "Praia Brava": 4000, "Cachoeira do Bom Jesus": 5000,
    "Vargem Grande": 6000, "Vargem do Bom Jesus": 4000, "Não Identificado": 0
}

# Áreas aproximadas dos bairros em km² para calcular densidade
AREAS_KM2 = {
    "Centro": 3.2, "Estreito": 3.8, "Capoeiras": 4.2, "Campinas": 2.5,
    "Coqueiros": 2.8, "Agronômica": 2.1, "Trindade": 3.5, "Itacorubi": 4.1,
    "Córrego Grande": 2.2, "Canasvieiras": 5.5, "Ingleses": 7.0, "Campeche": 8.5,
    "Saco dos Limoes": 3.0, "Roçado": 3.2, "Morro das Pedras": 4.0, "Armacao": 5.5,
    "Tapera": 6.0, "Carianos": 3.5, "Rio Tavares": 9.0, "Lagoa da Conceição": 12.0,
    "Barra da Lagoa": 3.5, "Costeira do Pirajubaé": 4.0, "Ribeirão da Ilha": 15.0,
    "Pântano do Sul": 8.0, "Daniela": 4.5, "Jurerê Internacional": 6.0,
    "Ratones": 10.0, "Santo Antônio de Lisboa": 5.5, "Ponta das Canas": 4.5,
    "Santinho": 4.0, "Praia Brava": 3.5, "Cachoeira do Bom Jesus": 5.0,
    "Vargem Grande": 8.0, "Vargem do Bom Jesus": 6.5, "Não Identificado": 50.0
}

# ---------- Carregar dados ----------
BASE = "/root/projects/floripa-patrimonio/data"

with open(f"{BASE}/osm_equipamentos.json") as f:
    osm = json.load(f)

with open(f"{BASE}/imoveis.json") as f:
    imoveis = json.load(f)

with open(f"{BASE}/bairros_stats.json") as f:
    bairros_stats_list = json.load(f)

# Index bairros_stats por nome
bairros_stats = {b["bairro"]: b for b in bairros_stats_list}

# ---------- Pre-calcular stats por bairro ----------
bairro_imoveis = {}
for im in imoveis:
    nome = im["bairro"]
    if nome not in bairro_imoveis:
        bairro_imoveis[nome] = []
    bairro_imoveis[nome].append(im)

def get_bairro_stats(nome):
    ims = bairro_imoveis.get(nome, [])
    sem_uso = [x for x in ims if x.get("sem_uso")]
    areas_com_valor = [x["area"] for x in ims if x.get("area", 0) > 0]
    area_sem_uso = sum(x.get("area", 0) for x in sem_uso)
    area_media = sum(areas_com_valor) / len(areas_com_valor) if areas_com_valor else 0

    # Zoneamentos disponíveis
    zonas = {}
    for im in ims:
        z = im.get("zoneamento", "N/A") or "N/A"
        zonas[z] = zonas.get(z, 0) + 1

    return {
        "sem_uso_count": len(sem_uso),
        "area_sem_uso_m2": round(area_sem_uso, 2),
        "area_media": area_media,
        "zonas": zonas,
        "total": len(ims)
    }

def tem_zona(zonas, prefixo):
    return any(z.startswith(prefixo) for z in zonas if z != "N/A")

def has_zona_compat(zonas, tipos_zona):
    for z in zonas:
        for t in tipos_zona:
            if z.startswith(t):
                return True
    return False

# ---------- Motor de vocação ----------
def calcular_vocacoes(nome):
    pop = POPULACOES.get(nome, 0)
    area_km2 = AREAS_KM2.get(nome, 5.0)
    densidade = pop / area_km2 if area_km2 > 0 else 0
    alta_densidade = densidade > 5000

    equip = osm.get(nome, {}).get("equipamentos", {"ubs": 0, "escola": 0, "creche": 0, "parque": 0, "praca": 0})
    stats = get_bairro_stats(nome)
    sem_uso = stats["sem_uso_count"] > 0
    area_media = stats["area_media"]
    grande_area = area_media > 500
    zonas = stats["zonas"]

    # Calcular equipamentos por 10k hab
    fator = (pop / 10000) if pop > 0 else 1
    fator = max(fator, 0.1)

    ubs_p10k = equip.get("ubs", 0) / fator
    escola_p10k = equip.get("escola", 0) / fator
    creche_p10k = equip.get("creche", 0) / fator
    parque_p10k = equip.get("parque", 0) / fator

    gaps = []
    if ubs_p10k < 2:
        gaps.append("saude")
    if escola_p10k < 3:
        gaps.append("educacao")
    if creche_p10k < 2:
        gaps.append("creche")
    if parque_p10k < 1:
        gaps.append("ambiental")

    # Calcular score para cada tipo de vocação (capped at 100)
    vocacoes = []

    def calc_score(gap_tipo, zonas_compat, label, tipo):
        score = 0
        justifs = []

        # +30 gap crítico
        if gap_tipo in gaps:
            score += 30
            justifs.append(f"Gap crítico de {gap_tipo.capitalize()}")

        # +20 imóveis sem uso disponíveis
        if sem_uso:
            score += 20
            justifs.append("Imóveis sem uso disponíveis")

        # +20 alta densidade
        if alta_densidade:
            score += 20
            justifs.append("Alta densidade demográfica")

        # +15 zoneamento compatível
        if zonas_compat and has_zona_compat(zonas, zonas_compat):
            score += 15
            justifs.append(f"Zoneamento compatível ({'/'.join(zonas_compat)})")

        # +15 área média > 500m²
        if grande_area:
            score += 15
            justifs.append("Área média dos imóveis > 500m²")

        score = min(score, 100)  # cap at 100

        if score >= 20:  # só listar se tiver relevância mínima
            vocacoes.append({
                "tipo": tipo,
                "label": label,
                "score": score,
                "justificativa": ", ".join(justifs) if justifs else "Análise geoespacial"
            })

    # Saúde
    calc_score("saude", ["AMC", "ARP", "ACI"], "🏥 Unidade de Saúde (UBS)", "saude")

    # Educação (escola ou creche = gap de educação)
    if "educacao" in gaps or "creche" in gaps:
        score = 0
        justifs = []
        if "educacao" in gaps:
            score += 30
            justifs.append("Gap crítico de Escolas")
        if "creche" in gaps:
            score += 15
            justifs.append("Gap crítico de Creches")
        if sem_uso:
            score += 20
            justifs.append("Imóveis sem uso disponíveis")
        if alta_densidade:
            score += 20
            justifs.append("Alta densidade demográfica")
        if has_zona_compat(zonas, ["ARP", "AMC"]):
            score += 15
            justifs.append("Zoneamento residencial/misto compatível")
        score = min(score, 100)
        if score >= 20:
            vocacoes.append({
                "tipo": "educacao",
                "label": "🎓 Escola / Creche",
                "score": score,
                "justificativa": ", ".join(justifs)
            })
    else:
        # Se não há gap, verifica se há vocação menor
        if sem_uso or grande_area:
            score = 0
            justifs = []
            if sem_uso:
                score += 20
                justifs.append("Imóveis sem uso disponíveis")
            if has_zona_compat(zonas, ["ARP", "AMC"]):
                score += 15
                justifs.append("Zoneamento compatível")
            if grande_area:
                score += 15
                justifs.append("Área disponível")
            score = min(score, 100)
            if score >= 20:
                vocacoes.append({
                    "tipo": "educacao",
                    "label": "🎓 Escola / Creche",
                    "score": score,
                    "justificativa": ", ".join(justifs)
                })

    # Habitação Social
    calc_score("habitacao", ["ARP", "AMC"], "🏘️ Habitação Social (HIS)", "habitacao")

    # Ambiental / Parque
    calc_score("ambiental", ["ARE", "APP"], "🌳 Parque Urbano / Lazer", "ambiental")

    # Infraestrutura / Logística
    calc_score("infraestrutura", ["ACI"], "🏗️ Infraestrutura / Logística", "infraestrutura")

    # Econômico / Incubadora
    calc_score("economico", ["AMC", "ACI"], "💼 Hub Econômico / Incubadora", "economico")

    # Cultural
    calc_score("cultural", ["ARE", "AMC"], "🎭 Centro Cultural / Espaço Público", "cultural")

    # Concessão
    if not sem_uso and pop > 0:
        score = 0
        justifs = []
        if alta_densidade:
            score += 20
            justifs.append("Alta densidade — oportunidade de concessão")
        if has_zona_compat(zonas, ["AMC", "ACI"]):
            score += 15
            justifs.append("Zoneamento misto favorável")
        if grande_area:
            score += 15
            justifs.append("Área disponível para concessão")
        score = min(score, 100)
        if score >= 20:
            vocacoes.append({
                "tipo": "concessao",
                "label": "🏢 Concessão / PPP",
                "score": score,
                "justificativa": ", ".join(justifs)
            })

    # Ambiental especial para APP
    if has_zona_compat(zonas, ["APP"]):
        score = 0
        justifs = ["Zona de Proteção Permanente — preservação obrigatória"]
        score = 30
        if grande_area:
            score += 15
            justifs.append("Grandes áreas preservadas")
        score = min(score, 100)
        if score >= 20:
            vocacoes.append({
                "tipo": "ambiental",
                "label": "🌿 Preservação / Trilha Ecológica",
                "score": score,
                "justificativa": ", ".join(justifs)
            })

    # Ordenar por score decrescente, remover duplicatas de tipo
    seen_tipos = set()
    vocacoes_uniq = []
    for v in sorted(vocacoes, key=lambda x: -x["score"]):
        if v["tipo"] not in seen_tipos:
            seen_tipos.add(v["tipo"])
            vocacoes_uniq.append(v)

    return {
        "populacao": pop,
        "equipamentos": equip,
        "gaps": gaps,
        "sem_uso_count": stats["sem_uso_count"],
        "area_sem_uso_m2": stats["area_sem_uso_m2"],
        "vocacoes": vocacoes_uniq[:5]  # top 5 vocações
    }

# ---------- Gerar para todos os bairros ----------
resultado = {}
for nome in POPULACOES.keys():
    resultado[nome] = calcular_vocacoes(nome)

output = {"bairros": resultado}

with open(f"{BASE}/vocacao.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ vocacao.json gerado com {len(resultado)} bairros")

# Mostrar top 10 por score
top10 = sorted(
    [(nome, d["vocacoes"][0]["score"], d["vocacoes"][0]["label"], d["area_sem_uso_m2"])
     for nome, d in resultado.items() if d.get("vocacoes")],
    key=lambda x: -x[1]
)[:10]

print("\n🏆 TOP 10 BAIRROS POR SCORE DE OPORTUNIDADE:")
for i, (nome, score, label, area) in enumerate(top10, 1):
    print(f"  {i:2}. {nome:<30} Score: {score:3d}  {label}  (Área sem uso: {area:,.0f} m²)")
