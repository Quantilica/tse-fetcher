---
dataset:
  id: "votacao-munzona"
  fonte: "tse"
  titulo: "Votação nominal por município e zona (votacao_candidato_munzona)"
  resumo: "Votos nominais recebidos por cada candidatura em cada município e zona eleitoral, por turno e destinação do voto (válido, anulado, anulado sub judice)."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/resultados-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "diária segundo o portal de dados abertos (extração com data de geração em cada arquivo)"
  cobertura: {inicio: "2018", fim: 2026}
  unidade: "votos de uma candidatura em um município e zona, em um turno e com uma destinação do voto"
  granularidade: {espacial: "zona eleitoral dentro do município, com UF", temporal: "eleição (ano e turno)"}
  formato_bruto: "ZIP por ano com um CSV por UF, mais o consolidado BRASIL (e BR em 2018); CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho"
  lake: {estado: convertido, particoes: ["ano", "uf"], chave: ["ano", "nr_turno", "sq_candidato", "cd_municipio", "nr_zona"], colunas: 52}
  unidades_de_medida: {qt_votos_nominais: "votos", qt_votos_nominais_validos: "votos"}
  dados_pessoais:
    - {coluna: "nm_candidato", categoria: "nome"}
    - {coluna: "nm_urna_candidato", categoria: "nome"}
    - {coluna: "nm_social_candidato", categoria: "nome social"}
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
  eras:
    - {desde: "2020", mudanca: "as colunas `cd_situacao_diploma` e `ds_situacao_diploma` do arquivo de 2018 passam a se chamar `cd_situacao_dconst_diploma` e `ds_situacao_dconst_diploma`; o resto do cabeçalho (50 colunas) não muda de 2018 a 2024"}
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Votação nominal por município e zona (votacao_candidato_munzona)

## Resumo

Resultado da votação por candidatura e por zona eleitoral de cada município (arquivo `votacao_candidato_munzona`). Reúne os dados da candidatura (cargo, partido, federação, coligação, situação) e a quantidade de votos nominais por destinação. Serve para somar votos por candidato, partido ou município; é a base mais agregada da apuração por candidato (a votação por seção fica no dataset `votacao-secao`).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/votacao-munzona` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/resultados-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | diária segundo o portal de dados abertos (extração com data de geração em cada arquivo) |
| Cobertura | 2018 a 2026 |
| Unidade (uma linha) | votos de uma candidatura em um município e zona, em um turno e com uma destinação do voto |
| Granularidade | espacial: zona eleitoral dentro do município, com UF; temporal: eleição (ano e turno) |
| Formato bruto | ZIP por ano com um CSV por UF, mais o consolidado BRASIL (e BR em 2018); CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho |
| Estado no lake | convertido |
| Partições | `ano`, `uf` |
| Chave | `ano`, `nr_turno`, `sq_candidato`, `cd_municipio`, `nr_zona` |
| Colunas | 52 |
| Unidades de medida | `qt_votos_nominais`: votos; `qt_votos_nominais_validos`: votos |
| Dados pessoais | `nm_candidato` (nome); `nm_urna_candidato` (nome); `nm_social_candidato` (nome social); `sq_candidato` (identificador da pessoa candidata) |
| Eras | 2020: as colunas `cd_situacao_diploma` e `ds_situacao_diploma` do arquivo de 2018 passam a se chamar `cd_situacao_dconst_diploma` e `ds_situacao_dconst_diploma`; o resto do cabeçalho (50 colunas) não muda de 2018 a 2024 |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- O fetcher baixa `votacao_candidato_munzona_<ano>.zip` do CDN (`https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/`). No bruto o nome é o da fonte, com manifesto ao lado.
- Dentro do ZIP: `leiame.pdf` (descartado), um CSV por UF, o consolidado `_BRASIL.csv` e, em 2018, o `_BR.csv` da eleição presidencial.
- Conferido em 2026-11-10 pela listagem do bruto: ZIPs de 2018, 2020, 2022, 2024 e 2026 (o de 2018 descompacta o `BRASIL` em 4,0 GB). Foram abertos para a conferência os de 2018, 2020 e 2024.
- O fetcher aceita desde 1996; o portal publica os anos anteriores.

## Conteúdo

- Unidade de análise: os votos de uma candidatura em um município e zona, por turno e destinação do voto. A chave `ano`, `nr_turno`, `sq_candidato`, `cd_municipio`, `nr_zona` foi única nas amostras (8.402 linhas, as 3.000 primeiras do arquivo do Acre de 2018, 2020 e 2024); não foi conferida no arquivo inteiro.
- Cobertura conferida (linhas do `BRASIL`): 2018: 8.680.108; 2020: 983.614; 2024: 717.288. Os anos 2022 e 2026 estão no bruto e não foram abertos.
- Eras: de 2018 para 2020 mudam os nomes das colunas de situação do diploma (veja a tabela); em 2018 as colunas de julgamento, cassação e diploma já existem no cabeçalho, mas a amostra as traz com `#NE`/`-3`.
- Nulos e chave: só amostra (3 × 3.000 linhas do Acre). Nenhuma coluna nula dentro de cada ano, salvo as colunas de diploma que existem só em uma das eras.

