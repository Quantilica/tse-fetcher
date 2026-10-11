"""Constantes do TSE (Tribunal Superior Eleitoral).

Datasets no CDN de estatísticas eleitorais (SEAD/ODSele).
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"
SOURCE_ID = "tse"
PRODUCER = "Tribunal Superior Eleitoral"

DEFAULT_OUTPUT = "/data/tse"
DEFAULT_YEAR_RANGE = "2018:2026"


@dataclass(frozen=True)
class DatasetSpec:
    """Especificação de um dataset do ODSele."""

    key: str
    name: str
    prefix: str
    first_year: int
    per_uf: bool = False
    # Diretório remoto no CDN; None usa ``prefix`` (padrão ODSele antigo,
    # em que diretório e prefixo de arquivo coincidem).
    path: str | None = None


DATASETS: dict[str, DatasetSpec] = {
    "candidatos": DatasetSpec(
        key="candidatos",
        name="Candidatos (consulta_cand)",
        prefix="consulta_cand",
        first_year=1994,
    ),
    "bens": DatasetSpec(
        key="bens",
        name="Bens de candidatos (bem_candidato)",
        prefix="bem_candidato",
        first_year=2006,
    ),
    "votacao": DatasetSpec(
        key="votacao",
        name="Votação nominal por município e zona (votacao_candidato_munzona)",
        prefix="votacao_candidato_munzona",
        first_year=1996,
    ),
    # Desde 2020 o TSE unificou receitas e despesas num arquivo nacional
    # único por ano (o portal "Prestação de Contas Eleitorais"); os antigos
    # arquivos per_uf (ex: despesas_candidato_2020_RJ.zip) foram removidos
    # do CDN e retornam 404.
    "prestacao_contas": DatasetSpec(
        key="prestacao_contas",
        name="Prestação de contas eleitorais de candidatos (receitas e despesas)",
        prefix="prestacao_de_contas_eleitorais_candidatos",
        path="prestacao_contas",
        first_year=2020,
    ),
}

# Nomes legados aceitos em get_dataset/plan_sync/sync/download e resolvidos
# para o dataset consolidado (compatibilidade com scripts e crons antigos).
# Não fazem parte do catálogo (list/list_datasets/sync sem argumento).
ALIASES: dict[str, str] = {
    "receitas": "prestacao_contas",
    "despesas": "prestacao_contas",
}

# Anos eleitorais: eleições federais (par) e municipais (ímpar) desde 1994.
ELECTION_YEARS: tuple[int, ...] = tuple(range(1994, 2027, 2))

UFS: tuple[str, ...] = (
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
)
