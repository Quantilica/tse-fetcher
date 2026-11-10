---
dataset:
  id: "eleitorado"
  fonte: "tse"
  titulo: "Perfil do eleitorado (perfil_eleitorado)"
  resumo: "Perfil agregado do eleitorado (por exemplo por município, sexo, faixa etária e escolaridade), segundo o título do conjunto no portal."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/eleitorado-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "não informado pela fonte para este arquivo"
  cobertura: {inicio: "2024", fim: 2024}
  unidade: "não conferido"
  granularidade: {espacial: "não conferido", temporal: "não conferido"}
  formato_bruto: "ZIP do CDN do TSE; layout não conferido"
  lake: {estado: so-bruto, particoes: ["ano", "uf"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Perfil do eleitorado (perfil_eleitorado)

## Resumo

Perfil agregado do eleitorado (por exemplo por município, sexo, faixa etária e escolaridade), segundo o título do conjunto no portal. O fetcher não baixa este conjunto e o lake não o tem.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/eleitorado` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/eleitorado-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | não informado pela fonte para este arquivo |
| Cobertura | 2024 a 2024 |
| Unidade (uma linha) | não conferido |
| Granularidade | espacial: não conferido; temporal: não conferido |
| Formato bruto | ZIP do CDN do TSE; layout não conferido |
| Estado no lake | so-bruto |
| Partições | `ano`, `uf` |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- **O fetcher não baixa este conjunto** e o bruto conferido em 2026-11-10 não tem arquivo dele. A fonte publica `perfil_eleitorado_2024.zip` em `https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado`.
- **Layout não conferido:** o ZIP não foi aberto neste levantamento (o download de 228 MB ficou truncado).

## Conteúdo

- Nada conferido: unidade, cobertura e layout ficam como "não conferido". Cobertura no lake: nenhuma.

## Variáveis

Não conferido. O layout não foi aberto e, como o dataset não está no lake, não há esquema de referência. Para o layout, use o `leiame.pdf` do ZIP da fonte.

## No lake

- Estado: `so-bruto`. Não há dataset `tse/eleitorado` no lake nem esquema de referência.
- O conversor reconhece o id `eleitorado` e o nome de arquivo `(o download de 228 MB ficou truncado)`, mas nada foi convertido.

## Cuidados de uso

- Não conferido. O campo `dados_pessoais` do cabeçalho está como `nenhum` por falta de informação contrária, não porque o layout tenha sido inspecionado.

## Exemplos

Ainda não há dados no lake para este dataset; não há exemplo executável.

## Referências

- Conjunto no portal: https://dadosabertos.tse.jus.br/dataset/eleitorado-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado
