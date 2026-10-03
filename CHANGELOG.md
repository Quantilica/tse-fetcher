# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-10-02

### Adicionado
- Scaffold do pacote `tse-fetcher` (padrão fetcher Quantilica: `cli.py` argparse + `plugin.py` Typer).
- `constants.py`: URL base do CDN ODSele, 5 datasets (`candidatos`, `bens`, `votacao`, `receitas`, `despesas`), anos eleitorais 1994–2026 e siglas de UF.
- `client.py`: `TseClient` com `list_datasets()`, `get_download_url()`, `download()` (gravação atômica + manifest SHA-256 via `quantilica-core`) e `sync()` bulk tolerante a falhas.
- CLI nativa (argparse) com subcomandos `list`, `sync`, `info`.
- Plugin Typer para `quantilica-cli` com imports graciosos de typer/rich (fallback argparse nativo).
