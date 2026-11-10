---
dataset:
  id: "candidatos"
  fonte: "tse"
  titulo: "Candidatos (consulta_cand)"
  resumo: "Candidaturas registradas nas eleições, uma linha por pessoa candidata, cargo e turno, com partido, federação, coligação, perfil declarado e resultado da totalização."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/candidatos-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos; o LEIAME dos arquivos avisa que CPF, e-mail e outros dados pessoais de candidatos podem vir ocultos (veja os cuidados de uso)."
  periodicidade: "diária segundo o portal de dados abertos (extração com data de geração em cada arquivo)"
  cobertura: {inicio: "2018", fim: 2026}
  unidade: "uma candidatura (pessoa candidata em uma eleição, cargo, unidade eleitoral e turno)"
  granularidade: {espacial: "unidade eleitoral (município, UF ou nacional), com UF", temporal: "eleição (ano e turno)"}
  formato_bruto: "ZIP por ano com um CSV por UF, mais os consolidados BR e BRASIL; CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho"
  lake: {estado: convertido, particoes: ["ano", "uf"], chave: ["ano", "nr_turno", "sq_candidato"], colunas: 50}
  unidades_de_medida: null
  dados_pessoais:
    - {coluna: "nr_cpf_candidato", categoria: "CPF"}
    - {coluna: "nm_candidato", categoria: "nome"}
    - {coluna: "nm_urna_candidato", categoria: "nome"}
    - {coluna: "nm_social_candidato", categoria: "nome social"}
    - {coluna: "ds_email", categoria: "e-mail (na prática sempre \"NÃO DIVULGÁVEL\")"}
    - {coluna: "dt_nascimento", categoria: "data de nascimento"}
    - {coluna: "nr_titulo_eleitoral_candidato", categoria: "título de eleitor"}
    - {coluna: "sg_uf_nascimento", categoria: "naturalidade"}
    - {coluna: "cd_genero", categoria: "gênero"}
    - {coluna: "ds_genero", categoria: "gênero"}
    - {coluna: "cd_cor_raca", categoria: "cor/raça (dado sensível)"}
    - {coluna: "ds_cor_raca", categoria: "cor/raça (dado sensível)"}
    - {coluna: "cd_estado_civil", categoria: "estado civil"}
    - {coluna: "ds_estado_civil", categoria: "estado civil"}
    - {coluna: "cd_grau_instrucao", categoria: "escolaridade"}
    - {coluna: "ds_grau_instrucao", categoria: "escolaridade"}
    - {coluna: "cd_ocupacao", categoria: "ocupação"}
    - {coluna: "ds_ocupacao", categoria: "ocupação"}
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
  eras:
    - {desde: "2024", mudanca: "`cd_situacao_candidatura` e `ds_situacao_candidatura` deixam de ser preenchidas (`-3`/`#NE`) e `nr_cpf_candidato` passa a vir `-4` (não divulgável) em todas as linhas; o cabeçalho de 50 colunas não muda de 2018 a 2026"}
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Candidatos (consulta_cand)

## Resumo

