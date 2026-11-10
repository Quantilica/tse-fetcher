---
dataset:
  id: "motivo-cassacao"
  fonte: "tse"
  titulo: "Motivo da cassação (motivo_cassacao)"
  resumo: "Motivos de indeferimento do registro, cassação ou não diplomação de candidaturas, com o número do processo."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/candidatos-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "diária segundo o portal de dados abertos (conjunto de candidatos)"
  cobertura: {inicio: "2024", fim: 2024}
  unidade: "um motivo ligado a uma candidatura"
  granularidade: {espacial: "unidade eleitoral (município ou UF), com UF", temporal: "eleição (ano)"}
  formato_bruto: "ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas"
  lake: {estado: so-bruto, particoes: ["ano", "uf"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
    - {coluna: "nr_processo", categoria: "número de processo judicial"}
    - {coluna: "ds_motivo", categoria: "texto livre sobre o motivo, que pode citar a pessoa"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Motivo da cassação (motivo_cassacao)

## Resumo

Motivos de indeferimento do registro, cassação ou não diplomação de candidaturas, com o número do processo. O fetcher não baixa este conjunto e o lake não o tem: o conversor reconhece os arquivos pelo nome, mas nenhum foi convertido.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/motivo-cassacao` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/candidatos-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | diária segundo o portal de dados abertos (conjunto de candidatos) |
| Cobertura | 2024 a 2024 |
| Unidade (uma linha) | um motivo ligado a uma candidatura |
| Granularidade | espacial: unidade eleitoral (município ou UF), com UF; temporal: eleição (ano) |
| Formato bruto | ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas |
| Estado no lake | so-bruto |
| Partições | `ano`, `uf` |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | `sq_candidato` (identificador da pessoa candidata); `nr_processo` (número de processo judicial); `ds_motivo` (texto livre sobre o motivo, que pode citar a pessoa) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- **O fetcher não baixa este conjunto.** O catálogo do fetcher (`candidatos`, `bens`, `votacao`, `prestacao_contas`) não o inclui, e o bruto conferido em 2026-11-10 não tem nenhum arquivo dele. O conversor `LakeConverter` aceita o id `motivo-cassacao` e reconhece arquivos pelo prefixo do nome, se alguém os colocar no diretório de entrada.
- A fonte publica `motivo_cassacao_<ano>.zip` em `https://cdn.tse.jus.br/estatistica/sead/odsele/motivo_cassacao/` (um ZIP por ano). Para este documento foi baixado, diretamente do CDN e só para conferência, o ZIP de 2024 (cabeçalho e LEIAME).

## Conteúdo

- Unidade de análise: um motivo ligado a uma candidatura.
- Cobertura: nada no lake. O cabeçalho abaixo foi conferido no ZIP de 2024 do CDN em 2026-11-10; layouts de outros anos não foram conferidos.

## Variáveis

Colunas do CSV de 2024 e descrições do LEIAME oficial do TSE; onde o texto não define a variável, a célula diz "não informado pela fonte". Como o dataset não está no lake, esta tabela não é verificada contra um esquema de referência e a coluna "Tipo" indica o tipo que o conversor usaria (texto).

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todo |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todo |
| `ano_eleicao` | `ANO_ELEICAO` | texto | Ano de referência da eleição para geração do arquivo. | — | todo |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | . 1: Eleição Suplementar; . 2: Eleição Ordinária; e . 3: Consulta Popular. | todo |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição. | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da unidade eleitoral na qual a candidata ou candidato concorre na eleição. A unidade eleitoral representa a unidade da federação ou o município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal, é o nome do município em que (...) | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. | — | todo |
| `nr_processo` | `NR_PROCESSO` | texto | não informado pela fonte | — | todo |
| `ds_tp_motivo` | `DS_TP_MOTIVO` | texto | Descrição do tipo do motivo que indica se tratar de julgamento do registro de candidatura, cassação ou desconstituição de diploma. | — | todo |
| `ds_motivo` | `DS_MOTIVO` | texto | Descrição do motivo que ocasionou o indeferimento do registro de candidatura, a cassação ou a desconstituição de diploma. | — | todo |

## No lake

- Estado: `so-bruto`. Não há dataset `tse/motivo-cassacao` no lake e, portanto, não há esquema de referência.
- Se o conjunto for baixado e convertido, o conversor o gravaria particionado por `ano` e `uf` (partição `uf` a partir do nome do membro, `__HIVE_DEFAULT_PARTITION__` para `BR`/`BRASIL`) com todas as colunas em texto, como nos demais datasets.

## Cuidados de uso

- Quando for convertido, o ZIP traria também `BRASIL` (e `BR`) junto com as UFs, e o conversor atual os leria todos: a dupla contagem descrita nos outros datasets se repetiria.
- Dado pessoal: o número do processo e o texto do motivo ligam um fato judicial a uma pessoa pelo `sq_candidato`.
- Não conferido: linhas, nulos e chave.

## Exemplos

Ainda não há dados no lake para este dataset. Depois de baixar e converter o conjunto, a leitura segue o padrão dos outros datasets (cada ano em `lake/tse/motivo-cassacao/ano=<ano>/`), por exemplo:

```python
import polars as pl

df = pl.scan_parquet("lake/tse/motivo-cassacao/ano=2024/uf=__HIVE_DEFAULT_PARTITION__/*_brasil.parquet")
```

O caminho acima é só ilustrativo e não foi executado: o dataset não existe no lake.

## Referências

- Conjunto no portal: https://dadosabertos.tse.jus.br/dataset/candidatos-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/motivo_cassacao/
- Layout: `leiame.pdf` dentro do ZIP
