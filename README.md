# tse-fetcher

Coletor de dados eleitorais do **TSE** (Tribunal Superior Eleitoral) — datasets
do CDN de estatísticas eleitorais ([ODSele](https://cdn.tse.jus.br/estatistica/sead/odsele/)):
candidatos, bens, votação por município/zona e prestação de contas (receitas e
despesas).

Parte do ecossistema [Quantilica](https://github.com/Quantilica).

## Instalação

Via hub Quantilica (recomendado):

```bash
quantilica install tse
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
| `receitas` | Receitas de campanha (prestação de contas) | `receitas_candidato` | 2020 | sim |
| `despesas` | Despesas de campanha (prestação de contas) | `despesas_candidato` | 2020 | sim |

## Uso como biblioteca

```python
from tse_fetcher import TseClient

client = TseClient()

# Metadados de um dataset
print(client.get_download_url("candidatos", 2022))
# https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2022.zip

# Download com validação de frescor, gravação atômica e manifest SHA-256
path = client.download("candidatos", 2022, output_dir="/data/tse")

# Receitas por UF (dataset per_uf)
path = client.download("receitas", 2022, uf="SP")
```

## CLI

O pacote expõe duas interfaces:

### CLI nativa (`tse-fetcher`, argparse — sem dependências de UI)

```bash
tse-fetcher --version
tse-fetcher list
tse-fetcher info candidatos
tse-fetcher sync -o /data/tse --years 2018:2026 --verbose
tse-fetcher sync bens votacao 2022
```

### Plugin do hub (`quantilica`, Typer + Rich)

```bash
quantilica tse list
quantilica tse info candidatos
quantilica tse sync -o /data/tse --years 2018:2026
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
