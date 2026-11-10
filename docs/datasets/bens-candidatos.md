---
dataset:
  id: "bens-candidatos"
  fonte: "tse"
  titulo: "Bens de candidatos (bem_candidato)"
  resumo: "Bens patrimoniais declarados por cada candidatura no registro, um item por linha, com tipo, descrição, valor e data da última atualização."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/candidatos-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos; o LEIAME dos arquivos avisa que CPF, e-mail e outros dados pessoais de candidatos podem vir ocultos (veja os cuidados de uso)."
  periodicidade: "diária segundo o portal de dados abertos (extração com data de geração em cada arquivo)"
  cobertura: {inicio: "2018", fim: 2026}
  unidade: "um bem declarado por uma candidatura"
  granularidade: {espacial: "unidade eleitoral (município, UF ou nacional), com UF", temporal: "eleição (ano)"}
  formato_bruto: "ZIP por ano com um CSV por UF, mais os consolidados BR e BRASIL; CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho"
  lake: {estado: convertido, particoes: ["ano", "uf"], chave: ["ano", "sq_candidato", "nr_ordem_bem_candidato"], colunas: 19}
  unidades_de_medida: {vr_bem_candidato: "R$ (texto com vírgula decimal)"}
  dados_pessoais:
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
    - {coluna: "ds_bem_candidato", categoria: "texto livre sobre o patrimônio da pessoa (pode conter endereços, matrículas e nomes)"}
    - {coluna: "vr_bem_candidato", categoria: "patrimônio declarado"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Bens de candidatos (bem_candidato)

## Resumo

Declaração de bens que acompanha o registro de candidatura (arquivo `bem_candidato`): cada linha é um bem de uma candidatura, ligado ao cadastro de candidatos por `sq_candidato`. Serve para somar o patrimônio declarado por pessoa, cargo ou partido.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/bens-candidatos` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/candidatos-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos; o LEIAME dos arquivos avisa que CPF, e-mail e outros dados pessoais de candidatos podem vir ocultos (veja os cuidados de uso). |
| Periodicidade | diária segundo o portal de dados abertos (extração com data de geração em cada arquivo) |
| Cobertura | 2018 a 2026 |
| Unidade (uma linha) | um bem declarado por uma candidatura |
| Granularidade | espacial: unidade eleitoral (município, UF ou nacional), com UF; temporal: eleição (ano) |
| Formato bruto | ZIP por ano com um CSV por UF, mais os consolidados BR e BRASIL; CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho |
| Estado no lake | convertido |
| Partições | `ano`, `uf` |
| Chave | `ano`, `sq_candidato`, `nr_ordem_bem_candidato` |
| Colunas | 19 |
| Unidades de medida | `vr_bem_candidato`: R$ (texto com vírgula decimal) |
| Dados pessoais | `sq_candidato` (identificador da pessoa candidata); `ds_bem_candidato` (texto livre sobre o patrimônio da pessoa (pode conter endereços, matrículas e nomes)); `vr_bem_candidato` (patrimônio declarado) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- O fetcher baixa `bem_candidato_<ano>.zip` do CDN (`https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/`). No bruto o nome é o da fonte, com manifesto ao lado.
- Dentro do ZIP: `leiame.pdf` (descartado), um CSV por UF (`bem_candidato_<ano>_<UF>.csv`), o consolidado `bem_candidato_<ano>_BRASIL.csv` e, em 2018, 2022 e 2026, o `BR` das candidaturas nacionais.
- Conferido em 2026-11-10 pela listagem do bruto: ZIPs de 2018, 2020, 2022, 2024 e 2026. O fetcher aceita desde 2006.

## Conteúdo

- Unidade de análise: um bem; a chave `ano`, `sq_candidato` e `nr_ordem_bem_candidato` é única nos arquivos por UF conferidos (2.189.264 linhas distintas em 2.189.264).
- Cobertura conferida (arquivo `BRASIL`, linhas): 2018: 93.527; 2020: 1.015.279; 2022: 92.559; 2024: 911.317; 2026: 77.446.
- Cabeçalho de 19 colunas igual em todos os anos conferidos; nenhuma quebra de layout.
- Nulos: nenhum campo nulo nas 4.380.256 linhas conferidas (com a duplicação descrita nos cuidados).

## Variáveis

Descrições do LEIAME oficial do TSE (bem_candidato); onde o texto não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todo |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todo |
| `ano_eleicao` | `ANO_ELEICAO` | texto | Ano de referência da eleição para geração do arquivo. | — | todo |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | . 1: Eleição Suplementar; . 2: Eleição Ordinária; e . 3: Consulta Popular. | todo |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todo |
| `dt_eleicao` | `DT_ELEICAO` | texto | Data da ocorrência da eleição. | — | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição. | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da unidade eleitoral na qual a candidata ou candidato concorre na eleição. A unidade eleitoral representa a unidade da federação ou o município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal, é o nome do município em que (...) | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. | — | todo |
| `nr_ordem_bem_candidato` | `NR_ORDEM_BEM_CANDIDATO` | texto | Número de ordenação do bem patrimonial material da candidata ou candidato de acordo com a sequência de bens declarados pela(o) mesma(o). | — | todo |
| `cd_tipo_bem_candidato` | `CD_TIPO_BEM_CANDIDATO` | texto | Código do tipo do bem patrimonial material declarado pela candidata ou candidato. | — | todo |
| `ds_tipo_bem_candidato` | `DS_TIPO_BEM_CANDIDATO` | texto | Tipo do bem patrimonial material declarado pela candidata ou candidato. | — | todo |
| `ds_bem_candidato` | `DS_BEM_CANDIDATO` | texto | Descrição detalhada do bem material patrimonial da candidata ou candidato. | — | todo |
| `vr_bem_candidato` | `VR_BEM_CANDIDATO` | texto | Valor, em reais, do bem declarado. Texto com vírgula decimal e sem separador de milhar, como `20000,00` | R$ | todo |
| `dt_ult_atual_bem_candidato` | `DT_ULT_ATUAL_BEM_CANDIDATO` | texto | Data da última atualização, no sistema, do bem material patrimonial declarado pela candidata ou candidato. | — | todo |
| `hh_ult_atual_bem_candidato` | `HH_ULT_ATUAL_BEM_CANDIDATO` | texto | Hora da última atualização, no sistema, do bem material patrimonial declarado pela candidata ou candidato. | — | todo |

## No lake

- Dataset `tse/bens-candidatos`, particionado por `ano` e `uf`, um Parquet por CSV de origem.
- `ano` e `uf` vêm do nome do membro; o `BR` vai para `uf=br` e o `BRASIL` só é lido se o ZIP não tiver os arquivos por UF (então vai para `uf=__HIVE_DEFAULT_PARTITION__`).
- Todas as colunas são texto (inclusive `vr_bem_candidato`, com vírgula decimal). Leitura em Latin-1; os campos de descrição com quebra de linha entre aspas são lidos corretamente: o `bem_candidato_2024_BRASIL.csv` tem 936.515 linhas físicas e 911.317 registros, e o lake tem 911.317.
- O esquema de referência (`bens-candidatos.schema.json`) tem 19 colunas.

## Cuidados de uso

- **Dupla contagem (corrigida; lake gerado até a versão 0.3.3 ainda tem).** O ZIP traz um CSV por UF, o `BR` (registros de âmbito nacional, quando existe) e o `BRASIL` (consolidado que repete as UFs e o `BR`). O conversor atual não lê o `BRASIL` quando o ZIP tem os arquivos por UF: lê as UFs (`uf=<sigla>`) e o `BR` (`uf=br`, com `sg_uf` = `BR`); se o ZIP só tiver o `BRASIL`, ele é lido e vai para `uf=__HIVE_DEFAULT_PARTITION__`. Assim somar o lake inteiro conta cada linha uma vez. Um lake gerado antes da correção tem os Parquets do `BRASIL` em `uf=__HIVE_DEFAULT_PARTITION__` e as linhas em dobro: apague `tse/bens-candidatos/` e reconverta (veja o `CHANGELOG.md`). Evidência (conferida em 2026-11-10 com o conversor atual): em 2018 o `BRASIL` tem 93.527 linhas, as UFs somam 93.212 e o `BR` 315, e o lake passa a ter 93.527; em 2020 e 2024 o `BRASIL` iguala a soma das UFs.
- **Valor em texto.** `vr_bem_candidato` é texto com vírgula (`20000,00`); troque a vírgula por ponto antes de converter. Todas as linhas de 2022 seguem o padrão `dígitos,dd`.
- **Soma por pessoa.** Um bem pode ser declarado em mais de uma eleição pela mesma pessoa; some por `sq_candidato` dentro de um `ano`, nunca entre anos. O `sq_candidato` muda a cada eleição.
- **Descrição livre.** `ds_bem_candidato` é texto digitado pela pessoa candidata e traz, por exemplo, percentuais de participação ("1/3 do imóvel") e aplicações financeiras; o valor não é padronizado.
- **Marcadores da fonte ficam como texto, não viram nulo.

## Exemplos

Patrimônio declarado mediano das candidaturas ordinárias de 2022 (soma dos bens por candidatura):

```python
import polars as pl

bens = pl.scan_parquet(
    "lake/tse/bens-candidatos/ano=2022/*/*.parquet", hive_partitioning=True
)
patrimonio = (
    bens.filter(pl.col("cd_tipo_eleicao") == "2")
    .with_columns(valor=pl.col("vr_bem_candidato").str.replace(",", ".").cast(pl.Float64))
    .group_by("sq_candidato")
    .agg(pl.col("valor").sum().alias("patrimonio"))
    .select(pl.col("patrimonio").median())
    .collect()
)
```

Na conversão local de 2026-11-10 o resultado foi R$ 275.900,00 para 18.244 candidaturas.

## Referências

- Conjunto de 2024: https://dadosabertos.tse.jus.br/dataset/candidatos-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/
- Layout: `leiame.pdf` dentro de cada ZIP
