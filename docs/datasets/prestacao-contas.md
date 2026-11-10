---
dataset:
  id: "prestacao-contas"
  fonte: "tse"
  titulo: "Prestação de contas eleitorais de candidatos"
  resumo: "Receitas, doadores originários, despesas contratadas e despesas pagas declaradas pelas campanhas, quatro famílias de arquivos reunidas num só dataset, uma linha por lançamento."
  orgao: "Tribunal Superior Eleitoral (TSE)"
  pagina_oficial: "https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2024"
  licenca: "Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos."
  periodicidade: "não informado pela fonte (o conjunto não declara frequência de atualização; cada arquivo traz a data de geração)"
  cobertura: {inicio: "2020", fim: 2026}
  unidade: "um lançamento de receita, de doador originário, de despesa contratada ou de despesa paga (o tipo depende do arquivo de origem, que não é gravado como coluna)"
  granularidade: {espacial: "candidatura (com UF); o doador e o fornecedor trazem UF e município próprios", temporal: "lançamento, com data da receita/despesa"}
  formato_bruto: "ZIP nacional por ano com 4 famílias de CSV (`receitas_candidatos`, `receitas_candidatos_doador_originario`, `despesas_contratadas_candidatos`, `despesas_pagas_candidatos`), cada uma com um arquivo por UF, `BR` e `BRASIL`, mais quatro `leiame_*.pdf`; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas"
  lake: {estado: convertido, particoes: ["ano", "uf"], chave: [], colunas: 102}
  unidades_de_medida: {vr_receita: "R$ (texto com vírgula decimal)", vr_despesa_contratada: "R$ (texto com vírgula decimal)", vr_pagto_despesa: "R$ (texto com vírgula decimal)"}
  dados_pessoais:
    - {coluna: "nr_cpf_candidato", categoria: "CPF (`-4` nos arquivos conferidos de 2026)"}
    - {coluna: "nr_cpf_vice_candidato", categoria: "CPF"}
    - {coluna: "nm_candidato", categoria: "nome"}
    - {coluna: "nr_cpf_cnpj_doador", categoria: "CPF ou CNPJ do doador"}
    - {coluna: "nm_doador", categoria: "nome do doador"}
    - {coluna: "nm_doador_rfb", categoria: "nome do doador na Receita Federal"}
    - {coluna: "nr_cpf_cnpj_doador_originario", categoria: "CPF ou CNPJ do doador originário"}
    - {coluna: "nm_doador_originario", categoria: "nome"}
    - {coluna: "nm_doador_originario_rfb", categoria: "nome"}
    - {coluna: "nr_cpf_cnpj_fornecedor", categoria: "CPF ou CNPJ do fornecedor"}
    - {coluna: "nm_fornecedor", categoria: "nome do fornecedor"}
    - {coluna: "nm_fornecedor_rfb", categoria: "nome do fornecedor na Receita Federal"}
    - {coluna: "ds_genero", categoria: "gênero"}
    - {coluna: "ds_cor_raca", categoria: "cor/raça (dado sensível)"}
    - {coluna: "sq_candidato", categoria: "identificador da pessoa candidata"}
    - {coluna: "ds_receita", categoria: "texto livre"}
    - {coluna: "ds_despesa", categoria: "texto livre"}
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.3
---

# Prestação de contas eleitorais de candidatos

## Resumo

