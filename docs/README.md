# Tribunal Superior Eleitoral — dados eleitorais (`tse`)

O `tse-fetcher` coleta do repositório de dados eleitorais do Tribunal Superior Eleitoral (TSE), no CDN de estatísticas eleitorais (`cdn.tse.jus.br/estatistica/sead/odsele`), quatro conjuntos de arquivos ZIP: candidatos, bens de candidatos, votação nominal por município e zona, e prestação de contas de campanha. O conversor do lake declara doze datasets; os quatro primeiros abaixo têm dados convertidos, os oito seguintes são reconhecidos pelo conversor mas não são baixados pelo fetcher (estado `so-bruto`).

| Dataset | O que é | Origem | Período no bruto | Estado | Página |
|---|---|---|---|---|---|
| `candidatos` | Candidaturas registradas, com perfil e situação de totalização | `consulta_cand_<ano>.zip` | 2018 a 2026 | convertido | [candidatos](datasets/candidatos.md) |
| `bens-candidatos` | Bens declarados pelas candidaturas | `bem_candidato_<ano>.zip` | 2018 a 2026 | convertido | [bens-candidatos](datasets/bens-candidatos.md) |
| `votacao-munzona` | Votos nominais por candidatura, município e zona | `votacao_candidato_munzona_<ano>.zip` | 2018, 2020, 2024 (2022 e 2026 no bruto, não abertos) | convertido | [votacao-munzona](datasets/votacao-munzona.md) |
| `prestacao-contas` | Receitas e despesas de campanha (quatro famílias de arquivos num dataset) | `prestacao_de_contas_eleitorais_candidatos_<ano>.zip` | 2020 a 2026 | convertido | [prestacao-contas](datasets/prestacao-contas.md) |
| `votacao-secao` | Votos por seção eleitoral | `votacao_secao_<ano>_<UF>.zip` | não baixado | so-bruto | [votacao-secao](datasets/votacao-secao.md) |
| `detalhe-votacao-munzona` | Totais da apuração por município e zona | `detalhe_votacao_munzona_<ano>.zip` | não baixado | so-bruto | [detalhe-votacao-munzona](datasets/detalhe-votacao-munzona.md) |
| `detalhe-votacao-secao` | Totais da apuração por seção | `detalhe_votacao_secao_<ano>.zip` | não baixado | so-bruto | [detalhe-votacao-secao](datasets/detalhe-votacao-secao.md) |
| `eleitorado` | Perfil do eleitorado | `perfil_eleitorado_<ano>.zip` | não baixado | so-bruto | [eleitorado](datasets/eleitorado.md) |
| `redes-sociais` | Redes sociais informadas pelas candidaturas | `rede_social_candidato_<ano>.zip` | não baixado | so-bruto | [redes-sociais](datasets/redes-sociais.md) |
| `motivo-cassacao` | Motivos de indeferimento, cassação ou não diplomação | `motivo_cassacao_<ano>.zip` | não baixado | so-bruto | [motivo-cassacao](datasets/motivo-cassacao.md) |
| `vagas` | Vagas em disputa por cargo e unidade eleitoral | `consulta_vagas_<ano>.zip` | não baixado | so-bruto | [vagas](datasets/vagas.md) |
| `boletim-urna` | Boletins de urna | `bweb_<turno>_<UF>_<data>.zip` | não baixado | so-bruto | [boletim-urna](datasets/boletim-urna.md) |

## Como o TSE publica

- O portal de dados abertos (`dadosabertos.tse.jus.br`) organiza os conjuntos por ano (`candidatos-<ano>`, `resultados-<ano>`, `prestacao-de-contas-eleitorais-<ano>`, `eleitorado-<ano>`). Todos os conjuntos conferidos declaram a licença Creative Commons Attribution (CC BY). Candidatos e resultados declaram atualização diária; a prestação de contas não declara frequência. Cada arquivo traz a data e a hora de geração nas colunas `DT_GERACAO` e `HH_GERACAO`.
- Os arquivos ficam no CDN em ZIP por ano. Dentro de cada ZIP há um CSV por unidade da federação, o consolidado `BRASIL` e, nas eleições gerais, o `BR` (candidaturas de abrangência nacional); o `leiame.pdf` descreve o layout. A prestação de contas é um ZIP nacional por ano, com quatro famílias de CSV e quatro `leiame_*.pdf`.
- Os CSV usam Latin-1, ponto e vírgula e aspas duplas em todos os campos, inclusive os numéricos. Campos de texto livre (descrição de bem, histórico) podem conter quebra de linha dentro das aspas.
- O LEIAME define marcadores: `#NULO` (campo em branco, `-1` nos numéricos), `#NE` (informação não registrada naquele ano, `-3`) e `-4` (dado pessoal não divulgável). O LEIAME de 2024 informa que o CPF do candidato não é divulgado naquele ano (art. 33, § 2º, da Resolução TSE nº 23.609/2019).

## O que vale para todos os datasets

- **Dupla contagem.** O conversor lê o `BRASIL` e o `BR` junto com os arquivos de cada UF, e eles caem em `uf=__HIVE_DEFAULT_PARTITION__`. Conferido para `candidatos`, `bens-candidatos`, `votacao-munzona` (2018, 2020, 2024): o `BRASIL` tem exatamente as linhas das UFs (mais o `BR`, em 2018). Em `prestacao-contas` os ZIPs seguem o mesmo padrão (UFs, `BR` e `BRASIL`), mas a contagem de linhas não foi feita. Leia o `*_brasil.parquet` de cada ano, ou só as UFs mais o `BR`.
- **Tudo é texto.** O lake guarda todas as colunas como texto, incluindo valores em reais com vírgula decimal e datas `dd/mm/aaaa`, e os marcadores `#NULO`, `#NE`, `-1`, `-3` e `-4` ficam literais.
- **Dados pessoais.** Candidaturas e prestação de contas trazem nomes, CPF, título de eleitor, data de nascimento, gênero e cor/raça. São públicos por lei eleitoral, mas pessoais; cada página lista as colunas no cabeçalho como inventário.
- **Eleições suplementares** vêm dentro do arquivo do ciclo ordinário correspondente.

## Quebras que valem para mais de um conjunto

| Desde | Mudança | Afeta |
|---|---|---|
| 2020 | Prestação de contas passa a ser um arquivo nacional único por ano; os arquivos por UF anteriores foram removidos do CDN | `prestacao-contas` |
| 2024 | CPF do candidato não divulgado (`-4`); situação do registro de candidatura deixa de ser preenchida (`#NE`) | `candidatos` |
| 2020 | Colunas de diploma da votação por município e zona mudam de nome (`..._diploma` para `..._dconst_diploma`) | `votacao-munzona` |
