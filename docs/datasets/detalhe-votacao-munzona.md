---
dataset:
  id: "detalhe-votacao-munzona"
  fonte: "tse"
  titulo: "Detalhe da apuração por município e zona (detalhe_votacao_munzona)"
  resumo: "Totais da apuração por município e zona: aptos, comparecimento, abstenções, votos válidos, brancos, nulos e anulados, por cargo e turno."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/resultados-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "diária segundo o portal de dados abertos (conjunto de resultados da eleição)"
  cobertura: {inicio: "2024", fim: 2024}
  unidade: "os totais da apuração de um cargo em um município e zona, em um turno"
  granularidade: {espacial: "zona eleitoral dentro do município, com UF", temporal: "eleição (ano e turno)"}
  formato_bruto: "ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas"
  lake: {estado: so-bruto, particoes: ["ano", "uf"], chave: [], colunas: null}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Detalhe da apuração por município e zona (detalhe_votacao_munzona)

## Resumo

Totais da apuração por município e zona: aptos, comparecimento, abstenções, votos válidos, brancos, nulos e anulados, por cargo e turno. O fetcher não baixa este conjunto e o lake não o tem: o conversor reconhece os arquivos pelo nome, mas nenhum foi convertido.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/detalhe-votacao-munzona` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/resultados-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | diária segundo o portal de dados abertos (conjunto de resultados da eleição) |
| Cobertura | 2024 a 2024 |
| Unidade (uma linha) | os totais da apuração de um cargo em um município e zona, em um turno |
| Granularidade | espacial: zona eleitoral dentro do município, com UF; temporal: eleição (ano e turno) |
| Formato bruto | ZIP do CDN do TSE; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas |
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

- **O fetcher não baixa este conjunto.** O catálogo do fetcher (`candidatos`, `bens`, `votacao`, `prestacao_contas`) não o inclui, e o bruto conferido em 2026-11-10 não tem nenhum arquivo dele. O conversor `LakeConverter` aceita o id `detalhe-votacao-munzona` e reconhece arquivos pelo prefixo do nome, se alguém os colocar no diretório de entrada.
- A fonte publica `detalhe_votacao_munzona_<ano>.zip` em `https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/` (um ZIP por ano). Para este documento foi baixado, diretamente do CDN e só para conferência, o ZIP de 2024 (cabeçalho e LEIAME).

## Conteúdo

- Unidade de análise: os totais da apuração de um cargo em um município e zona, em um turno.
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
| `nr_turno` | `NR_TURNO` | texto | Número do turno da eleição. | — | todo |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todo |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todo |
| `dt_eleicao` | `DT_ELEICAO` | texto | Data da ocorrência da eleição. | — | todo |
| `tp_abrangencia` | `TP_ABRANGENCIA` | texto | Abrangência do cargo ao qual a candidata ou candidato concorre. | . Municipal; . Estadual; e . Federal. Observação: a abrangência territorial da eleição está diretamente relacionada aos cargos eletivos e suas circunscrições eleitorais. As eleições realizadas na (...) | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação de ocorrência da eleição. | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da unidade eleitoral na qual a candidata ou candidato concorre na eleição. A unidade eleitoral representa a unidade da federação ou o município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal é o nome do município em que a (...) | — | todo |
| `cd_municipio` | `CD_MUNICIPIO` | texto | Código TSE do município de ocorrência da eleição. Em caso de eleição com abrangência federal (cargo de Presidente e Vice-Presidente) a sigla é BR. Em caso de abrangência estadual (cargos de Governador, Vice-Governador, Senador, Deputado Federal, Deputado (...) | — | todo |
| `nm_municipio` | `NM_MUNICIPIO` | texto | Nome do município de ocorrência da eleição. Em caso de eleição com abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF. Em caso de abrangência municipal, é o nome do município. | — | todo |
| `nr_zona` | `NR_ZONA` | texto | Número da zona eleitoral de ocorrência da eleição. | — | todo |
| `cd_cargo` | `CD_CARGO` | texto | Código do cargo ao qual os votos foram totalizados. | — | todo |
| `ds_cargo` | `DS_CARGO` | texto | Descrição do cargo ao qual os votos foram totalizados. | — | todo |
| `qt_aptos` | `QT_APTOS` | texto | Quantidade de eleitoras e eleitores aptos a votar. | — | todo |
| `qt_secoes_principais` | `QT_SECOES_PRINCIPAIS` | texto | Quantidade de seções eleitorais principais. | — | todo |
| `qt_secoes_agregadas` | `QT_SECOES_AGREGADAS` | texto | Quantidade de seções eleitorais que foram agregadas para votação em uma mesma urna. Agregar seções significa unir seções eleitorais em uma única mesa receptora de votos com a finalidade de atender ao Código Eleitoral que estabelece, como regra, o mínimo de 50 (...) | — | todo |
| `qt_secoes_nao_instaladas` | `QT_SECOES_NAO_INSTALADAS` | texto | Quantidade de eleitoras ou eleitores nas seções eleitorais não instaladas. | — | todo |
| `qt_total_secoes` | `QT_TOTAL_SECOES` | texto | Quantidade total de seções eleitorais. É somatório da quantidade de seções eleitorais principais somadas com com a quantidade de seções eleitorais agregadas. | — | todo |
| `qt_comparecimento` | `QT_COMPARECIMENTO` | texto | Quantidade de eleitoras e eleitores que compareceram às eleições. | — | todo |
| `qt_eleitores_secoes_nao_instaladas` | `QT_ELEITORES_SECOES_NAO_INSTALADAS` | texto | Quantidade de eleitoras ou eleitores nas seções eleitorais não instaladas. | — | todo |
| `qt_abstencoes` | `QT_ABSTENCOES` | texto | Quantidade de eleitoras e eleitores aptos que não compareceram às eleições. | — | todo |
| `st_voto_em_transito` | `ST_VOTO_EM_TRANSITO` | texto | Informa se o quantitativo de votos se refere a voto em trânsito. | . S: Sim; e . N: Não. | todo |
| `qt_votos` | `QT_VOTOS` | texto | Quantidade de votos totalizados. | — | todo |
| `qt_votos_concorrentes` | `QT_VOTOS_CONCORRENTES` | texto | Quantidade de votos nominais e em legenda válidos, anulados sub judice e anulados totalizados. | — | todo |
| `qt_total_votos_validos` | `QT_TOTAL_VOTOS_VALIDOS` | texto | Quantidade total de votos nominais e em legenda válidos totalizados. | — | todo |
| `qt_votos_nominais_validos` | `QT_VOTOS_NOMINAIS_VALIDOS` | texto | Quantidade de votos nominais válidos totalizados. | — | todo |
| `qt_total_votos_leg_validos` | `QT_TOTAL_VOTOS_LEG_VALIDOS` | texto | Quantidade total de votos válidos em legenda e convertidos em legenda totalizados. | — | todo |
| `qt_votos_leg_validos` | `QT_VOTOS_LEG_VALIDOS` | texto | Quantidade de votos válidos em legenda totalizados. | — | todo |
| `qt_votos_nom_convr_leg_validos` | `QT_VOTOS_NOM_CONVR_LEG_VALIDOS` | texto | Quantidade de votos nominais válidos e totalizados que, por decisão judicial, se tornaram votos para a legenda ao qual concorriam. | — | todo |
| `qt_total_votos_anulados` | `QT_TOTAL_VOTOS_ANULADOS` | texto | Quantidade total de votos nominais e em legenda anulados em razão da situação jurídica totalizados. | — | todo |
| `qt_votos_nominais_anulados` | `QT_VOTOS_NOMINAIS_ANULADOS` | texto | Quantidade de votos nominais totalizados mas que tiveram a votação anulada em razão da sua situação jurídica. | — | todo |
| `qt_votos_legenda_anulados` | `QT_VOTOS_LEGENDA_ANULADOS` | texto | Quantidade de votos em legenda totalizados mas que tiveram a votação anulada em razão da sua situação jurídica. | — | todo |
| `qt_total_votos_anul_subjud` | `QT_TOTAL_VOTOS_ANUL_SUBJUD` | texto | Quantidade total de votos nominais e em legenda anulados sub judice (indeferido com recurso) totalizados. | — | todo |
| `qt_votos_nominais_anul_subjud` | `QT_VOTOS_NOMINAIS_ANUL_SUBJUD` | texto | Quantidade de votos nominais anulados em razão da sua situação jurídica mas que há recurso pendente no momento da totalização. | — | todo |
| `qt_votos_legenda_anul_subjud` | `QT_VOTOS_LEGENDA_ANUL_SUBJUD` | texto | Quantidade de votos em legenda anulados em razão da sua situação jurídica mas que há recurso pendente no momento da totalização. | — | todo |
| `qt_votos_brancos` | `QT_VOTOS_BRANCOS` | texto | Quantidade de votos brancos totalizados referente ao cargo. | — | todo |
| `qt_total_votos_nulos` | `QT_TOTAL_VOTOS_NULOS` | texto | Quantidade total de votos dados à candidata ou candidato excluído do pleito (que não consta na urna eletrônica) totalizados. É também a quantidade total de votos dados à candidatura ou partido inexistentes na totalização, podendo representar a expressão (...) | — | todo |
| `qt_votos_nulos` | `QT_VOTOS_NULOS` | texto | Quantidade de votos nulos totalizados. | — | todo |
| `qt_votos_nulos_tecnicos` | `QT_VOTOS_NULOS_TECNICOS` | texto | Quantidade de votos nulos técnicos. Votos nulos técnicos são votos dados à candidata, ao candidato ou em legenda que estavam inaptos no dia da eleição mas que constava na urna por não ter sido possível, por motivo técnico, removê-los. Esses candidatos e (...) | — | todo |
| `qt_votos_anulados_apu_sep` | `QT_VOTOS_ANULADOS_APU_SEP` | texto | Quantidade de votos anulados e apurados em separado referente ao cargo. Esse quantitativo reflete os votos oriundos de alguma urna que está sub judice. Ainda não são votos válidos e nem nulos até a decisão do juiz eleitoral. | — | todo |
| `hh_ultima_totalizacao` | `HH_ULTIMA_TOTALIZACAO` | texto | Hora da última totalização. | — | todo |
| `dt_ultima_totalizacao` | `DT_ULTIMA_TOTALIZACAO` | texto | Data da última totalização. | — | todo |

## No lake

- Estado: `so-bruto`. Não há dataset `tse/detalhe-votacao-munzona` no lake e, portanto, não há esquema de referência.
- Se o conjunto for baixado e convertido, o conversor o gravaria particionado por `ano` e `uf` (partição `uf` a partir do nome do membro, `__HIVE_DEFAULT_PARTITION__` para `BR`/`BRASIL`) com todas as colunas em texto, como nos demais datasets.

## Cuidados de uso

- Quando for convertido, o ZIP traria também `BRASIL` (e `BR`) junto com as UFs, e o conversor atual os leria todos: a dupla contagem descrita nos outros datasets se repetiria.
- Não conferido: layouts de outros anos, linhas, nulos e chave.

## Exemplos

Ainda não há dados no lake para este dataset. Depois de baixar e converter o conjunto, a leitura segue o padrão dos outros datasets (cada ano em `lake/tse/detalhe-votacao-munzona/ano=<ano>/`), por exemplo:

```python
import polars as pl

df = pl.scan_parquet("lake/tse/detalhe-votacao-munzona/ano=2024/uf=__HIVE_DEFAULT_PARTITION__/*_brasil.parquet")
```

O caminho acima é só ilustrativo e não foi executado: o dataset não existe no lake.

## Referências

- Conjunto no portal: https://dadosabertos.tse.jus.br/dataset/resultados-2024
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/
- Layout: `leiame.pdf` dentro do ZIP
