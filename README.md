# tse-fetcher

Coletor de dados eleitorais do **TSE** (Tribunal Superior Eleitoral) — datasets
do CDN de estatísticas eleitorais ([ODSele](https://cdn.tse.jus.br/estatistica/sead/odsele/)):
candidatos, bens, votação por município/zona e prestação de contas (receitas e
despesas).

Parte do ecossistema [Quantilica](https://github.com/Quantilica).

## Instalação

Via hub Quantilica (recomendado — distribuído pelo índice estático PEP 503):

```bash
quantilica install tse
```

Para contribuir no repositório (ambiente de desenvolvimento do workspace):

```bash
uv sync
```

O pacote também roda standalone — traz apenas `quantilica-core`
(sem versões leves de typer/rich):

```bash
uv add tse-fetcher
```

## Datasets suportados

| Chave | Conteúdo | Prefixo do arquivo | Primeiro ano | Por UF |
|---|---|---|---|---|
| `candidatos` | Candidaturas (consulta_cand) | `consulta_cand` | 1994 | não |
| `bens` | Bens declarados por candidato | `bem_candidato` | 2006 | não |
| `votacao` | Votação nominal por município/zona | `votacao_candidato_munzona` | 1996 | não |
| `prestacao_contas` | Receitas e despesas de campanha (prestação de contas) | `prestacao_de_contas_eleitorais_candidatos` | 2020 | não |

Todos os datasets usam um arquivo nacional único por ano. Desde 2020 o TSE
unificou receitas e despesas de candidatos no portal "Prestação de Contas
Eleitorais"; os antigos arquivos particionados por UF (`receitas_candidato`,
`despesas_candidato`) foram **removidos do CDN** (404). Os nomes legados
`receitas` e `despesas` continuam aceitos como aliases de `prestacao_contas`
(mas não aparecem no catálogo nem no sync completo). Use `--dry-run` para
pré-visualizar o volume antes de baixar.

## Uso como biblioteca

```python
from tse_fetcher import TseClient

client = TseClient()

# Metadados de um dataset
print(client.get_download_url("candidatos", 2022))
# https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2022.zip

# Download com validação de frescor, gravação atômica e manifest SHA-256
path = client.download("candidatos", 2022, output_dir="/data/tse")

# Prestação de contas consolidada (receitas e despesas, arquivo nacional;
# aliases legados 'receitas' e 'despesas' também são aceitos)
path = client.download("prestacao_contas", 2022, output_dir="/data/tse")

# Pré-visualizar um plano de sync sem tocar na rede
items, skipped = client.plan_sync(["prestacao_contas"], [2022])
print(len(items), skipped)  # 1 arquivo nacional, 0 pares ignorados
```

## CLI

O pacote expõe uma CLI unificada (Typer + Rich via `FetcherApp` de
`quantilica.cli.sdk`), usada tanto pelo entry point `tse-fetcher` quanto pelo
plugin do hub (`quantilica tse`):

```bash
tse-fetcher list
tse-fetcher info candidatos
tse-fetcher sync -o /data/tse -y 2018:2026 --verbose
tse-fetcher sync bens votacao -y 2022

# Pré-visualizar o que seria baixado, sem tocar na rede (tabela Rich):
tse-fetcher sync --dry-run
tse-fetcher sync prestacao_contas -y 2022:2026 --dry-run
```

Verbos `sync` (download, idempotente e tudo por padrão), `list` (catálogo
remoto) e `info` (metadados de um dataset) seguem o vocabulário canônico de
fetchers do ecossistema.

## Proveniência

Todo download garante gravação atômica + um sidecar de manifesto com `sha256`,
URL final, tamanho e timestamps (`quantilica-core.DownloadManifest`).

## Histórico de mudanças

Veja [CHANGELOG.md](CHANGELOG.md).

## Licença

MIT — veja [LICENSE](LICENSE).