Cadastro das candidaturas registradas na Justiça Eleitoral a cada eleição, publicado pelo TSE no repositório de dados eleitorais (arquivo `consulta_cand`). Cada linha é uma candidatura com os dados do registro (cargo, número, nome, partido, federação, coligação), o perfil declarado (idade, gênero, escolaridade, estado civil, cor/raça, ocupação) e a situação de totalização (eleito, suplente, não eleito, 2º turno). Serve para contar candidaturas por cargo, partido, gênero ou escolaridade e como tabela de ligação (`sq_candidato`) com os bens, a votação e a prestação de contas.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/candidatos` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/candidatos-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos; o LEIAME dos arquivos avisa que CPF, e-mail e outros dados pessoais de candidatos podem vir ocultos (veja os cuidados de uso). |
| Periodicidade | diária segundo o portal de dados abertos (extração com data de geração em cada arquivo) |
| Cobertura | 2018 a 2026 |
| Unidade (uma linha) | uma candidatura (pessoa candidata em uma eleição, cargo, unidade eleitoral e turno) |
| Granularidade | espacial: unidade eleitoral (município, UF ou nacional), com UF; temporal: eleição (ano e turno) |
| Formato bruto | ZIP por ano com um CSV por UF, mais os consolidados BR e BRASIL; CSV em Latin-1 (ISO-8859-1), separador ponto e vírgula, todos os campos entre aspas duplas (inclusive os numéricos), uma linha de cabeçalho |
| Estado no lake | convertido |
| Partições | `ano`, `uf` |
| Chave | `ano`, `nr_turno`, `sq_candidato` |
| Colunas | 50 |
| Unidades de medida | — |
| Dados pessoais | `nr_cpf_candidato` (CPF); `nm_candidato` (nome); `nm_urna_candidato` (nome); `nm_social_candidato` (nome social); `ds_email` (e-mail (na prática sempre "NÃO DIVULGÁVEL")); `dt_nascimento` (data de nascimento); `nr_titulo_eleitoral_candidato` (título de eleitor); `sg_uf_nascimento` (naturalidade); `cd_genero` (gênero); `ds_genero` (gênero); `cd_cor_raca` (cor/raça (dado sensível)); `ds_cor_raca` (cor/raça (dado sensível)); `cd_estado_civil` (estado civil); `ds_estado_civil` (estado civil); `cd_grau_instrucao` (escolaridade); `ds_grau_instrucao` (escolaridade); `cd_ocupacao` (ocupação); `ds_ocupacao` (ocupação); `sq_candidato` (identificador da pessoa candidata) |
| Eras | 2024: `cd_situacao_candidatura` e `ds_situacao_candidatura` deixam de ser preenchidas (`-3`/`#NE`) e `nr_cpf_candidato` passa a vir `-4` (não divulgável) em todas as linhas; o cabeçalho de 50 colunas não muda de 2018 a 2026 |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- O fetcher baixa `consulta_cand_<ano>.zip` do CDN de estatísticas eleitorais do TSE (`https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/`), um ZIP por ano eleitoral.
- No bruto o arquivo guarda o nome da fonte, com o manifesto ao lado (`consulta_cand_2024.zip` e `consulta_cand_2024.zip.manifest.json`). Uma versão nova substitui a anterior.
- Dentro do ZIP há `leiame.pdf` (o layout oficial, descartado na conversão), um CSV por UF (`consulta_cand_<ano>_<UF>.csv`, incluindo `DF`), o consolidado `consulta_cand_<ano>_BRASIL.csv` e, nos anos de eleição geral (2018, 2022, 2026), `consulta_cand_<ano>_BR.csv` com as candidaturas de abrangência nacional (Presidente e Vice).
- Conferido em 2026-11-10 pela listagem do bruto: ZIPs de 2018, 2020, 2022, 2024 e 2026. O fetcher aceita anos desde 1994 (`DEFAULT_YEAR_RANGE` é 2018:2026); a fonte publica desde 1933.

## Conteúdo

- Unidade de análise: a candidatura, identificada por `sq_candidato` dentro da eleição (a chave é única por `ano`, `nr_turno` e `sq_candidato` nos arquivos por UF conferidos: 1.102.262 linhas distintas em 1.102.262). O `sq_candidato` é um sequencial interno de cada eleição, não o número de urna.
- Cobertura conferida (arquivo `BRASIL`, linhas): 2018: 29.287; 2020: 558.804; 2022: 29.322; 2024: 463.926; 2026: 21.017. As eleições gerais (2018, 2022, 2026) têm de 21 mil a 30 mil candidaturas; as municipais (2020, 2024), meio milhão.
- O arquivo de um ano inclui também as eleições suplementares que a fonte atribui àquele ciclo (`cd_tipo_eleicao = 1`); em 2024, por exemplo, há `ds_eleicao` de 2021.
- Eras: o cabeçalho tem as mesmas 50 colunas em todos os anos conferidos. O que muda é o preenchimento: a partir de 2024 a situação do registro não é mais preenchida e o CPF vem oculto; em 2026 o CPF volta a aparecer nos arquivos conferidos (42.028 de 42.034 linhas com 11 dígitos, contando o `BRASIL` e as UFs).
- Nulos e chave: números conferidos no lake de amostra completo dos cinco anos (2.204.712 linhas, com a duplicação descrita nos cuidados). Só `dt_nascimento` tem nulo (940 linhas), exatamente as de candidatos com dados não divulgáveis.

## Variáveis

