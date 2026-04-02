# Resultado — Inteligência de Mercado Imobiliário

## 1. Confirmação de Push

✅ **Push realizado com sucesso** em `master` (commit `ad1a636`)  
Repo: https://github.com/decomontenegro/floripa-patrimonio  
Arquivos modificados:
- `data/mercado.json` — criado (análise de inteligência de mercado por bairro)
- `index.html` — aba "Mercado" adicionada ao dashboard

---

## 2. Top 10 Bairros por VGV Estimado

| # | Bairro | VGV Estimado | Principal Oportunidade | Potencial | Tendência |
|---|--------|-------------|------------------------|-----------|-----------|
| 1 | **Campeche** | R$ 119,7M | Residencial Premium | 85/100 | ↑ Alta |
| 2 | **Armação** | R$ 81,6M | Residencial Premium (16 imóveis s/ uso) | 80/100 | ↑ Alta |
| 3 | **Lagoa da Conceição** | R$ 72,0M | Residencial Ultra-Premium | 88/100 | ↑ Alta |
| 4 | **Coqueiros** | R$ 62,1M | Residencial Premium | 82/100 | ↑ Alta |
| 5 | **Canasvieiras** | R$ 58,5M | Hotel / Pousada | 78/100 | ↑ Alta |
| 6 | **Barra da Lagoa** | R$ 48,6M | Residencial Premium | 78/100 | ↑ Alta |
| 7 | **Vargem Grande** | R$ 36,0M | Condomínio Horizontal | 65/100 | ↑ Alta |
| 8 | **Estreito** | R$ 33,0M | Escritórios Corporativos | 62/100 | ↑ Alta |
| 9 | **Saco dos Limões** | R$ 29,4M | Residencial Médio-Alto | 65/100 | → Estável |
| 10 | **Costeira do Pirajubaé** | R$ 19,5M | Logística / Serviços | 60/100 | → Estável |

> **Destaque especial:** Jurerê Internacional tem potencial de 90/100 e R$19.931/m² (maior do Sul do BR), mas apenas 1 imóvel sem uso cadastrado — VGV unitário calculado em base mínima. Qualquer liberação aqui tem retorno extraordinário.

---

## 3. VGV Total do Portfólio Municipal

### **R$ 744 milhões** (excluindo "Não Identificado")

- Se incluídos os 60 imóveis "sem bairro identificado": +R$ 216M potenciais → **R$ 960M total**
- 36 bairros mapeados com análise completa
- **8 bairros** com tendência de alta simultânea ao maior VGV (≥ R$ 30M)
- Score médio de potencial de incorporação: **~65/100**
- **15 bairros** com tendência "alta" de valorização

---

## 4. Fontes de Dados Utilizadas

| Fonte | Dados | Referência |
|-------|-------|-----------|
| **FipeZAP** (via MySide.com.br) | Preço médio Florianópolis: R$13.011/m² (fev/2026), variação +8,69% a.a. | Dados mensais até fev/2026 |
| **DataZAP / ZAP Imóveis** | Jurerê Internacional: R$19.931/m² | 2025 |
| **Agente Imóvel** | Jurerê Internacional: R$14.515/m² | Último mês disponível |
| **Andrea Cardoso Imóveis** | Coqueiros: R$11.483/m² (+21,1% em 12 meses, mai/2025) | Nov/2025 |
| **CRECI-SC** | Florianópolis: 3° aluguel mais caro do Brasil; +10,39% em 2024 | 2025 |
| **ZAP Imóveis (narrativo)** | Ingleses/Campeche: R$6.000-8.000/m²; Jurerê/Lagoa: >R$12.000/m² | 2025 |
| **Estimativas calibradas** | Bairros sem dados precisos: estimados por posicionamento geográfico, perfil socioeconômico e distância de referências | Metodologia interna |
| **data/bairros_stats.json** | Área sem uso por bairro (base para cálculo de VGV) | PMF/2024 |

### Metodologia de VGV
```
VGV = área_disponivel_m2 × 0.6 (aproveitamento) × valor_m2_residencial
- área_disponivel_m2: derivado de sem_uso count × estimativa média por imóvel
- Mínimo de 1.000m² para bairros com 0 imóveis sem uso
- VGV usa a oportunidade de maior potencial identificada por bairro
```

---

## 5. O que foi construído

### `data/mercado.json`
- 36 bairros analisados (100% de cobertura do portfólio)
- Por bairro: valor m² residencial + comercial, potencial de incorporação (0-100), potencial comercial, tendência, perfil de mercado, usos permitidos, 2-3 modelos PPP detalhados, 2-4 oportunidades privadas com VGV estimado, risco e observações
- VGV calculado para todos os bairros

### `index.html` — Aba "Mercado"
- ✅ Botão de tab com ícone `building-2` (Lucide)
- ✅ Mapa: círculos coloridos por gradiente de potencial_incorporacao (cinza → âmbar → verde → dourado)
- ✅ Legenda de mercado (Baixo/Médio/Alto/Muito Alto)
- ✅ Painel VGV Total estimado + stats
- ✅ Ranking de bairros por potencial de incorporação (top 15)
- ✅ Top 10 PPP por VGV com modelo principal e score
- ✅ Detalhe ao clicar: valor m², oportunidades privadas com ícones Lucide, modelos PPP com viabilidade e prazo
- ✅ mercado.json carregado via fetch() no init() junto com os demais JSONs
- ✅ Dark theme preservado, senha "baoba" intacta
