# RESULTADO — Vocação Patrimonial + Inteligência Baoba

## 1. Confirmação de Push

✅ **Push realizado com sucesso.**  
Branch: `main`  
Commit: `feat: vocação patrimonial + inteligência Baoba`  
Arquivos modificados:
- `data/vocacao.json` — 35 bairros com análise de vocação
- `data/osm_equipamentos.json` — equipamentos públicos via OSM (já existia, mantido)
- `index.html` — dashboard atualizado com aba 🎯 Vocação completa
- `scripts/gerar_vocacao.py` — motor de vocação (Python)

---

## 2. Top 10 Bairros por Score de Oportunidade

| # | Bairro | Vocação Principal | Score | Área Sem Uso | Pop. |
|---|--------|-------------------|-------|--------------|------|
| 1 | **Coqueiros** | 🏥 Unidade de Saúde (UBS) | 100 | 16.619 m² | 15.000 |
| 2 | **Estreito** | 🎓 Escola / Creche | 85 | 4.809 m² | 28.000 |
| 3 | **Campinas** | 🎓 Escola / Creche | 85 | 2.589 m² | 18.000 |
| 4 | **Campeche** | 🏥 Unidade de Saúde (UBS) | 80 | 19.437 m² | 28.000 |
| 5 | **Saco dos Limões** | 🏥 Unidade de Saúde (UBS) | 80 | 23.437 m² | 11.000 |
| 6 | **Ratones** | 🏥 Unidade de Saúde (UBS) | 80 | 6.568 m² | 3.000 |
| 7 | **Cachoeira do Bom Jesus** | 🏥 Unidade de Saúde (UBS) | 80 | 7.780 m² | 5.000 |
| 8 | **Vargem Grande** | 🏥 Unidade de Saúde (UBS) | 80 | 6.298 m² | 6.000 |
| 9 | **Capoeiras** | 🏥 Unidade de Saúde (UBS) | 70 | — | 22.000 |
| 10 | **Canasvieiras** | 🎓 Escola / Creche | 65 | 3.595 m² | 12.000 |

### Destaques

- **Coqueiros** tem score máximo (100): zero equipamentos registrados na Overpass API num raio de 1.5km, alta densidade demográfica (5.357 hab/km²), 9 imóveis sem uso disponíveis com área média > 500m². Melhor oportunidade para UBS no patrimônio municipal.
- **Campeche e Saco dos Limões** têm as maiores áreas sem uso (>19k e >23k m² respectivamente) — alta viabilidade para implantação de equipamentos de saúde.
- A vocação de **saúde** domina 7 dos top 10 bairros, indicando déficit sistêmico de UBS fora da área central.

---

## 3. Limitações Encontradas nos Dados OSM

### 3.1 Dados OSM (Overpass API)
- **Raio de 1.5km pode gerar sobreposição**: bairros próximos (ex: Centro, Agronômica, Trindade) compartilham equipamentos na mesma consulta, inflacionando contagens. O Centro com 91 UBS é quase certamente resultado de sobreposição com bairros vizinhos.
- **Cobertura irregular no OSM**: bairros periféricos (Ribeirão da Ilha, Tapera, Daniela, Santinho) têm dados muito escassos ou zerados — OSM tem menor contribuição em áreas rurais/insulares de Floripa.
- **Tags inconsistentes**: saúde usa `amenity=clinic,doctors` + `healthcare=*`. Na prática, muitas UBSs em Florianópolis não estão no OSM ou estão tagueadas de forma não padronizada.
- **Parques vs. praças**: alguns parques urbanos estão catalogados como `leisure=garden` ou `leisure=square`, outros como `leisure=park`, gerando subcontagem.
- **Coqueiros com zero equipamentos**: provavelmente erro de mapeamento OSM — bairro densamente habitado. Sugere-se validar com dados da SMS Florianópolis.

### 3.2 Dados de Imóveis (PMF)
- **Area=0 para 852 imóveis**: 52% dos imóveis têm área zerada, prejudicando o critério "área média > 500m²". O cálculo de área média usa apenas imóveis com área > 0.
- **Coordenadas aproximadas**: lat/lng dos imóveis é o centroide do bairro (não o lote real), impossibilitando análise geoespacial precisa por imóvel.
- **Zoneamento "N/A" predominante**: 63% dos imóveis têm zoneamento não informado, reduzindo a pontuação de zoneamento compatível para maioria dos bairros.
- **"Não Identificado" com 585 imóveis (36%)**: maior "bairro" do dataset, excluído do mapa por falta de coordenada específica.

### 3.3 Recomendações Futuras
1. Cruzar dados OSM com Geosampa / IPUF de Florianópolis para equipamentos reais
2. Obter shapefile dos bairros para cálculo preciso de densidade e área
3. Atualizar zoneamento dos imóveis via cruzamento com PD Florianópolis 2023
4. Adicionar dados do IBGE Censo 2022 para população mais precisa