## Variáveis

Descrições do LEIAME oficial do TSE (votacao_candidato_munzona, versão de 2024); onde o texto não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todo |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todo |
| `ano_eleicao` | `ANO_ELEICAO` | texto | Ano de referência da eleição para geração do arquivo. | — | todo |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | . 1: Eleição Suplementar; . 2: Eleição Ordinária; e . 3: Consulta Popular. | todo |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todo |
| `nr_turno` | `NR_TURNO` | texto | Número do turno da eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição | — | todo |
| `dt_eleicao` | `DT_ELEICAO` | texto | Data da ocorrência da eleição. | — | todo |
| `tp_abrangencia` | `TP_ABRANGENCIA` | texto | Abrangência da eleição. | . M: Municipal; . E: Estadual; e . F: Federal. Observação: a abrangência territorial da eleição está diretamente relacionada aos cargos eletivos e suas circunscrições eleitorais. As eleições (...) | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação de ocorrência da eleição. | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da unidade eleitoral na qual a candidata ou candidato concorre na eleição. A unidade eleitoral representa a unidade da federação ou o município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal é o nome do município em que a (...) | — | todo |
| `cd_municipio` | `CD_MUNICIPIO` | texto | Código TSE do município de ocorrência da eleição. | — | todo |
| `nm_municipio` | `NM_MUNICIPIO` | texto | Nome do município de ocorrência da eleição. | — | todo |
| `nr_zona` | `NR_ZONA` | texto | Número da zona eleitoral de ocorrência da eleição. | — | todo |
| `cd_cargo` | `CD_CARGO` | texto | Código do cargo ao qual a candidata ou candidato concorre. | — | todo |
| `ds_cargo` | `DS_CARGO` | texto | Descrição do cargo ao qual a candidata ou candidato concorre. | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. | — | todo |
| `nr_candidato` | `NR_CANDIDATO` | texto | Número da candidata ou candidato na urna. | — | todo |
| `nm_candidato` | `NM_CANDIDATO` | texto | Nome completo da candidata ou candidato. | — | todo |
| `nm_urna_candidato` | `NM_URNA_CANDIDATO` | texto | Nome da candidata ou candidato que aparece na urna. | — | todo |
| `nm_social_candidato` | `NM_SOCIAL_CANDIDATO` | texto | Nome social da candidata ou candidato. | — | todo |
| `cd_situacao_candidatura` | `CD_SITUACAO_CANDIDATURA` | texto | Código da situação do registro de candidatura da candidata ou candidato. Aplicável somente para os registros das eleições até 2022. | — | todo |
| `ds_situacao_candidatura` | `DS_SITUACAO_CANDIDATURA` | texto | Descrição da situação do registro de candidatura da candidata ou candidato. Aplicável somente para os registros das eleições até 2022. | — | todo |
| `cd_detalhe_situacao_cand` | `CD_DETALHE_SITUACAO_CAND` | texto | Código do detalhe da situação do registro da candidatura da candidata ou candidato. Aplicável somente para os registros das eleições até 2022. | — | todo |
| `ds_detalhe_situacao_cand` | `DS_DETALHE_SITUACAO_CAND` | texto | Descrição do detalhe da situação do registro de candidatura da candidata ou candidato. Aplicável somente para os registros das eleições até 2022. | — | todo |
| `cd_situacao_julgamento` | `CD_SITUACAO_JULGAMENTO` | texto | Código da situação da candidata ou candidato com relação ao julgamento do registro de candidatura. Aplicável somente para os registros a partir das eleições de 2024. | — | todo |
| `ds_situacao_julgamento` | `DS_SITUACAO_JULGAMENTO` | texto | Descrição da situação da candidata ou candidato com relação ao julgamento do registro de candidatura. Aplicável somente para os registros a partir das eleições de 2024. | — | todo |
| `cd_situacao_cassacao` | `CD_SITUACAO_CASSACAO` | texto | Código da situação da candidata ou candidato com relação à cassação do mandato. Aplicável somente para os registros a partir das eleições de 2024. | — | todo |
| `ds_situacao_cassacao` | `DS_SITUACAO_CASSACAO` | texto | Descrição da situação da candidata ou candidato com relação à cassação do mandato. Aplicável somente para os registros a partir das eleições de 2024. | — | todo |
| `cd_situacao_diploma` | `CD_SITUACAO_DIPLOMA` | texto | Código da situação com relação ao diploma. Coluna do arquivo de 2018, renomeada a partir de 2020; o LEIAME não a descreve (não informado pela fonte) | — | 2018 |
| `ds_situacao_diploma` | `DS_SITUACAO_DIPLOMA` | texto | Descrição da situação com relação ao diploma. Coluna do arquivo de 2018, renomeada a partir de 2020; o LEIAME não a descreve (não informado pela fonte) | — | 2018 |
| `cd_situacao_dconst_diploma` | `CD_SITUACAO_DCONST_DIPLOMA` | texto | Código da situação da candidata ou candidato com relação ao processo de desconstituição do diploma. | — | 2020 em diante |
| `ds_situacao_dconst_diploma` | `DS_SITUACAO_DCONST_DIPLOMA` | texto | Descrição da situação da candidata ou candidato com relação ao processo de desconstituição do diploma. Aplicável somente para os registros a partir das eleições de 2024. | — | 2020 em diante |
| `tp_agremiacao` | `TP_AGREMIACAO` | texto | Forma como a candidata ou candidato concorre nas eleições. | . Coligação: quando a candidata ou candidato concorre por coligação; . Federação: quando a candidata ou candidato concorre por uma federação; e . Partido Isolado: quando a candidata ou candidato (...) | todo |
| `nr_partido` | `NR_PARTIDO` | texto | Número do partido da candidata ou candidato. | — | todo |
| `sg_partido` | `SG_PARTIDO` | texto | Sigla do partido da candidata ou candidato. | — | todo |
| `nm_partido` | `NM_PARTIDO` | texto | Nome do partido da candidata ou candidato. | — | todo |
| `nr_federacao` | `NR_FEDERACAO` | texto | Número da federação pela qual o partido da candidata ou candidato concorre na eleição. | — | todo |
| `nm_federacao` | `NM_FEDERACAO` | texto | Nome da federação pela qual o partido da candidata ou candidato concorre na eleição. | — | todo |
| `sg_federacao` | `SG_FEDERACAO` | texto | Sigla da federação pela qual o partido da candidata ou candidato concorre na eleição. | — | todo |
| `ds_composicao_federacao` | `DS_COMPOSICAO_FEDERACAO` | texto | Composição da federação pela qual o partido da candidata ou candidato concorre na eleição. A informação da federação é composta pela concatenação das siglas dos partidos federados intercaladas com o símbolo "/". | — | todo |
| `sq_coligacao` | `SQ_COLIGACAO` | texto | Sequencial da coligação pela qual o partido da candidata ou candidato concorre na eleição. | — | todo |
| `nm_coligacao` | `NM_COLIGACAO` | texto | Nome da coligação pela qual o partido da candidata ou candidato concorre na eleição. | — | todo |
| `ds_composicao_coligacao` | `DS_COMPOSICAO_COLIGACAO` | texto | Composição da coligação pela qual o partido da candidata ou candidato concorre na eleição. A informação da coligação é composta pela concatenação das siglas dos partidos coligados intercaladas com ",". | — | todo |
| `st_voto_em_transito` | `ST_VOTO_EM_TRANSITO` | texto | Informa se o quantitativo de votos se refere a voto em trânsito. | . S: Sim; e . N: Não. | todo |
| `qt_votos_nominais` | `QT_VOTOS_NOMINAIS` | texto | Quantidade de votos nominais totalizados | votos; contagem inteira, em texto | todo |
| `nm_tipo_destinacao_votos` | `NM_TIPO_DESTINACAO_VOTOS` | texto | Nome do tipo da destinação dos votos. | — | todo |
| `qt_votos_nominais_validos` | `QT_VOTOS_NOMINAIS_VALIDOS` | texto | Quantidade de votos nominais válidos totalizados. Nas amostras é igual a `qt_votos_nominais` quando `nm_tipo_destinacao_votos` é `Válido` e `0` quando é `Anulado` ou `Anulado sub judice` | votos | todo |
| `cd_sit_tot_turno` | `CD_SIT_TOT_TURNO` | texto | Código da situação de totalização da candidata ou candidato no turno. | — | todo |
| `ds_sit_tot_turno` | `DS_SIT_TOT_TURNO` | texto | Descrição da situação de totalização da candidata ou candidato no turno. | — | todo |

