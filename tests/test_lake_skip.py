"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from quantilica.analytics.lake import LakeWriter

import tse_fetcher.lake as lake_mod
from tse_fetcher.lake import converter

_CAND = "ano_eleicao;sg_uf;sq_candidato\n2022;{uf};{n}\n"


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    (raw / "votacao-munzona").mkdir(parents=True)
    (raw / "votacao-munzona" / "votacao_candidato_munzona_2022_RJ.csv").write_text(
        "ano_eleicao;sg_uf;qt_votos\n2022;RJ;5\n", encoding="latin-1"
    )
    (raw / "candidatos").mkdir()
    with zipfile.ZipFile(raw / "candidatos" / "consulta_cand_2022@1.zip", "w") as zf:
        zf.writestr("consulta_cand_2022_SP.csv", _CAND.format(uf="SP", n=1))
        zf.writestr("consulta_cand_2022_RJ.csv", _CAND.format(uf="RJ", n=2))
        zf.writestr("consulta_cand_2022_BRASIL.csv", _CAND.format(uf="BR", n=3))
    return raw


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Registra toda abertura/leitura do bruto: ZIP, extração, contagem, DuckDB."""
    vistas: list[str] = []

    def espia(nome: str, original):  # noqa: ANN001, ANN202
        def _f(*args, **kwargs):  # noqa: ANN002, ANN003
            vistas.append(nome)
            return original(*args, **kwargs)

        return _f

    monkeypatch.setattr(zipfile, "ZipFile", espia("zipfile", zipfile.ZipFile))
    monkeypatch.setattr(
        lake_mod, "decompress_archive", espia("extrai", lake_mod.decompress_archive)
    )
    monkeypatch.setattr(
        lake_mod, "count_csv_records", espia("conta", lake_mod.count_csv_records)
    )
    monkeypatch.setattr(
        LakeWriter, "_duckdb_convert", espia("duckdb", LakeWriter._duckdb_convert)
    )
    return vistas


@pytest.mark.parametrize(("dataset", "n"), [("votacao-munzona", 1), ("candidatos", 2)])
def test_segunda_rodada_nao_le_o_bruto(
    tmp_path: Path, leituras: list[str], dataset: str, n: int
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=[dataset])
    assert not res.errors, res.errors
    assert (res.converted, res.skipped) == (n, 0)
    assert leituras

    leituras.clear()
    res2 = converter.convert(raw, lake, datasets=[dataset])
    assert (res2.converted, res2.skipped, res2.errors) == (0, n, [])
    assert leituras == []


def test_force_reconverte_lendo_o_bruto(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["candidatos"])

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["candidatos"], force=True)
    assert (res.converted, res.skipped, res.errors) == (2, 0, [])
    assert "extrai" in leituras and "conta" in leituras


def test_zip_novo_e_convertido_e_o_resto_pulado(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["candidatos"])
    with zipfile.ZipFile(raw / "candidatos" / "consulta_cand_2018@2.zip", "w") as zf:
        zf.writestr("consulta_cand_2018_SP.csv", _CAND.format(uf="SP", n=9))

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["candidatos"])
    assert not res.errors, res.errors
    assert (res.converted, res.skipped) == (1, 2)
    assert leituras.count("extrai") == 1  # só o ZIP novo


def test_zip_alterado_com_o_mesmo_nome_e_reconvertido(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["candidatos"])
    with zipfile.ZipFile(raw / "candidatos" / "consulta_cand_2022@1.zip", "w") as zf:
        zf.writestr("consulta_cand_2022_SP.csv", _CAND.format(uf="SP", n=7))

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["candidatos"])
    assert not res.errors, res.errors
    assert res.converted == 1
    assert "extrai" in leituras