Descrições do LEIAME oficial do TSE (consulta_cand, versão de 2024), resumidas; onde o texto não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto. As colunas de partição `ano` e `uf` não fazem parte dos arquivos Parquet e saem do nome do arquivo.

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
| `tp_abrangencia` | `TP_ABRANGENCIA` | texto | Abrangência da eleição. | . M: Municipal; . E: Estadual; e . F: Federal. Observação: a abrangência territorial da eleição está diretamente relacionada aos cargos eletivos e suas circunscrições eleitorais. As eleições (...) | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição. | — | todo |
| `sg_ue` | `SG_UE` | texto | Sigla da unidade eleitoral na qual a candidata ou candidato concorre na eleição. A unidade eleitoral representa a unidade da federação ou o município em que a candidata ou o candidato concorre na eleição e é relacionada à abrangência territorial desta (...) | — | todo |
| `nm_ue` | `NM_UE` | texto | Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal, é o nome do município em que (...) | — | todo |
| `cd_cargo` | `CD_CARGO` | texto | Código do cargo ao qual a candidata ou candidato concorre. | — | todo |
| `ds_cargo` | `DS_CARGO` | texto | Descrição do cargo ao qual a candidata ou candidato concorre. | — | todo |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. | — | todo |
| `nr_candidato` | `NR_CANDIDATO` | texto | Número da candidata ou candidato na urna. | — | todo |
| `nm_candidato` | `NM_CANDIDATO` | texto | Nome completo da candidata ou candidato. | — | todo |
| `nm_urna_candidato` | `NM_URNA_CANDIDATO` | texto | Nome da candidata ou candidato que aparece na urna. | — | todo |
| `nm_social_candidato` | `NM_SOCIAL_CANDIDATO` | texto | Nome social da candidata ou candidato. | — | todo |
| `nr_cpf_candidato` | `NR_CPF_CANDIDATO` | texto | Número do CPF da pessoa candidata. Não divulgável em 2024 (`-4` em todas as linhas conferidas); presente nos arquivos de 2018, 2020, 2022 e 2026 | CPF de 11 dígitos; `-4` = não divulgável | 2018-2022, 2026 |
| `ds_email` | `DS_EMAIL` | texto | Endereço de e-mail da pessoa candidata | conferido: sempre `NÃO DIVULGÁVEL` | todo |
| `cd_situacao_candidatura` | `CD_SITUACAO_CANDIDATURA` | texto | Código da situação do registro de candidatura. Segundo a fonte, aplicável só até as eleições de 2022; em 2024 e 2026 vem `-3` | `1` cadastrado, `3` inapto, `12` apto (conferido); `-3` = não registrado | até 2022 |
| `ds_situacao_candidatura` | `DS_SITUACAO_CANDIDATURA` | texto | Descrição da situação do registro de candidatura. Segundo a fonte, aplicável só até as eleições de 2022; em 2024 e 2026 vem `#NE` | CADASTRADO, INAPTO, APTO; `#NE` | até 2022 |
| `tp_agremiacao` | `TP_AGREMIACAO` | texto | Tipo de agremiação da candidatura, ou seja, forma como a candidata ou o candidato concorrerá nas eleições. | . Coligação: quando a candidata ou candidato concorre por coligação; . Federação: quando a candidata ou candidato concorre por uma federação; e . Partido Isolado: quando a candidata ou candidato (...) | todo |
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
| `sg_uf_nascimento` | `SG_UF_NASCIMENTO` | texto | Sigla da unidade da federação de nascimento da candidata ou candidato. | — | todo |
| `dt_nascimento` | `DT_NASCIMENTO` | texto | Data de nascimento da candidata ou candidato. | — | todo |
| `nr_titulo_eleitoral_candidato` | `NR_TITULO_ELEITORAL_CANDIDATO` | texto | Número do título eleitoral da candidata ou candidato. | — | todo |
| `cd_genero` | `CD_GENERO` | texto | Código do gênero da candidata ou candidato. | . 2: Masculino; e . 4: Feminino. | todo |
| `ds_genero` | `DS_GENERO` | texto | Descrição do gênero da candidata ou candidato. | — | todo |
| `cd_grau_instrucao` | `CD_GRAU_INSTRUCAO` | texto | Código do grau de instrução da candidata ou candidato. | . 1: Analfabeto; . 2: Lê e escreve; . 3: Ensino fundamental incompleto; . 4: Ensino fundamental completo; . 5: Ensino médio incompleto; . 6: Ensino médio completo; . 7: Superior incompleto; e . 8: (...) | todo |
| `ds_grau_instrucao` | `DS_GRAU_INSTRUCAO` | texto | Descrição do grau de instrução da candidata ou candidato. | — | todo |
| `cd_estado_civil` | `CD_ESTADO_CIVIL` | texto | Código do estado civil da candidata ou candidato. | . 1: Solteiro(a); . 3: Casado(a); . 5: Viúvo(a); . 7: Separado(a) judicialmente; e . 9: Divorciado(a). | todo |
| `ds_estado_civil` | `DS_ESTADO_CIVIL` | texto | Descrição do estado civil da candidata ou candidato. | — | todo |
| `cd_cor_raca` | `CD_COR_RACA` | texto | Código da cor/raça da candidata ou candidato. | . 01: Branca; . 02: Preta; . 03: Parda; . 04: Amarela; . 05: Indígena; e . 06: Não Informado. | todo |
| `ds_cor_raca` | `DS_COR_RACA` | texto | Descrição da cor/raça da candidata ou candidato. | — | todo |
| `cd_ocupacao` | `CD_OCUPACAO` | texto | Código da ocupação da candidata ou candidato. | — | todo |
| `ds_ocupacao` | `DS_OCUPACAO` | texto | Descrição da ocupação da candidata ou candidato. | — | todo |
| `cd_sit_tot_turno` | `CD_SIT_TOT_TURNO` | texto | Código da situação de totalização da candidata ou candidato no turno. | — | todo |
| `ds_sit_tot_turno` | `DS_SIT_TOT_TURNO` | texto | Descrição da situação de totalização da candidata ou candidato no turno. | — | todo |