## No lake

- Dataset `tse/votacao-munzona`, particionado por `ano` e `uf`, um Parquet por CSV de origem.
- `ano` e `uf` vêm do nome do membro; `BR` e `BRASIL` vão para `uf=__HIVE_DEFAULT_PARTITION__`.
- Todas as colunas são texto, nomes da fonte em minúsculas; a conversão de um ano inteiro lê um `BRASIL` que pode passar de 4 GB descompactado (2018), então reserve disco temporário.
- O esquema de referência (`votacao-munzona.schema.json`) tem 52 colunas: as 50 do layout atual mais as duas de diploma de 2018. Foi gerado de uma conversão de amostras (3.000 linhas do Acre por ano), não dos arquivos inteiros.

## Cuidados de uso

- **Dupla contagem: o arquivo consolidado `BRASIL` é lido junto com os de cada UF.** O ZIP traz um CSV por UF, o `BR` (nível nacional, quando existe) e o `BRASIL` (todas as linhas). O conversor lê todos: os de UF vão para `uf=<sigla>` e o `BR` e o `BRASIL` caem na mesma partição `uf=__HIVE_DEFAULT_PARTITION__`. Somar o lake inteiro conta cada linha pelo menos duas vezes (em 2018 o `BR` também entra duas vezes). Para contar uma vez, leia só o arquivo `*_brasil.parquet` de cada `ano` (ele já inclui os de UF e o `BR`) ou só as partições de UF mais o `BR`. Evidência (versão 0.3.3, 2026-11-10): em 2018 o `BRASIL` tem 8.680.108 linhas, as UFs somam 8.586.508 e o `BR` 93.600; em 2020 e 2024 o `BRASIL` iguala a soma das UFs (983.614 e 717.288).
- **Colunas de diploma mudam de nome em 2020.** Ao juntar os anos, `cd_situacao_diploma` (2018) e `cd_situacao_dconst_diploma` (2020 em diante) ficam em colunas separadas, e um `union` por posição erra; use `how="diagonal"` ou renomeie.
- **Votos válidos.** Some `qt_votos_nominais_validos` (ou filtre `nm_tipo_destinacao_votos = "Válido"`); `qt_votos_nominais` inclui votos anulados.
- **Marcadores da fonte ficam como texto, não viram nulo.** Segundo o LEIAME, `#NULO` indica campo em branco (`-1` nos numéricos), `#NE` indica informação não registrada naquele ano (`-3`) e `-4` indica dado pessoal não divulgável. O lake os guarda literais; a escrita varia entre arquivos (`#NULO#` em 2018 e `#NULO` em 2024, conferido nas amostras), então teste as duas. Nulo de verdade só aparece em campos vazios.
- **Voto em trânsito.** `st_voto_em_transito` (`S`/`N`) separa os votos em trânsito; a chave acima não o inclui e não houve linha repetida nas amostras.

## Exemplos

Votos nominais válidos por partido para vereador em 2024, lendo só o consolidado `BRASIL`:

```python
import polars as pl

votos = pl.scan_parquet(
    "lake/tse/votacao-munzona/ano=2024/uf=__HIVE_DEFAULT_PARTITION__/*_brasil.parquet"
)
resumo = (
    votos.filter(pl.col("ds_cargo") == "Vereador")
    .group_by("sg_partido")
    .agg(pl.col("qt_votos_nominais_validos").cast(pl.Int64).sum().alias("votos"))
    .sort("votos", descending=True)
    .collect()
)
```

## Referências

- Conjunto de 2024: https://dadosabertos.tse.jus.br/dataset/resultados-2024 (há um por ano, `resultados-<ano>`)
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/
- Layout: `leiame.pdf` dentro de cada ZIP
