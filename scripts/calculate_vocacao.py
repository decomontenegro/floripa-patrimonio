#!/usr/bin/env python3
import json

def calculate_vocation_data():
    with open("/root/projects/floripa-patrimonio/data/imoveis.json", "r", encoding="utf-8") as f:
        imoveis_data = json.load(f)
    with open("/root/projects/floripa-patrimonio/data/osm_equipamentos.json", "r", encoding="utf-8") as f:
        osm_data = json.load(f)

    # Populações estimadas por bairro
    populacoes_bairro = {
        "Centro": 42000, "Estreito": 28000, "Capoeiras": 22000, "Campinas": 18000, "Coqueiros": 15000,
        "Agronômica": 14000, "Trindade": 20000, "Itacorubi": 16000, "Córrego Grande": 8000,
        "Canasvieiras": 12000, "Ingleses": 35000, "Campeche": 28000, "Saco dos Limoes": 11000,
        "Roçado": 9000, "Morro das Pedras": 7000, "Armacao": 6000, "Tapera": 5000, "Carianos": 4000,
        "Rio Tavares": 8000, "Lagoa da Conceição": 9000, "Barra da Lagoa": 4000,
        "Costeira do Pirajubaé": 6000, "Ribeirão da Ilha": 8000, "Pântano do Sul": 3000,
        "Daniela": 5000, "Jurerê Internacional": 8000, "Ratones": 3000,
        "Santo Antônio de Lisboa": 4000, "Ponta das Canas": 6000, "Santinho": 3000,
        "Praia Brava": 4000, "Cachoeira do Bom Jesus": 5000, "Vargem Grande": 6000,
        "Vargem do Bom Jesus": 4000, "Não Identificado": 0
    }

    # Agregação de dados de imóveis por bairro
    bairros_aggregated = {}
    for imovel in imoveis_data:
        bairro = imovel.get("bairro")
        if bairro not in bairros_aggregated:
            bairros_aggregated[bairro] = {
                "total_imoveis": 0,
                "sem_uso_count": 0,
                "area_sem_uso_m2": 0,
                "zoneamentos": {},
                "total_area": 0
            }
        
        bairros_aggregated[bairro]["total_imoveis"] += 1
        bairros_aggregated[bairro]["total_area"] += imovel.get("area", 0)
        
        if imovel.get("sem_uso"):
            bairros_aggregated[bairro]["sem_uso_count"] += 1
            bairros_aggregated[bairro]["area_sem_uso_m2"] += imovel.get("area", 0)

        zoneamento = imovel.get("zoneamento", "N/A") or "N/A"
        bairros_aggregated[bairro]["zoneamentos"][zoneamento] = \
            bairros_aggregated[bairro]["zoneamentos"].get(zoneamento, 0) + 1

    vocacao_data = {"bairros": {}}

    for bairro_name, stats in bairros_aggregated.items():
        if bairro_name not in populacoes_bairro:
            continue # Ignorar bairros sem população estimada

        populacao = populacoes_bairro.get(bairro_name, 0)
        equipamentos_osm = osm_data.get(bairro_name, {}).get("equipamentos", {"ubs": 0, "escola": 0, "creche": 0, "parque": 0, "praca": 0})
        
        gaps = []
        if populacao > 0:
            if (equipamentos_osm["ubs"] / (populacao / 10000)) < 2:
                gaps.append("saude")
            if (equipamentos_osm["escola"] / (populacao / 10000)) < 3:
                gaps.append("educacao")
            if (equipamentos_osm["creche"] / (populacao / 10000)) < 2:
                gaps.append("creche")
            if (equipamentos_osm["parque"] + equipamentos_osm["praca"]) / (populacao / 10000) < 1:
                gaps.append("lazer")
        
        vocacoes = []
        
        # Vocação - Saúde
        score_saude = 0
        justificativa_saude = []
        if "saude" in gaps:
            score_saude += 30
            justificativa_saude.append("Gap crítico de UBS/Postos de Saúde")
        if stats["sem_uso_count"] > 0:
            score_saude += 20
            justificativa_saude.append("Imóveis sem uso disponíveis")
        # Alta densidade (simplificado, sem calculo exato de km2 por falta de dados de area do bairro)
        if populacao > 15000: # Threshold arbitrario para "alta densidade" para Florianopolis
             score_saude += 20
             justificativa_saude.append("Bairro com alta população")
        if "AMC" in stats["zoneamentos"] or "ACI" in stats["zoneamentos"]:
            score_saude += 15
            justificativa_saude.append("Zoneamento compatível (AMC/ACI)")
        if stats["total_imoveis"] > 0 and (stats["total_area"] / stats["total_imoveis"]) > 500:
            score_saude += 15
            justificativa_saude.append("Área média dos imóveis > 500m²")
        if score_saude > 0:
            vocacoes.append({"tipo": "saude", "label": "🏥 Unidade de Saúde", "score": score_saude, "justificativa": ", ".join(justificativa_saude)})

        # Vocação - Educação (Escolas/Creches)
        score_educacao = 0
        justificativa_educacao = []
        if "educacao" in gaps:
            score_educacao += 30
            justificativa_educacao.append("Gap crítico de Escolas")
        if "creche" in gaps:
            score_educacao += 30
            justificativa_educacao.append("Gap crítico de Creches")
        if stats["sem_uso_count"] > 0:
            score_educacao += 20
            justificativa_educacao.append("Imóveis sem uso disponíveis")
        if populacao > 15000:
            score_educacao += 20
            justificativa_educacao.append("Bairro com alta população")
        if "ARP" in stats["zoneamentos"] or "AMC" in stats["zoneamentos"]:
            score_educacao += 15
            justificativa_educacao.append("Zoneamento compatível (ARP/AMC)")
        if stats["total_imoveis"] > 0 and (stats["total_area"] / stats["total_imoveis"]) > 500:
            score_educacao += 15
            justificativa_educacao.append("Área média dos imóveis > 500m²")
        if score_educacao > 0:
            vocacoes.append({"tipo": "educacao", "label": "🎓 Escola / Creche", "score": score_educacao, "justificativa": ", ".join(justificativa_educacao)})

        # Vocação - Habitacao Social (HIS)
        score_habitacao = 0
        justificativa_habitacao = []
        if stats["sem_uso_count"] > 0:
            score_habitacao += 20
            justificativa_habitacao.append("Imóveis sem uso disponíveis")
        if populacao > 15000:
            score_habitacao += 20
            justificativa_habitacao.append("Bairro com alta população")
        if "ARP" in stats["zoneamentos"] or "AMC" in stats["zoneamentos"]:
            score_habitacao += 15
            justificativa_habitacao.append("Zoneamento compatível (ARP/AMC)")
        if stats["total_imoveis"] > 0 and (stats["total_area"] / stats["total_imoveis"]) > 500:
            score_habitacao += 15
            justificativa_habitacao.append("Área média dos imóveis > 500m²")
        if score_habitacao > 0:
            vocacoes.append({"tipo": "habitacao", "label": "🏘️ Habitação Social (HIS)", "score": score_habitacao, "justificativa": ", ".join(justificativa_habitacao)})
        
        # Vocação - Ambiental/Lazer
        score_ambiental = 0
        justificativa_ambiental = []
        if "lazer" in gaps:
            score_ambiental += 30
            justificativa_ambiental.append("Gap crítico de Parques/Praças")
        if "APP" in stats["zoneamentos"] or "ARE" in stats["zoneamentos"]:
            score_ambiental += 15
            justificativa_ambiental.append("Zoneamento compatível (APP/ARE)")
        if stats["total_imoveis"] > 0 and (stats["total_area"] / stats["total_imoveis"]) > 500:
            score_ambiental += 15
            justificativa_ambiental.append("Área média dos imóveis > 500m²")
        if score_ambiental > 0:
            vocacoes.append({"tipo": "ambiental", "label": "🌳 Parque Urbano / Lazer", "score": score_ambiental, "justificativa": ", ".join(justificativa_ambiental)})

        # Outras vocações (simplificado por falta de mais regras)
        score_infra = 0
        justificativa_infra = []
        if "ACI" in stats["zoneamentos"]:
            score_infra += 15
            justificativa_infra.append("Zoneamento Industrial/Comercial (ACI)")
        if stats["total_imoveis"] > 0 and (stats["total_area"] / stats["total_imoveis"]) > 1000: # Maior area para infra
            score_infra += 15
            justificativa_infra.append("Grandes áreas disponíveis")
        if stats["sem_uso_count"] > 0:
            score_infra += 20
            justificativa_infra.append("Imóveis sem uso disponíveis")
        if score_infra > 0:
            vocacoes.append({"tipo": "infraestrutura", "label": "🏗️ Infraestrutura / Logística", "score": score_infra, "justificativa": ", ".join(justificativa_infra)})


        vocacao_data["bairros"][bairro_name] = {
            "populacao": populacao,
            "equipamentos": equipamentos_osm,
            "gaps": gaps,
            "sem_uso_count": stats["sem_uso_count"],
            "area_sem_uso_m2": stats["area_sem_uso_m2"],
            "vocacoes": sorted(vocacoes, key=lambda x: x["score"], reverse=True)
        }

    output_path = "/root/projects/floripa-patrimonio/data/vocacao.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(vocacao_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Arquivo de vocação gerado em {output_path}")

if __name__ == "__main__":
    calculate_vocation_data()