## No lake

- Dataset `tse/candidatos`, particionado por `ano` e `uf`, um Parquet por CSV de origem (por membro do ZIP).
- `ano` e `uf` vêm do nome do membro (`consulta_cand_2022_SP.csv` dá `ano=2022`, `uf=sp`); o `BR` vai para `uf=br` e o `BRASIL` só é lido se o ZIP não tiver os arquivos por UF (então vai para `uf=__HIVE_DEFAULT_PARTITION__`).
- Todas as colunas são texto, com os nomes da fonte em minúsculas. O CSV é lido em Latin-1 com aspas duplas e campos com quebra de linha tratados. Nenhum marcador vira nulo.
- O LEIAME (`leiame.pdf`) é ignorado. O esquema de referência (`candidatos.schema.json`) tem 50 colunas, gerado de uma conversão real dos cinco anos.

## Cuidados de uso

- **Dupla contagem (corrigida; lake gerado até a versão 0.3.3 ainda tem).** O ZIP traz um CSV por UF, o `BR` (registros de âmbito nacional, quando existe) e o `BRASIL` (consolidado que repete as UFs e o `BR`). O conversor atual não lê o `BRASIL` quando o ZIP tem os arquivos por UF: lê as UFs (`uf=<sigla>`) e o `BR` (`uf=br`, com `sg_uf` = `BR`); se o ZIP só tiver o `BRASIL`, ele é lido e vai para `uf=__HIVE_DEFAULT_PARTITION__`. Assim somar o lake inteiro conta cada linha uma vez. Um lake gerado antes da correção tem os Parquets do `BRASIL` em `uf=__HIVE_DEFAULT_PARTITION__` e as linhas em dobro: apague `tse/candidatos/` e reconverta (veja o `CHANGELOG.md`). Evidência (conferida em 2026-11-10 com o conversor atual): em 2018 o `BRASIL` tem 29.287 linhas, as UFs somam 29.255 e o `BR` 32, e o lake passa a ter 29.287; em 2020 e 2024 o `BRASIL` tem exatamente a soma das UFs (558.804 e 463.926).
- **Marcadores da fonte ficam como texto, não viram nulo.** Segundo o LEIAME, `#NULO` indica campo em branco (`-1` nos numéricos), `#NE` indica informação não registrada naquele ano (`-3`) e `-4` indica dado pessoal não divulgável. O lake os guarda literais; a escrita varia entre arquivos (`#NULO#` em 2018 e `#NULO` em 2024, conferido nas amostras), então teste as duas. Nulo de verdade só aparece em campos vazios.
- **CPF, título de eleitor e e-mail.** O CPF vem preenchido em 2018, 2020, 2022 e 2026 e `-4` em 2024; o e-mail é sempre `NÃO DIVULGÁVEL` e o título de eleitor traz o número, salvo `-4` em candidaturas não divulgáveis. Para candidaturas não divulgáveis o LEIAME diz que os campos textuais pessoais vêm como `NÃO DIVULGÁVEL`, os numéricos como `-4` e a idade e a data de nascimento ficam em branco. Em 2022 há candidaturas com `ds_genero = NÃO DIVULGÁVEL`.
- **Situação do registro** só existe até 2022; para 2024 em diante use `ds_sit_tot_turno`, que também traz `#NULO` para quem ainda não teve apuração (por exemplo suplementares e candidaturas sem votos).
- **Eleições suplementares** estão no arquivo do ciclo ordinário: filtre por `cd_tipo_eleicao = 2` para só a eleição ordinária.
- **Ano do arquivo e `ano_eleicao`** coincidiram nas 2.204.712 linhas conferidas.

## Exemplos

Candidaturas ordinárias de 2022 por cargo e gênero (cada linha uma vez):

```python
import polars as pl

cand = pl.scan_parquet(
    "lake/tse/candidatos/ano=2022/*/*.parquet", hive_partitioning=True
)
resumo = (
    cand.filter(pl.col("cd_tipo_eleicao") == "2")
    .group_by("ds_cargo", "ds_genero")
    .agg(pl.len().alias("candidaturas"))
    .sort("ds_cargo", "ds_genero")
    .collect()
)
```

## Referências

- Conjunto de 2024: https://dadosabertos.tse.jus.br/dataset/candidatos-2024 (há um por ano, `candidatos-<ano>`)
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/
- Layout: `leiame.pdf` dentro de cada ZIP
- Contato da fonte para dúvidas: estatistica@tse.jus.br (citado no LEIAME)
