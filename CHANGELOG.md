# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

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
