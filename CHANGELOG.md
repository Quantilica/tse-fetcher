# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Alterado
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com código 1 e orienta `quantilica install tse`.
- Datasets `receitas` e `despesas` substituídos por `prestacao_contas` (arquivo nacional consolidado de receitas e despesas de candidatos): o TSE removeu do CDN os arquivos particionados por UF (ex: `despesas_candidato_2020_RJ.zip` → HTTP 404, centenas de falhas no cron diário). Nomes legados continuam aceitos como aliases no `.get_dataset`/`plan_sync`/`sync`/`download`, deduplicados para um único download nacional.
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
