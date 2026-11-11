# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.5.0] - 2026-11-11

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).

### Corrigido
- `sync` (com ou sem `--from-plan`) não sai mais com código 0 quando algum arquivo falha: sai com `3` se parte dos arquivos baixou e parte falhou, com `1` se nada baixou e com `0` sem falhas, o mesmo contrato do `sync` dos demais fetchers.

## [0.4.0] - 2026-11-10

### Adicionado
- `docs/`: documentação dos dados conforme a norma, com uma página por dataset (12) e o esquema de referência dos quatro que o fetcher baixa e converte (`candidatos`, `bens-candidatos`, `votacao-munzona` e `prestacao-contas`). Os oito restantes ficam como `so-bruto`: o conversor os reconhece, mas o fetcher não os baixa. `tests/test_docs.py` verifica a pasta.

### Corrigido
- `lake`: `candidatos`, `bens-candidatos`, `votacao-munzona` e `prestacao-contas` não contam mais as linhas em dobro. O ZIP traz um CSV por UF, o `BR` (registros de âmbito nacional, como a eleição presidencial) e o `BRASIL` (consolidado que repete as UFs e o `BR`), e o conversor lia todos. Agora o `BRASIL` só é lido quando o ZIP não tem arquivos por UF (na prestação de contas a decisão é por família de arquivos); quando é descartado, o conversor confere o número de linhas dele com a soma das UFs e do `BR` e, se divergir, registra um aviso com as três contagens (o lake fica com as UFs e o `BR`). O descartado não conta em `skipped`. O `BR` vai para a partição `uf=br`, também em CSV avulso (antes ia, com o `BRASIL`, para `uf=__HIVE_DEFAULT_PARTITION__`). Nos arquivos conferidos de 2018, `candidatos` passa de 58.574 para 29.287 linhas e `bens-candidatos` de 187.054 para 93.527 (as UFs mais o `BR`). Os demais datasets não mudam.
- `lake`: o ZIP de redes sociais, publicado pela fonte como `rede_social_candidato_<ano>.zip`, passa a ser reconhecido como `redes-sociais` (o nome antigo `redes_sociais_candidatos` continua valendo). O mesmo vale para a pasta de destino do bruto.

**Como reconverter.** O `BRASIL` deixa de ser lido e o `BR` muda de partição, e o conversor só remove Parquets com a mesma chave de arquivo; uma reconversão, mesmo com `--force`, deixaria os Parquets antigos e as linhas continuariam em dobro. Antes de reconverter, apague do lake as pastas dos datasets afetados:

- `tse/candidatos/`
- `tse/bens-candidatos/`
- `tse/votacao-munzona/`
- `tse/prestacao-contas/`

Depois converta de novo esses datasets. Os outros datasets (`votacao-secao`, `detalhe-votacao-munzona`, `detalhe-votacao-secao`, `eleitorado`, `motivo-cassacao`, `vagas`, `boletim-urna`) não precisam ser refeitos.

### Alterado
- **Mudança incompatível em `prestacao-contas`:** o dataset ganha a partição `tabela`, e as chaves de partição passam de `[ano, uf]` para `[ano, tabela, uf]` (`ano=2026/tabela=receitas/uf=ac/`). O id do dataset não muda. As quatro tabelas do ZIP, que tinham colunas diferentes e se misturavam num esquema de 102 colunas, agora ficam em partições próprias, derivadas do prefixo do nome do membro: `receitas_candidatos` (`receitas`), `receitas_candidatos_doador_originario` (`doador-originario`), `despesas_contratadas_candidatos` (`despesas-contratadas`) e `despesas_pagas_candidatos` (`despesas-pagas`). Cada partição tem só as suas colunas (60, 23, 53 e 28). Membro com prefixo desconhecido não é convertido e aparece nos erros do resultado. O esquema de referência continua sendo a união das colunas (102). Quem lia o dataset deve passar a filtrar por `tabela`.

**Como reconverter `prestacao-contas`.** Apague a pasta `tse/prestacao-contas/` do lake (a mesma que a correção da dupla contagem já pedia apagar) e converta o dataset de novo; as pastas antigas `ano=<ano>/uf=<uf>/` não são removidas por uma reconversão.

## [0.3.3] - 2026-11-07

### Corrigido
- `lake`: campos entre aspas com quebra de linha dentro (descrição de bem do candidato, textos da prestação de contas) encerravam o registro no meio e a conversão falhava com `CSV Error on Line`. Agora o CSV é lido com aspas duplas como delimitador e escape, e a quebra fica preservada no valor. A leitura desses arquivos passa a usar uma thread só.

## [0.3.2] - 2026-11-06

### Corrigido
- Anos eleitorais deixam de ser uma lista fixa até 2026: são calculados a partir da data (o ano par seguinte, como 2028, entra quando chegar), sem mudar os ids atuais.
- `lake`: arquivos de documentação dentro dos ZIPs (`LEIAME*`, `readme*`) não são lidos como dados.

## [0.3.1] - 2026-11-04

### Corrigido
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install tse --extra analysis`), sem traceback.

### Alterado
- O diretório de saída padrão (`/data/tse`) passa a ser declarado explicitamente no plugin; o valor não muda.

## [0.3.0] - 2026-11-04

### Corrigido
- Política de frescor volta a F1 (`HEAD_OR_MANIFEST`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.

### Alterado
- Exige `quantilica-core>=0.16.0`.

## [0.2.0] - 2026-10-20

### Adicionado
- Comandos `quantilica tse check --out <path>` e `sync --from-plan` para plano de download determinístico e integração com pipelines de carga.
- Suporte a `sync --force` para forçar download mesmo quando arquivos locais existem.

### Alterado
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com código 1 e orienta `quantilica install tse`.
- Datasets `receitas` e `despesas` substituídos por `prestacao_contas` (arquivo nacional consolidado de receitas e despesas de candidatos): o TSE removeu do CDN os arquivos particionados por UF (ex: `despesas_candidato_2020_RJ.zip` → HTTP 404, centenas de falhas em execuções agendadas diárias). Nomes legados continuam aceitos como aliases no `.get_dataset`/`plan_sync`/`sync`/`download`, deduplicados para um único download nacional.
- `DatasetSpec` ganha campo `path` (diretório remoto no CDN independente do prefixo do arquivo) para acomodar o novo layout `prestacao_contas`.

### Corrigido
- Sync completo (`quantilica tse sync`) não gera mais 404 em massa: todas as 19 URLs do plano padrão 2018–2026 verificadas como HTTP 200 no CDN.

## [0.1.0] - 2026-10-05

### Adicionado
- Versão inicial do coletor de dados eleitorais do TSE (Tribunal Superior Eleitoral).
- `constants.py`: URL base do CDN ODSele, 5 datasets (`candidatos`, `bens`, `votacao`, `receitas`, `despesas`), anos eleitorais 1994–2026 e siglas de UF.
- `client.py`: `TseClient` com `list_datasets()`, `get_download_url()`, `download()` (gravação atômica + manifest SHA-256 via `quantilica-core`), `sync()` bulk tolerante a falhas e `plan_sync()` com dataclass `SyncPlanItem`.
- Flag `--dry-run` no comando `sync` (CLI nativa e plugin Typer/Rich com pré-visualização em tabela Rich).
- Integração ao ecossistema via `FetcherApp` (`quantilica.cli.sdk`) com thin wrapper em `cli.py` e entry points `tse-fetcher` e `quantilica tse`.
