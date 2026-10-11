"""Testes das constantes do tse-fetcher."""

from tse_fetcher.constants import (
    ALIASES,
    BASE_URL,
    DATASETS,
    ELECTION_YEARS,
    UFS,
    DatasetSpec,
)


def test_base_url() -> None:
    """A URL base aponta para o CDN de estatísticas do TSE."""
    assert BASE_URL == "https://cdn.tse.jus.br/estatistica/sead/odsele"


def test_datasets_obrigatorios() -> None:
    """Os quatro datasets canônicos estão presentes."""
    assert set(DATASETS) == {"candidatos", "bens", "votacao", "prestacao_contas"}


def test_prestacao_contas_segue_padrao_nacional_do_tse() -> None:
    """Dataset consolidado segue o padrão atual do CDN (nacional, 2020+)."""
    spec = DATASETS["prestacao_contas"]
    assert spec.path == "prestacao_contas"
    assert spec.prefix == "prestacao_de_contas_eleitorais_candidatos"
    assert spec.first_year == 2020
    assert spec.per_uf is False


def test_aliases_legados() -> None:
    """Nomes legados mapeiam para o dataset consolidado."""
    assert ALIASES == {"receitas": "prestacao_contas", "despesas": "prestacao_contas"}


def test_datasets_sao_especificacoes() -> None:
    """Cada valor de DATASETS é um DatasetSpec com prefixo."""
    for key, spec in DATASETS.items():
        assert isinstance(spec, DatasetSpec)
        assert spec.key == key
        assert spec.name
        assert spec.prefix


def test_primeiro_ano_salto_maior_que_ano_2010() -> None:
    """Datasets de prestação de contas começam em 2020; demais antes de 2010."""
    assert all(DATASETS[k].first_year < 2010 for k in ("candidatos", "bens", "votacao"))
    assert DATASETS["prestacao_contas"].first_year >= 2020


def test_anos_eleitorais() -> None:
    """Anos eleitorais são pares desde 1994 e incluem 2022."""
    assert ELECTION_YEARS[0] == 1994
    assert 2022 in ELECTION_YEARS
    assert all(ano % 2 == 0 for ano in ELECTION_YEARS)


def test_ufs() -> None:
    """As 26 UFs + DF estão presentes, sem duplicatas."""
    assert len(UFS) == 27
    assert len(set(UFS)) == 27
    assert "SP" in UFS
    assert "DF" in UFS
