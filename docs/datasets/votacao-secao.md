---
dataset:
  id: "votacao-secao"
  fonte: "tse"
  titulo: "Votação por seção eleitoral (votacao_secao)"
  resumo: "Votos de cada votável (candidato, partido, branco, nulo) em cada seção eleitoral, com o local de votação."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/resultados-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "diária segundo o portal de dados abertos (conjunto de resultados da eleição)"
  cobertura: {inicio: "2024", fim: 2024}
  unidade: "os votos de um votável em uma seção eleitoral"
  granularidade: {espacial: "seção eleitoral (município, zona e seção), com UF", temporal: "eleição (ano e turno)"}
  formato_bruto: "ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas"
  lake: {estado: so-bruto, particoes: ["ano", "uf"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "nr_votavel", categoria: "número do candidato ou partido votado"}
    - {coluna: "nm_votavel", categoria: "nome da pessoa candidata"}
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
    - {coluna: "nm_local_votacao", categoria: "local de votação (instituição)"}
    - {coluna: "ds_local_votacao_endereco", categoria: "endereço do local de votação"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Votação por seção eleitoral (votacao_secao)

## Resumo

Votos de cada votável (candidato, partido, branco, nulo) em cada seção eleitoral, com o local de votação. O fetcher não baixa este conjunto e o lake não o tem: o conversor reconhece os arquivos pelo nome, mas nenhum foi convertido.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/votacao-secao` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/resultados-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | diária segundo o portal de dados abertos (conjunto de resultados da eleição) |
| Cobertura | 2024 a 2024 |
| Unidade (uma linha) | os votos de um votável em uma seção eleitoral |
| Granularidade | espacial: seção eleitoral (município, zona e seção), com UF; temporal: eleição (ano e turno) |
| Formato bruto | ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas |
| Estado no lake | so-bruto |
| Partições | `ano`, `uf` |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | `nr_votavel` (número do candidato ou partido votado); `nm_votavel` (nome da pessoa candidata); `sq_candidato` (identificador da pessoa candidata); `nm_local_votacao` (local de votação (instituição)); `ds_local_votacao_endereco` (endereço do local de votação) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- **O fetcher não baixa este conjunto.** O catálogo do fetcher (`candidatos`, `bens`, `votacao`, `prestacao_contas`) não o inclui, e o bruto conferido em 2026-11-10 não tem nenhum arquivo dele. O conversor `LakeConverter` aceita o id `votacao-secao` e reconhece arquivos pelo prefixo do nome, se alguém os colocar no diretório de entrada.
- A fonte publica `votacao_secao_<ano>_<UF>.zip (um ZIP por UF e ano)` em `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/` (um ZIP por ano). Para este documento foi baixado, diretamente do CDN e só para conferência, o ZIP de 2024 (cabeçalho e LEIAME).
- Diferente dos outros conjuntos, a votação por seção sai em um ZIP por UF (`votacao_secao_2024_RR.zip`, com um único CSV e o LEIAME); o de Roraima de 2024 tem 31,8 MB descompactados.
- Esse formato (ano e UF no nome do ZIP) é lido pelo `resolve_partitions` do conversor, que extrai o ano e a UF do nome do arquivo.

## Conteúdo

- Unidade de análise: os votos de um votável em uma seção eleitoral.
- Cobertura: nada no lake. O cabeçalho abaixo foi conferido no ZIP de 2024 do CDN em 2026-11-10; layouts de outros anos não foram conferidos.

## Variáveis

Colunas do CSV de 2024 e descrições do LEIAME oficial do TSE; onde o texto não define a variável, a célula diz "não informado pela fonte". Como o dataset não está no lake, esta tabela não é verificada contra um esquema de referência e a coluna "Tipo" indica o tipo que o conversor usaria (texto).

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todo |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todo |
| `ano_eleicao` | `ANO_ELEICAO` | texto | Ano de referência da eleição para geração do arquivo. | — | todo |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | 1 - Eleição Suplementar, 2 - Eleição Ordinária e 3 - Consulta Popular. | todo |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todo |
| `nr_turno` | `NR_TURNO` | texto | Número do turno da eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todo |
| `dt_eleicao` | `DT_ELEICAO` | texto | Data em que ocorreu a eleição. | — | todo |
| `tp_abrangencia` | `TP_ABRANGENCIA` | texto | Abrangência da eleição. | Municipal, Estadual e Federal. Observação: A abrangência territorial da eleição está diretamente relacionada aos cargos eletivos e suas circunscrições eleitorais. As eleições realizadas na (...) | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da Unidade da Federação em que ocorreu a eleição | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da Unidade Eleitoral em que a candidata ou o candidato concorre na eleição. A Unidade Eleitoral representa a Unidade da Federação ou o Município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome de Unidade Eleitoral da candidata ou candidato (em caso de eleição majoritária é o nome da UF que o candidato concorre e em caso de eleição municipal é o nome do município). | — | todo |
| `cd_municipio` | `CD_MUNICIPIO` | texto | Código TSE do município onde ocorreu a eleição | — | todo |
| `nm_municipio` | `NM_MUNICIPIO` | texto | Nome do município onde ocorreu a eleição | — | todo |
| `nr_zona` | `NR_ZONA` | texto | Número da zona onde ocorreu a eleição. | — | todo |
| `nr_secao` | `NR_SECAO` | texto | Número da seção em que ocorreu a eleição. | — | todo |
| `cd_cargo` | `CD_CARGO` | texto | Código do cargo da candidata ou candidato. | — | todo |
| `ds_cargo` | `DS_CARGO` | texto | Descrição do cargo da candidata ou candidato. | — | todo |
| `nr_votavel` | `NR_VOTAVEL` | texto | Número do votável. | - número da candidata ou candidato, quando voto nominal; - número do partido, quando voto em legenda; - número 95, quando voto em branco; - número 96, quando voto nulo; - número 97, quando voto (...) | todo |
| `nm_votavel` | `NM_VOTAVEL` | texto | Nome do votável. | - nome do candidato, quando voto nominal ou voto anulado; - nome do partido, quando voto em legenda; - "Voto em branco", quando voto em branco; - "Voto nulo", quando voto nulo; - "Voto anulado e (...) | todo |
| `qt_votos` | `QT_VOTOS` | texto | Quantidade de votos recebidos pelo votável naquele município, zona e seção. | — | todo |
| `nr_local_votacao` | `NR_LOCAL_VOTACAO` | texto | Número do local de votação da eleitora ou eleitor. | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. Observações: 1) Este sequencial pode ser utilizado como chave para o cruzamento de dados. 2) Não é o número de campanha da candidata ou candidato. | — | todo |
| `nm_local_votacao` | `NM_LOCAL_VOTACAO` | texto | Nome do local de votação da eleitora ou eleitor. | — | todo |
| `ds_local_votacao_endereco` | `DS_LOCAL_VOTACAO_ENDERECO` | texto | Descrição do endereço do local de votação da eleitora ou eleitor. | — | todo |

## No lake

- Estado: `so-bruto`. Não há dataset `tse/votacao-secao` no lake e, portanto, não há esquema de referência.
- Se o conjunto for baixado e convertido, o conversor o gravaria particionado por `ano` e `uf` (partição `uf` a partir do nome do membro, `__HIVE_DEFAULT_PARTITION__` para `BR`/`BRASIL`) com todas as colunas em texto, como nos demais datasets.

## Cuidados de uso

- Quando for convertido, o ZIP traria também `BRASIL` (e `BR`) junto com as UFs, e o conversor atual os leria todos: a dupla contagem descrita nos outros datasets se repetiria.
- Dado pessoal: o local de votação tem nome e endereço de escola ou órgão público, e `nm_votavel` traz nomes de candidatos.
- Volume: é o maior conjunto de resultados (o ZIP nacional de 2024 pesa centenas de MB; o de Roraima sozinho tem 31,8 MB descompactado). Não conferido: linhas, nulos e chave.

## Exemplos

Ainda não há dados no lake para este dataset. Depois de baixar e converter o conjunto, a leitura segue o padrão dos outros datasets (cada ano em `lake/tse/votacao-secao/ano=<ano>/`), por exemplo:

```python
import polars as pl

df = pl.scan_parquet("lake/tse/votacao-secao/ano=2024/uf=__HIVE_DEFAULT_PARTITION__/*_brasil.parquet")
```

O caminho acima é só ilustrativo e não foi executado: o dataset não existe no lake.

## Referências

- Conjunto no portal: https://dadosabertos.tse.jus.br/dataset/resultados-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/
- Layout: `leiame.pdf` dentro do ZIP