Prestação de contas de campanha dos candidatos, publicada pelo TSE como um ZIP nacional por ano com quatro famílias de arquivos: receitas, doadores originários das receitas, despesas contratadas e despesas pagas. O conversor lê todos num único dataset, o que dá um esquema de 102 colunas em que cada arquivo ocupa só as suas (60, 23, 53 e 28 colunas). Serve para totalizar o que as campanhas arrecadaram e gastaram, por candidato, partido, doador ou fornecedor.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tse/prestacao-contas` |
| Órgão | Tribunal Superior Eleitoral (TSE) |
| Página oficial | https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2024 |
| Licença | Creative Commons Attribution (CC BY), conforme os conjuntos no portal de dados abertos do TSE: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de coleta ou de redistribuição foi encontrada nas páginas dos conjuntos. |
| Periodicidade | não informado pela fonte (o conjunto não declara frequência de atualização; cada arquivo traz a data de geração) |
| Cobertura | 2020 a 2026 |
| Unidade (uma linha) | um lançamento de receita, de doador originário, de despesa contratada ou de despesa paga (o tipo depende do arquivo de origem, que não é gravado como coluna) |
| Granularidade | espacial: candidatura (com UF); o doador e o fornecedor trazem UF e município próprios; temporal: lançamento, com data da receita/despesa |
| Formato bruto | ZIP nacional por ano com 4 famílias de CSV (`receitas_candidatos`, `receitas_candidatos_doador_originario`, `despesas_contratadas_candidatos`, `despesas_pagas_candidatos`), cada uma com um arquivo por UF, `BR` e `BRASIL`, mais quatro `leiame_*.pdf`; CSV em Latin-1, separador ponto e vírgula, campos entre aspas duplas |
| Estado no lake | convertido |
| Partições | `ano`, `uf` |
| Chave | — |
| Colunas | 102 |
| Unidades de medida | `vr_receita`: R$ (texto com vírgula decimal); `vr_despesa_contratada`: R$ (texto com vírgula decimal); `vr_pagto_despesa`: R$ (texto com vírgula decimal) |
| Dados pessoais | `nr_cpf_candidato` (CPF (`-4` nos arquivos conferidos de 2026)); `nr_cpf_vice_candidato` (CPF); `nm_candidato` (nome); `nr_cpf_cnpj_doador` (CPF ou CNPJ do doador); `nm_doador` (nome do doador); `nm_doador_rfb` (nome do doador na Receita Federal); `nr_cpf_cnpj_doador_originario` (CPF ou CNPJ do doador originário); `nm_doador_originario` (nome); `nm_doador_originario_rfb` (nome); `nr_cpf_cnpj_fornecedor` (CPF ou CNPJ do fornecedor); `nm_fornecedor` (nome do fornecedor); `nm_fornecedor_rfb` (nome do fornecedor na Receita Federal); `ds_genero` (gênero); `ds_cor_raca` (cor/raça (dado sensível)); `sq_candidato` (identificador da pessoa candidata); `ds_receita` (texto livre); `ds_despesa` (texto livre) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.3 |

## Origem e coleta

- O fetcher baixa `prestacao_de_contas_eleitorais_candidatos_<ano>.zip` do CDN (`https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/`). Desde 2020 o TSE publica um arquivo nacional único por ano; os arquivos antigos por UF (`despesas_candidato_2020_RJ.zip`) foram removidos do CDN e respondem 404. Os anos anteriores a 2020 não são baixados (`first_year = 2020`).
- No bruto o nome é o da fonte, com manifesto ao lado (de 0,4 a 1,4 GB cada).
- Cada ZIP traz 4 `leiame_*.pdf` (descartados) e, para cada família, um CSV por UF, o `BR` e o `BRASIL`. Conferido em 2026-11-10 pela listagem do bruto e pelo índice interno dos ZIPs: 2020 (112 membros, 4,99 GB só nas despesas contratadas), 2022 (120), 2024 (112) e 2026 (o membro `despesas_contratadas_candidatos_2026_BRASIL.csv` tem 1,09 GB).
- O pacote do portal tem ainda órgãos partidários, CNPJ de campanha, extratos bancários e FEFC/FP; o fetcher não baixa esses.

## Conteúdo

- Unidade de análise: o lançamento. Em `receitas` e `doador originario`, uma receita (`sq_receita`); em `despesas contratadas` e `pagas`, uma despesa (`sq_despesa`; as pagas têm também `sq_parcelamento_despesa`).
- Cobertura: eleições de 2020, 2022, 2024 e 2026 (bruto conferido em 2026-11-10). 2026 reflete a prestação em andamento, com `tp_prestacao_contas` `PARCIAL`, `FINAL` e `RELATÓRIO FINANCEIRO` na amostra.
- Layout: os cabeçalhos de cada família são idênticos em 2020, 2022, 2024 e 2026 (conferidos nos índices e no cabeçalho de um membro de cada ano); não há quebra de layout.
- Nulos e chave: só amostra (membros do Acre de 2026). `dt_receita` e `dt_despesa` têm nulos (39 de 3.005 e 95 de 22.427 linhas); `sq_receita` não é único (2.928 distintos em 3.005 linhas), e `sq_despesa` também não (18.456 em 22.427 nas contratadas e 18.040 em 23.061 nas pagas), então não há chave verificada.

## Variáveis

Descrições dos quatro `leiame_*.pdf` oficiais do TSE; a coluna Período diz em quais famílias a coluna existe. Onde o LEIAME não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `dt_geracao` | `DT_GERACAO` | texto | Data da extração dos dados para geração do arquivo. | — | todas as famílias |
| `hh_geracao` | `HH_GERACAO` | texto | Hora da extração dos dados para geração do arquivo com base no horário de Brasília. | — | todas as famílias |
| `aa_eleicao` | `AA_ELEICAO` | texto | Ano de referência da eleição. O LEIAME a chama `ANO_ELEICAO`, mas o cabeçalho do CSV traz `AA_ELEICAO` | — | todas as famílias |
| `cd_tipo_eleicao` | `CD_TIPO_ELEICAO` | texto | Código do tipo de eleição. | 1 - Eleição Suplementar, 2 - Eleição Ordinária e 3 - Consulta Popular. | todas as famílias |
| `nm_tipo_eleicao` | `NM_TIPO_ELEICAO` | texto | Nome do tipo de eleição. | — | todas as famílias |
| `cd_eleicao` | `CD_ELEICAO` | texto | Código único da eleição no âmbito da Justiça Eleitoral. | — | todas as famílias |
| `ds_eleicao` | `DS_ELEICAO` | texto | Descrição da eleição. | — | todas as famílias |
| `dt_eleicao` | `DT_ELEICAO` | texto | Data em que ocorreu a eleição. | — | todas as famílias |
| `st_turno` | `ST_TURNO` | texto | Indica o último turno em que a candidata ou candidato prestador de contas concorreu na eleição. Esta informação impacta no prazo para a prestação de contas, conforme estabelecido em lei. | - 1- 1º Turno; - 2- 2º Turno. | todas as famílias |
| `tp_prestacao_contas` | `TP_PRESTACAO_CONTAS` | texto | Tipo de entrega da prestação de contas. | 0 - Final, 1 - Relatório Financeiro e 2 - Parcial. Tipo 0 - Final: é o tipo de entrega final da prestação de contas, onde serão gerados os relatórios de análise, exame, diligência e conclusivo. Tipo (...) | todas as famílias |
| `dt_prestacao_contas` | `DT_PRESTACAO_CONTAS` | texto | Data de entrega da prestação de contas junto ao TSE. Essas datas são pré-definidas conforme o tipo de entrega da prestação de contas. | — | todas as famílias |
| `sq_prestador_contas` | `SQ_PRESTADOR_CONTAS` | texto | Número sequencial do prestador de contas, gerado internamento pelos sistemas eleitorais para cada eleição. | — | todas as famílias |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação de abrangência do prestador de contas. | — | todas as famílias |
| `sg_ue` | `SG_UE` | texto | Sigla da Unidade Eleitoral em que o candidato prestador de contas concorre na eleição. A Unidade Eleitoral representa a Unidade da Federação ou o Município em que o candidato concorre na eleição e é relacionada à abrangência territorial desta candidatura. Em (...) | — | só receitas, despesas contratadas |
| `nm_ue` | `NM_UE` | texto | Nome da Unidade Eleitoral do candidato prestador de contas. Em caso de abrangência nacional é igual à "Brasil". Em caso de abrangência estadual é o nome da UF em que o candidato concorre. Em caso de abrangência municipal é o nome do município em que o (...) | — | só receitas, despesas contratadas |
| `nr_cnpj_prestador_conta` | `NR_CNPJ_PRESTADOR_CONTA` | texto | Número do CNPJ do candidato prestador de contas cadastrado junto à Receita Federal. | — | só receitas, despesas contratadas |
| `cd_cargo` | `CD_CARGO` | texto | Código do cargo concorrido na eleição pelo candidato prestador de contas. | — | só receitas, despesas contratadas |
| `ds_cargo` | `DS_CARGO` | texto | Cargo concorrido na eleição pelo candidato prestador de contas. | — | só receitas, despesas contratadas |
| `sq_candidato` | `SQ_CANDIDATO` | texto | Número sequencial do candidato, gerado internamente pelos sistemas eleitorais para cada eleição. Observações: 1) Este sequencial pode ser utilizado como chave para o cruzamento de dados. 2) Não é o número de campanha do candidato. | — | só receitas, despesas contratadas |
| `nr_candidato` | `NR_CANDIDATO` | texto | Número do candidato prestador de contas na eleição, fornecido pela Justiça Eleitoral. Este número é o número que aparece na urna e é fornecido pela Justiça Eleitoral. | — | só receitas, despesas contratadas |
| `nm_candidato` | `NM_CANDIDATO` | texto | Nome completo do candidato prestador de contas. | — | só receitas, despesas contratadas |
| `nr_cpf_candidato` | `NR_CPF_CANDIDATO` | texto | Número do CPF do candidato prestador de contas registrado na Justiça Eleitoral e cadastrado junto à Receita Federal. | — | só receitas, despesas contratadas |
| `nr_cpf_vice_candidato` | `NR_CPF_VICE_CANDIDATO` | texto | Número do CPF do candidato à vice/suplente do candidato titular prestador de contas, registrado na Justiça Eleitoral e cadastrado junto à Receita Federal. | — | só receitas, despesas contratadas |
| `nr_partido` | `NR_PARTIDO` | texto | Número do partido do candidato prestador de contas na eleição, fornecido pela Justiça Eleitoral. | — | só receitas, despesas contratadas |
| `sg_partido` | `SG_PARTIDO` | texto | Sigla do partido do candidato prestador de contas. | — | só receitas, despesas contratadas |
| `nm_partido` | `NM_PARTIDO` | texto | Nome do partido do candidato prestador de contas. | — | só receitas, despesas contratadas |
| `cd_fonte_receita` | `CD_FONTE_RECEITA` | texto | Código do tipo de fonte de recursos da receita declarada. | 0 - Fundo Partidário, 1 - Outros Recursos, 2 - Fundo Especial e 9 - Não informado. | só receitas |
| `ds_fonte_receita` | `DS_FONTE_RECEITA` | texto | Tipo de fonte de recursos da receita declarada. | — | só receitas |
| `cd_origem_receita` | `CD_ORIGEM_RECEITA` | texto | Código de identificação do tipo de origem da receita declarada. É o código da conta DRD (Descrição de Receitas e Despesas) informado pelo prestador de contas. | — | só receitas |
| `ds_origem_receita` | `DS_ORIGEM_RECEITA` | texto | Origem da receita declarada, conforme o código DRD informado pelo prestador de contas. | — | só receitas |
| `cd_natureza_receita` | `CD_NATUREZA_RECEITA` | texto | Código da natureza de recursos da receita declarada pela candidata ou candidato prestador de contas. | - 0- Estimável; - 1- Financeiro. | só receitas |
| `ds_natureza_receita` | `DS_NATUREZA_RECEITA` | texto | Natureza de recursos da receita declarada. | — | só receitas |
| `cd_especie_receita` | `CD_ESPECIE_RECEITA` | texto | Código de identificação da espécie de recurso utilizada na receita declarada. Quando a natureza do recurso da receita for '0 - Estimável', a espécie do recurso da receita assume o valor '2 - Estimado'. Quando a natureza do recurso da receita for '1 - (...) | — | só receitas |
| `ds_especie_receita` | `DS_ESPECIE_RECEITA` | texto | Espécie de recurso utilizada na receita declarada. | — | só receitas |
| `cd_cnae_doador` | `CD_CNAE_DOADOR` | texto | Código Nacional de Atividade Empresarial - CNAE do doador da receita informada pelo candidato prestador de contas. Este campo é preenchido apenas para os doadores do tipo 0 - Pessoa Jurídica. | — | só receitas |
| `ds_cnae_doador` | `DS_CNAE_DOADOR` | texto | Nome da atividade empresarial conforme o código CNAE do doador da receita informada pelo prestador de contas. Este campo é preenchido apenas para os doadores do tipo 0 - Pessoa Jurídica. | — | só receitas |
| `nr_cpf_cnpj_doador` | `NR_CPF_CNPJ_DOADOR` | texto | Número do CPF/CNPJ do doador da receita informada pelo candidato prestador de contas. | — | só receitas |
| `nm_doador` | `NM_DOADOR` | texto | Nome, declarado à Justiça Eleitoral, do doador da receita informada pelo candidato prestador de contas. | — | só receitas |
| `nm_doador_rfb` | `NM_DOADOR_RFB` | texto | Nome declarado à Justiça Eleitoral e cadastrado na Receita Federal do doador da receita informada pelo candidato prestador de contas. | — | só receitas |
| `cd_esfera_partidaria_doador` | `CD_ESFERA_PARTIDARIA_DOADOR` | texto | Esfera indica a abrangência territorial de cada cargo concorrido na eleição e pode ser utilizada pelos cargos e órgãos partidários. Neste caso, é o código que representa o tipo de esfera do doador quando este é um órgão partidário. | N - Nacional, E - Estadual, Z - Zonal, M - Municipal, D - Distrital e F - Federal (Estadual/Distrital). | só receitas |
| `ds_esfera_partidaria_doador` | `DS_ESFERA_PARTIDARIA_DOADOR` | texto | Tipo de esfera partidária do doador quando este é um órgão partidário. | — | só receitas |
| `sg_uf_doador` | `SG_UF_DOADOR` | texto | Sigla da unidade da federação do doador, de acordo com sua esfera partidária, quando este é um doador candidato ou órgão partidário. | — | só receitas |
| `cd_municipio_doador` | `CD_MUNICIPIO_DOADOR` | texto | Código do município do doador quando a esfera partidária do mesmo for municipal. | — | só receitas |
| `nm_municipio_doador` | `NM_MUNICIPIO_DOADOR` | texto | Município do doador quando a esfera partidária do mesmo for municipal. | — | só receitas |
| `sq_candidato_doador` | `SQ_CANDIDATO_DOADOR` | texto | Sequencial do candidato doador, quando o doador for um candidato, gerado internamente pelos sistemas eleitorais. | — | só receitas |
| `nr_candidato_doador` | `NR_CANDIDATO_DOADOR` | texto | Número do candidato doador declarado pelo prestador de contas, quando o doador for um candidato. Este número é o número que aparece na urna e é fornecido pela Justiça Eleitoral. | — | só receitas |
| `cd_cargo_candidato_doador` | `CD_CARGO_CANDIDATO_DOADOR` | texto | Código do cargo do candidato doador declarado pelo prestador de contas, quando o doador for um candidato. | — | só receitas |
| `ds_cargo_candidato_doador` | `DS_CARGO_CANDIDATO_DOADOR` | texto | Cargo do candidato doador declarado pelo prestador de contas, quando o doador for um candidato. | — | só receitas |
| `nr_partido_doador` | `NR_PARTIDO_DOADOR` | texto | Número do partido do doador declarado pelo prestador de contas, quando o doador for um candidato ou órgão partidário. | — | só receitas |
| `sg_partido_doador` | `SG_PARTIDO_DOADOR` | texto | Sigla do partido do doador declarada pelo prestador de contas, quando o doador for um candidato ou órgão partidário. | — | só receitas |
| `nm_partido_doador` | `NM_PARTIDO_DOADOR` | texto | Nome do partido do doador declarado pelo prestador de contas, quando o doador for um candidato ou órgão partidário. | — | só receitas |
| `nr_recibo_doacao` | `NR_RECIBO_DOACAO` | texto | Número de recibo de doação informada pelo prestador de contas em relação à receita declarada. | — | só receitas |
| `nr_documento_doacao` | `NR_DOCUMENTO_DOACAO` | texto | Número do documento da doação informado pelo prestador de contas referente à receita declarada. Por exemplo, número do cheque ou da transferência bancária. | — | só receitas |
| `sq_receita` | `SQ_RECEITA` | texto | Sequencial de identificação do registro da receita declarada pelo prestador de contas, gerado internamente pelos sistemas eleitorais. | — | só receitas, doador originário |
| `dt_receita` | `DT_RECEITA` | texto | Data da receita declarada, informada pelo prestador de contas. | — | só receitas, doador originário |
| `ds_receita` | `DS_RECEITA` | texto | Descrição resumida informada pelo prestador de contas. | — | só receitas, doador originário |
| `vr_receita` | `VR_RECEITA` | texto | Valor da receita declarada, informado pelo prestador de contas, em Reais (R$). | — | só receitas, doador originário |
| `ds_natureza_recurso_estimavel` | `DS_NATUREZA_RECURSO_ESTIMAVEL` | texto | É a descrição da natureza do recurso estimável para a receita. | — | só receitas |
| `ds_genero` | `DS_GENERO` | texto | É a descrição do gênero do prestador de contas do tipo "Candidata" ou "Candidato", ao qual foi informado pela candidata ou pelo candidato à Justíça Eleitoral. (Autodeclaração). | — | só receitas |
| `ds_cor_raca` | `DS_COR_RACA` | texto | É a descrição da cor/raça do prestador de contas do tipo "Candidata" ou "Candidato", a qual foi informada pela candidata ou pelo candidato à Justíça Eleitoral. (Autodeclaração). | — | só receitas |
| `nr_cpf_cnpj_doador_originario` | `NR_CPF_CNPJ_DOADOR_ORIGINARIO` | texto | Número do CPF/CNPJ do doador originário da receita declarada pelo prestador de contas quando esta doação se der entre candidatos e/ou órgãos partidários ou quando a doação advém de Financiamento Coletivo de Campanha. Doador originário é aquele que foi o (...) | — | só doador originário |
| `nm_doador_originario` | `NM_DOADOR_ORIGINARIO` | texto | Nome, declarado à Justiça Eleitoral, do doador originário da receita informada pelo prestador de contas. | — | só doador originário |
| `nm_doador_originario_rfb` | `NM_DOADOR_ORIGINARIO_RFB` | texto | Nome declarado à Justiça Eleitoral e cadastrado na Receita Federal do doador originário da receita informada pelo prestador de contas. | — | só doador originário |
| `tp_doador_originario` | `TP_DOADOR_ORIGINARIO` | texto | Código do tipo do doador originário, em relação à natureza jurídica do mesmo, informado pelo prestador de contas e em relação à doação. | J - Pessoa Jurídica e F - Pessoa Física. | só doador originário |
| `cd_cnae_doador_originario` | `CD_CNAE_DOADOR_ORIGINARIO` | texto | Código Nacional de Atividade Empresarial - CNAE do doador originário da receita informada pelo prestador de contas. Este campo é preenchido apenas para os doadores originários do tipo J - Pessoa Jurídica. | — | só doador originário |
| `ds_cnae_doador_originario` | `DS_CNAE_DOADOR_ORIGINARIO` | texto | Nome da atividade empresarial conforme o código CNAE do doador originário da receita informada pelo prestador de contas. Este campo é preenchido apenas para os doadores originários do tipo J - Pessoa Jurídica. | — | só doador originário |
| `cd_tipo_fornecedor` | `CD_TIPO_FORNECEDOR` | texto | Código do tipo de fornecedor, em relação à natureza jurídica do mesmo, informado pela candidata ou candidato prestador de contas e em relação à despesa. | - 0- Pessoa Jurídica; - 1- Pessoa Física. | só despesas contratadas |
| `ds_tipo_fornecedor` | `DS_TIPO_FORNECEDOR` | texto | Tipo de natureza jurídica do fornecedor, informado pela candidata ou candidato prestador de contas em relação à despesa. | — | só despesas contratadas |
| `cd_cnae_fornecedor` | `CD_CNAE_FORNECEDOR` | texto | Código Nacional de Atividade Empresarial - CNAE do fornecedor de bens e/ou serviços da despesa informada pela candidata ou candidato prestador de contas. Este campo é preenchido apenas para os fornecedores do tipo 0 - Pessoa Jurídica. | — | só despesas contratadas |
| `ds_cnae_fornecedor` | `DS_CNAE_FORNECEDOR` | texto | Nome da atividade empresarial conforme o código CNAE do fornecedor de bens e/ou serviços da despesa informada pela candidata ou candidato prestador de contas. Este campo é preenchido apenas para os fornecedores do tipo 0 - Pessoa Jurídica. | — | só despesas contratadas |
| `nr_cpf_cnpj_fornecedor` | `NR_CPF_CNPJ_FORNECEDOR` | texto | Número do CPF/CNPJ do fornecedor de bens e/ou serviços da despesa informada pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `nm_fornecedor` | `NM_FORNECEDOR` | texto | Nome, declarado à Justiça Eleitoral, do fornecedor de bens e/ou serviços da despesa informada pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `nm_fornecedor_rfb` | `NM_FORNECEDOR_RFB` | texto | Nome declarado à Justiça Eleitoral e cadastrado na Receita Federal do fornecedor de bens e/ou serviços da despesa informada pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `cd_esfera_part_fornecedor` | `CD_ESFERA_PART_FORNECEDOR` | texto | Esfera que indica a abrangência territorial de cada cargo concorrido na eleição. Neste caso, é o código que representa o tipo de esfera do fornecedor quando este é um órgão partidário. | - N- Nacional; - E- Estadual; - Z- Zonal; - M- Municipal; - D- Distrital; - F- Federal (Estadual/Distrital). | só despesas contratadas |
| `ds_esfera_part_fornecedor` | `DS_ESFERA_PART_FORNECEDOR` | texto | Esfera partidária do fornecedor quando este é um órgão partidário. | — | só despesas contratadas |
| `sg_uf_fornecedor` | `SG_UF_FORNECEDOR` | texto | Sigla da Unidade da Federação do fornecedor, de acordo com sua esfera partidária, quando este fornecedor é uma candidata, um candidato ou órgão partidário. | — | só despesas contratadas |
| `cd_municipio_fornecedor` | `CD_MUNICIPIO_FORNECEDOR` | texto | Código do município do fornecedor quando a esfera partidária do mesmo for municipal. | — | só despesas contratadas |
| `nm_municipio_fornecedor` | `NM_MUNICIPIO_FORNECEDOR` | texto | Município do fornecedor quando a esfera partidária do mesmo for municipal. | — | só despesas contratadas |
| `sq_candidato_fornecedor` | `SQ_CANDIDATO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata ou candidato, é o sequencial do mesmo gerado internamente pelos sistemas eleitorais. | — | só despesas contratadas |
| `nr_candidato_fornecedor` | `NR_CANDIDATO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata ou candidato, é o número do mesmo declarado pela candidata ou candidato prestador de contas. Este número é o número que aparece na urna e é fornecido pela Justiça Eleitoral. | — | só despesas contratadas |
| `cd_cargo_fornecedor` | `CD_CARGO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata ou candidato, é o código do cargo do mesmo declarado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `ds_cargo_fornecedor` | `DS_CARGO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata ou candidato, é o nome do cargo do mesmo declarado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `nr_partido_fornecedor` | `NR_PARTIDO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata, um candidato ou órgão partidário, é o número do partido do mesmo declarado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `sg_partido_fornecedor` | `SG_PARTIDO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata, um candidato ou órgão partidário, é a sigla do partido do mesmo declarado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `nm_partido_fornecedor` | `NM_PARTIDO_FORNECEDOR` | texto | Quando o fornecedor for uma candidata, um candidato ou órgão partidário, é o nome do partido do mesmo declarado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `ds_tipo_documento` | `DS_TIPO_DOCUMENTO` | texto | Tipo de documento apresentado para justificar a despesa contratada pela candidata ou candidato prestador de contas. Utilizado para categorizar os tipos de comprovantes que a candidata ou candidato arrecadou. | - Cupom Fiscal; - Duplicata; - Fatura; - Nota Fiscal; - RPA: Recibo de Pagamento; - Autônomo; - Recibo; - Outro. | só despesas contratadas, despesas pagas |
| `nr_documento` | `NR_DOCUMENTO` | texto | Número do documento de comprovação da despesa contratada declarada. | — | só despesas contratadas, despesas pagas |
| `cd_origem_despesa` | `CD_ORIGEM_DESPESA` | texto | Código de identificação do tipo de origem da despesa paga. É o código da conta DRD (Descrição de Receitas e Despesas) informado pela candidata ou candidato prestador de contas. | — | só despesas contratadas, despesas pagas |
| `ds_origem_despesa` | `DS_ORIGEM_DESPESA` | texto | Origem da despesa paga, conforme o código DRD informado pela candidata ou candidato prestador de contas. | — | só despesas contratadas, despesas pagas |
| `sq_despesa` | `SQ_DESPESA` | texto | Sequencial de identificação do registro da despesa contratada declarada pela candidata ou candidato prestador de contas, gerado internamente pelos sistemas eleitorais. | — | só despesas contratadas, despesas pagas |
| `dt_despesa` | `DT_DESPESA` | texto | Data da despesa contratada, declarada pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `ds_despesa` | `DS_DESPESA` | texto | Descrição da aplicabilidade da despesa contratada, informada pela candidata ou candidato prestador de contas. | — | só despesas contratadas, despesas pagas |
| `vr_despesa_contratada` | `VR_DESPESA_CONTRATADA` | texto | Valor da despesa contratada, em reais (R$), informado pela candidata ou candidato prestador de contas. | — | só despesas contratadas |
| `cd_fonte_despesa` | `CD_FONTE_DESPESA` | texto | Código do tipo de fonte de recursos da despesa paga declarada. | - 0- Fundo Partidário; - 1- Outros Recursos; - 2- Fundo Especial de Financiamento de Campanha; - 9- Não informado. | só despesas pagas |
| `ds_fonte_despesa` | `DS_FONTE_DESPESA` | texto | Fonte de recursos da despesa paga declarada. | — | só despesas pagas |
| `cd_natureza_despesa` | `CD_NATUREZA_DESPESA` | texto | Código da natureza de recursos da despesa paga pela candidata ou candidato prestador de contas. | - 0- Estimável; - 1- Financeiro. | só despesas pagas |
| `ds_natureza_despesa` | `DS_NATUREZA_DESPESA` | texto | Natureza de recursos da despesa paga declarada. | — | só despesas pagas |
| `cd_especie_recurso` | `CD_ESPECIE_RECURSO` | texto | Código de identificação da espécie de recurso utilizada no pagamento da despesa declarada pela candidata ou candidato prestador de contas. | - 0- Estimável; - 1- Financeiro. | só despesas pagas |
| `ds_especie_recurso` | `DS_ESPECIE_RECURSO` | texto | Espécie de recurso utilizada no pagamento da despesa declarada. | — | só despesas pagas |
| `sq_parcelamento_despesa` | `SQ_PARCELAMENTO_DESPESA` | texto | Sequencial de identificação do registro do pagamento da despesa declarada pela candidata ou candidato prestador de contas, gerado internamente pelos sistemas eleitorais. | — | só despesas pagas |
| `dt_pagto_despesa` | `DT_PAGTO_DESPESA` | texto | Data de pagamento da despesa paga declarada pela candidata ou candidato prestador de contas. | — | só despesas pagas |
| `vr_pagto_despesa` | `VR_PAGTO_DESPESA` | texto | Valor da despesa paga, em reais (R$), informado pela candidata ou candidato prestador de contas. | — | só despesas pagas |

## No lake

- Dataset `tse/prestacao-contas`, particionado por `ano` e `uf`, um Parquet por CSV de origem. O nome do Parquet guarda a família (`...__receitas_candidatos_2026_ac.parquet`), mas a família **não é uma coluna**.
- `ano` e `uf` vêm do nome do membro; o `BR` vai para `uf=br` e o `BRASIL` de uma família só é lido se o ZIP não tiver os arquivos por UF dessa mesma família (então vai para `uf=__HIVE_DEFAULT_PARTITION__`). A decisão é por família: `receitas_candidatos` e `receitas_candidatos_doador_originario` não se misturam.
- Todas as colunas são texto; valores em reais com vírgula decimal. Leitura em Latin-1 com campos entre aspas e quebra de linha; nas amostras o lake tem tantas linhas quanto registros no CSV (3.005, 474, 22.427 e 23.061 nos quatro membros do Acre de 2026).
- O esquema de referência (`prestacao-contas.schema.json`) tem 102 colunas, união das quatro famílias, gerado de uma conversão de amostras do Acre de 2026.

## Cuidados de uso

- **Dupla contagem (corrigida; lake gerado até a versão 0.3.3 ainda tem).** O ZIP traz um CSV por UF, o `BR` (registros de âmbito nacional, quando existe) e o `BRASIL` (consolidado que repete as UFs e o `BR`). O conversor atual não lê o `BRASIL` quando o ZIP tem os arquivos por UF: lê as UFs (`uf=<sigla>`) e o `BR` (`uf=br`, com `sg_uf` = `BR`); se o ZIP só tiver o `BRASIL`, ele é lido e vai para `uf=__HIVE_DEFAULT_PARTITION__`. Ao descartar o `BRASIL`, o conversor confere o número de linhas dele com a soma das UFs e do `BR`; se divergir, registra um aviso com as três contagens e mantém só as UFs e o `BR`. Assim somar o lake inteiro conta cada linha uma vez. Um lake gerado antes da correção tem os Parquets do `BRASIL` em `uf=__HIVE_DEFAULT_PARTITION__` e as linhas em dobro: apague `tse/prestacao-contas/` e reconverta (veja o `CHANGELOG.md`). Padrão de nomes conferido no ZIP de 2026: `<família>_2026_<UF>.csv`, `<família>_2026_BR.csv` e `<família>_2026_BRASIL.csv` para cada uma das quatro famílias. A contagem de linhas dos arquivos inteiros não foi conferida; a regra é a mesma dos outros datasets.
- **Quatro tabelas num dataset.** Receitas, doadores originários, despesas contratadas e despesas pagas têm colunas e significados diferentes, e o lake não grava a família numa coluna. Ao ler com `union_by_name`, identifique a família pela coluna preenchida (`vr_receita` só nas receitas e nos doadores originários, `vr_despesa_contratada`, `vr_pagto_despesa`) ou pelo nome do arquivo (`input_file_name`/`include_file_paths`). Somar `vr_receita` com as colunas de despesa mistura conceitos.
- **Despesa contratada não é despesa paga.** As duas famílias descrevem etapas diferentes do mesmo gasto; não as some.
- **Doador originário.** Cada linha dessa família refere-se a uma receita (`sq_receita`) e detalha quem deu o dinheiro originalmente; somar receitas e doadores originários conta a mesma verba duas vezes.
- **Marcadores da fonte ficam como texto, não viram nulo. Exemplos: o CPF do candidato vem `-4` e o do fornecedor pode vir `-1` nas amostras de 2026.
- **Valor em texto.** `vr_receita`, `vr_despesa_contratada` e `vr_pagto_despesa` usam vírgula decimal (`4000,00`).
- **Colunas sem descrição.** `cd_origem_despesa` e `ds_origem_despesa` existem nas despesas contratadas e pagas, mas o LEIAME das contratadas não as descreve (a descrição na tabela vem do LEIAME das pagas).

## Exemplos

Total de receitas de campanha de 2026 por partido, lendo só a família `receitas_candidatos` (o arquivo é escolhido pelo nome, já que a família não é coluna):

```python
import polars as pl

receitas = pl.scan_parquet(
    "lake/tse/prestacao-contas/ano=2026/*/*__receitas_candidatos_2026_*.parquet"
)
resumo = (
    receitas.with_columns(
        valor=pl.col("vr_receita").str.replace(",", ".").cast(pl.Float64)
    )
    .group_by("sg_partido")
    .agg(pl.col("valor").sum().alias("receitas_r$"))
    .sort("receitas_r$", descending=True)
    .collect()
)
```

## Referências

- Conjunto de 2024: https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2024 (há um por ano)
- Repositório de dados eleitorais (CDN): https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/
- Layout: `leiame_receitas-candidatos.pdf`, `leiame_receitas-candidatos-doador-originario.pdf`, `leiame_despesas-contratadas-candidatos.pdf` e `leiame_despesas-pagas-candidatos.pdf` dentro de cada ZIP
