# Dashboard — Patrimônio Imobiliário de Florianópolis

## Objetivo
Criar um dashboard interativo de patrimônio público municipal de Florianópolis, inspirado no projeto https://decomontenegro.github.io/brazil-demographic-heatmap/

## Referência visual
- Dark theme com mapa central
- Header com tabs de navegação
- Painel lateral direito com filtros e rankings
- Timeline slider na parte inferior
- Cards de stats/métricas
- Cores por categoria/intensidade no mapa

## Dados disponíveis

### 1. bd_pmf.xlsx (1.634 registros)
Campos: fid, mslink, cd_lote, loteamento_desmembramento, processo_adm, caracterizacao, matricula_imobl, oficio, ano_registro, cartorio, finalidade, lei_rec_inc, area_matricula, Propriedade, Responsável, Tipo, Zoneamento

### 2. comcap.pdf (dados COMCAP — extrair como texto)
Campos: fid, cd_lote, endereco_completo, descrição, area_territorial, area_construida, Classificação, Estado_Conservação, Centro_Custo, Responsável, Conta_Contabil, Taxa_depreciacao, valor_aquisição, valor_residual, origem, matricula, oficio

### 3. sma.pdf (dados SMA — extrair como texto)
Campos: fid, cpf_cnpj, cd_lote, endereco_completo, endereco_complemento, area_territorial, area_construida_autonoma, utilizacao, ocupacao, caracterizacao, matricula_imobl, oficio, loteamento_desmembramento, finalidade_em_matricula, Origem

## O que construir

### Stack
- HTML + CSS + Vanilla JS (zero frameworks, como o projeto de referência)
- Leaflet.js para o mapa
- Chart.js para gráficos
- Dados embutidos no JS como JSON (sem backend)

### Funcionalidades obrigatórias
1. **Mapa de Florianópolis** com pontos plotados por bairro/região
   - Usar coordenadas aproximadas por bairro (cd_lote começa com código de região de Floripa)
   - Clustering de pontos quando zoom out
   - Tooltip ao hover com endereço + tipo + área

2. **Filtros** (painel direito):
   - Tipo de imóvel (Terreno / Edificação)
   - Classificação / Uso (Área Verde, ACI, Serv. Público, COMCAP, etc.)
   - Estado de Conservação (Bom / Regular / Ruim)
   - Responsável/Secretaria (SMS, SMA, COMCAP, etc.)
   - Área mínima (slider)

3. **Stats cards** (topo ou lateral):
   - Total de imóveis
   - Área total (m²)
   - Imóveis sem uso
   - Valor patrimonial total

4. **Rankings** (como o projeto de referência):
   - Top bairros por qtd de imóveis
   - Top bairros por área total
   - Imóveis de maior área

5. **Tabs de visualização** (como o heatmap):
   - Quantidade de imóveis
   - Área territorial
   - Valor de aquisição

### Dados de exemplo para testar
Para plotar no mapa, usar coordenadas por código de bairro do cd_lote.
Os 4 primeiros dígitos do cd_lote correspondem a setores do IBGE de Florianópolis.
Usar geocoding offline — mapeamento manual de bairros:
- Canasvieiras: -27.4744, -48.4672
- Daniela: -27.4589, -48.4878
- Jurerê Internacional: -27.4628, -48.5015
- Ponta das Canas: -27.4507, -48.4772
- Praia Brava: -27.4450, -48.4650
- Capoeiras: -27.5894, -48.5839
- Estreito: -27.5753, -48.5811
- Saco dos Limões: -27.6197, -48.5197
- Centro: -27.5969, -48.5495
- Vargem Grande: -27.4717, -48.4278

### Mapeamento cd_lote → bairro
- Começa com 233: Canasvieiras/Daniela
- Começa com 172/173/174/175: Ponta das Canas/Praia Brava
- Começa com 245/246: Jurerê Internacional/Daniela
- Começa com 247: Vargem Grande/Ingleses
- Começa com 513/514: Capoeiras/Abraão
- Começa com 515: Estreito
- Começa com 448/458: Jardim Atlântico
- Começa com 527: Saco dos Limões

## Estrutura de arquivos
```
floripa-patrimonio/
├── index.html
├── style.css
├── data/
│   └── imoveis.json   (dados combinados das 3 fontes)
├── js/
│   ├── app.js
│   ├── map.js
│   └── charts.js
```

## Processo de desenvolvimento
1. Extrair e combinar os dados das 3 fontes em imoveis.json
2. Fazer parsing do bd_pmf.xlsx com Python
3. Usar os dados do PDF que já estão no briefing acima
4. Criar index.html com layout dark inspirado no heatmap
5. Implementar mapa Leaflet com clustering
6. Implementar filtros e rankings

## Quando terminar
Rodar: openclaw system event --text "Done: Dashboard Floripa Patrimônio construído em /root/projects/floripa-patrimonio/" --mode now
