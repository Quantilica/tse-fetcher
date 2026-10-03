# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Adicionado
- Flag `--dry-run` no comando `sync` (CLI nativa e plugin Typer/Rich),
  conforme `docs/docs/normas/cli-fetchers.md` §9: pré-visualiza o plano de
  download — datasets particionados por UF (`receitas`, `despesas`) geram 27
  arquivos por ano eleitoral — sem tocar na rede nem gravar em disco.
- `client.py`: dataclass imutável `SyncPlanItem` (dataset, dataset_name, ano,
  uf, filename, url, target), método `TseClient.plan_sync()` que calcula os
  arquivos elegíveis e os pares (dataset, ano) ignorados fora da cobertura,
  e parâmetro opcional `dry_run` em `TseClient.sync()` (retorna
  `(0, 0, skipped)`). `SyncPlanItem` exportado no `__init__` do pacote.
- CLI nativa: saída textual `[dataset] ano UF -> filename (URL)` com linha de
  sumário (total planejado + pares ignorados).
- Plugin Typer/Rich: pré-visualização em `Rich Table` (colunas Dataset, Ano,
  UF, Arquivo, URL) com sumário via `console.print`.
- Documentação formal da degradação graciosa do plugin para a CLI nativa
  (argparse) quando `typer` não está disponível.

### Alterado
- `README.md`: instalação prioriza o fluxo canônico `quantilica install tse`
  (índice estático PEP 503) e documenta `uv sync` para o ambiente de
  desenvolvimento; exemplos com `--dry-run`.

## [0.1.0] - 2026-10-02

### Adicionado
- Scaffold do pacote `tse-fetcher` (padrão fetcher Quantilica: `cli.py` argparse + `plugin.py` Typer).
- `constants.py`: URL base do CDN ODSele, 5 datasets (`candidatos`, `bens`, `votacao`, `receitas`, `despesas`), anos eleitorais 1994–2026 e siglas de UF.
- `client.py`: `TseClient` com `list_datasets()`, `get_download_url()`, `download()` (gravação atômica + manifest SHA-256 via `quantilica-core`) e `sync()` bulk tolerante a falhas.
- CLI nativa (argparse) com subcomandos `list`, `sync`, `info`.
- Plugin Typer para `quantilica-cli` com imports graciosos de typer/rich (fallback argparse nativo).
