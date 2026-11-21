# Fontes de dados — Mundo Novo Global Oils Intelligence

## Objetivo
Monitorar exclusivamente informações externas e públicas sobre óleos vegetais, comércio internacional, energia e câmbio. Não incluir dados internos da empresa.

## Primeira fase — dados públicos
| Fonte | Indicador | Site | Estratégia |
|---|---|---|---|
| Banco Central do Brasil | USD/BRL, séries cambiais | https://dadosabertos.bcb.gov.br/ | API pública; validar série, frequência e atraso |
| USDA | Oferta/demanda, produção, consumo, comércio | https://www.usda.gov/ | Relatórios e bases públicas; investigar API aplicável |
| MPOB | Produção, estoques, exportações de óleo de palma | https://bepi.mpob.gov.my/ | Estatísticas oficiais; verificar formato e termos |
| Comex Stat | Importações brasileiras por NCM, origem e período | https://comexstat.mdic.gov.br/ | Dados públicos; atualização conforme calendário |
| EIA | Petróleo, energia | https://www.eia.gov/opendata/ | API pública; verificar chave e limites |
| GAPKI | Setor indonésio de palma | https://gapki.id/ | Comunicados e relatórios; sem assumir API |

## Segunda fase — notícias e contexto
- Antara News: https://en.antaranews.com/
- The Edge Malaysia: https://theedgemalaysia.com/
- CNN Brasil: https://www.cnnbrasil.com.br/
- CNN International: https://www.cnn.com/
- Reuters: https://www.reuters.com/

Consumir feeds autorizados ou links com título, fonte, URL e data. Não copiar matérias integralmente. Verificar RSS, termos de uso e direitos de republicação.

## Terceira fase — preços de mercado licenciados
- Bursa Malaysia: https://www.bursamalaysia.com/ — futuros de óleo de palma
- CME Group/CBOT: https://www.cmegroup.com/ — futuros de soja e óleo de soja
- Dalian Commodity Exchange: http://www.dce.com.cn/ — contratos chineses

Não apresentar cotações como tempo real sem fonte autorizada e metadados de atraso/licenciamento.

## Requisitos para cada integração
- Identificação da fonte e URL oficial.
- Unidade, moeda, mercado, período de referência, fuso horário e data da última atualização.
- Política de cache, frequência de atualização, falhas e limites de requisição.
- Evidenciar dados atrasados, indisponíveis ou estimados.
- Não inventar preços, variações ou análises quando faltarem dados.

## Ordem técnica sugerida
1. USD/BRL do Banco Central.
2. Dados periódicos USDA, MPOB e Comex Stat.
3. Energia via EIA.
4. Notícias por feeds permitidos.
5. Preços de Bursa/CME mediante acesso legalmente autorizado.
6. Indicadores derivados e alertas explicáveis com fontes.
