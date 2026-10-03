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
    "receitas": DatasetSpec(
        key="receitas",
        name="Receitas de candidatos (prestação de contas)",
        prefix="receitas_candidato",
        first_year=2020,
        per_uf=True,
    ),
    "despesas": DatasetSpec(
        key="despesas",
        name="Despesas de candidatos (prestação de contas)",
        prefix="despesas_candidato",
        first_year=2020,
        per_uf=True,
    ),
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
