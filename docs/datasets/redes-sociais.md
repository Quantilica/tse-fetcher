---
dataset:
  id: "redes-sociais"
  fonte: "tse"
  titulo: "Redes sociais de candidatos (rede_social_candidato)"
  resumo: "Endereços das redes sociais informadas por cada candidatura no registro."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/candidatos-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "diária segundo o portal de dados abertos (conjunto de candidatos)"
  cobertura: {inicio: "2024", fim: 2024}
  unidade: "uma rede social informada por uma candidatura"
  granularidade: {espacial: "UF da candidatura", temporal: "eleição (ano)"}
  formato_bruto: "ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas"
  lake: {estado: so-bruto, particoes: ["ano", "uf"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
    - {coluna: "ds_url", categoria: "endereço de perfil de rede social"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Redes sociais de candidatos (rede_social_candidato)

## Resumo

Endereços das redes sociais informadas por cada candidatura no registro. O fetcher não baixa este conjunto e o lake não o tem: o conversor reconhece os arquivos pelo nome, mas nenhum foi convertido.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/redes-sociais` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/candidatos-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | diária segundo o portal de dados abertos (conjunto de candidatos) |
| Cobertura | 2024 a 2024 |
| Unidade (uma linha) | uma rede social informada por uma candidatura |
| Granularidade | espacial: UF da candidatura; temporal: eleição (ano) |
| Formato bruto | ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas |
| Estado no lake | so-bruto |
| Partições | `ano`, `uf` |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | `sq_candidato` (identificador da pessoa candidata); `ds_url` (endereço de perfil de rede social) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- **O fetcher não baixa este conjunto.** O catálogo do fetcher (`candidatos`, `bens`, `votacao`, `prestacao_contas`) não o inclui, e o bruto conferido em 2026-11-10 não tem nenhum arquivo dele. O conversor `LakeConverter` aceita o id `redes-sociais` e reconhece arquivos pelo prefixo do nome, se alguém os colocar no diretório de entrada.
- A fonte publica `rede_social_candidato_<ano>.zip` em `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/` (um ZIP por ano). Para este documento foi baixado, diretamente do CDN e só para conferência, o ZIP de 2024 (cabeçalho e LEIAME).
- **O nome do arquivo não casa com o conversor.** A fonte publica o ZIP como `rede_social_candidato_<ano>.zip` (`consulta_cand/rede_social_candidato_2024.zip`), mas o conversor procura o prefixo `redes_sociais_candidatos`; mesmo se o arquivo fosse baixado, o conversor não o reconheceria pelo nome (verificado em `resolve_dataset`).

## Conteúdo

- Unidade de análise: uma rede social informada por uma candidatura.
- Cobertura: nada no lake. O cabeçalho abaixo foi conferido no ZIP de 2024 do CDN em 2026-11-10; layouts de outros anos não foram conferidos.

## Variáveis

Colunas do CSV de 2024 e descrições do LEIAME oficial do TSE; onde o texto não define a variável, a célula diz "não informado pela fonte". Como o dataset não está no lake, esta tabela não é verificada contra um esquema de referência e a coluna "Tipo" indica o tipo que o conversor usaria (texto).

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todo |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todo |
| `aa_eleicao` | `AA_ELEICAO` | texto | Ano de referência da eleição para geração do arquivo. | — | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição. | — | todo |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | . 1: Eleição Suplementar; . 2: Eleição Ordinária; e . 3: Consulta Popular. | todo |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. | — | todo |
| `nr_ordem_rede_social` | `NR_ORDEM_REDE_SOCIAL` | texto | Número de ordenação da rede social da candidata ou candidato de acordo com a sequência de redes sociais declaradas pela(o) mesma(o). | — | todo |
| `ds_url` | `DS_URL` | texto | Link da rede social informada pela candidata ou candidato. | — | todo |

## No lake

- Estado: `so-bruto`. Não há dataset `tse/redes-sociais` no lake e, portanto, não há esquema de referência.
- Se o conjunto for baixado e convertido, o conversor o gravaria particionado por `ano` e `uf` (partição `uf` a partir do nome do membro, `__HIVE_DEFAULT_PARTITION__` para `BR`/`BRASIL`) com todas as colunas em texto, como nos demais datasets.

## Cuidados de uso

- Quando for convertido, o ZIP traria também `BRASIL` (e `BR`) junto com as UFs, e o conversor atual os leria todos: a dupla contagem descrita nos outros datasets se repetiria.
- Dado pessoal: `ds_url` é o endereço do perfil pessoal da pessoa candidata.
- O cabeçalho do CSV traz `AA_ELEICAO` onde o LEIAME diz `ANO_ELEICAO`.
- Não conferido: linhas, nulos e chave.

## Exemplos

Ainda não há dados no lake para este dataset. Depois de baixar e converter o conjunto, a leitura segue o padrão dos outros datasets (cada ano em `lake/tse/redes-sociais/ano=<ano>/`), por exemplo:

```python
import polars as pl

df = pl.scan_parquet("lake/tse/redes-sociais/ano=2024/uf=__HIVE_DEFAULT_PARTITION__/*_brasil.parquet")
```

O caminho acima é só ilustrativo e não foi executado: o dataset não existe no lake.

## Referências

- Conjunto no portal: https://dadosabertos.tse.jus.br/dataset/candidatos-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/
- Layout: `leiame.pdf` dentro do ZIP
