"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest
import quantilica.core.manifests as manifests_mod
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
    _sidecars(raw)
    return raw


def _sidecars(raiz: Path) -> None:
    """Sidecar ``.manifest.json`` com o sha256 de cada bruto, como o fetcher grava:
    o hash do bruto sai dele, sem ler o arquivo."""
    for f in sorted(raiz.rglob("*")):
        if f.is_file() and not f.name.endswith(".manifest.json"):
            Path(f"{f}.manifest.json").write_text(
                json.dumps(
                    {
                        "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                        "size_bytes": f.stat().st_size,
                    }
                ),
                encoding="utf-8",
            )


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[str]:
    """Registra toda abertura/leitura do bruto: ZIP, extração, contagem, DuckDB,
    abertura de arquivo do bruto (menos o sidecar, lido de propósito) e hash por
    leitura."""
    vistas: list[str] = []
    raiz = str(tmp_path / "raw")

    def do_bruto(arquivo) -> bool:  # noqa: ANN001
        nome = str(arquivo)
        return nome.startswith(raiz) and not nome.endswith(".manifest.json")

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
    monkeypatch.setattr(
        manifests_mod, "sha256_file", espia("hash", manifests_mod.sha256_file)
    )

    original_open = builtins.open
    original_io_open = io.open
    original_path_open = Path.open

    def open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(file):
            vistas.append(f"open:{file}")
        return original_open(file, *args, **kwargs)

    def io_open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(file):
            vistas.append(f"io.open:{file}")
        return original_io_open(file, *args, **kwargs)

    def path_open_espiado(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(self):
            vistas.append(f"Path.open:{self}")
        return original_path_open(self, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espiado)
    monkeypatch.setattr(io, "open", io_open_espiado)
    monkeypatch.setattr(Path, "open", path_open_espiado)
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
    _sidecars(raw)

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
    _sidecars(raw)

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["candidatos"])
    assert not res.errors, res.errors
    assert res.converted == 1
    assert "extrai" in leituras


def test_sem_sidecar_o_espiao_de_hash_dispara(
    tmp_path: Path, leituras: list[str]
) -> None:
    # Prova de que o espião funciona: sem sidecar o bruto é hasheado lendo-o.
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["candidatos"])
    for sidecar in raw.rglob("*.manifest.json"):
        sidecar.unlink()
    leituras.clear()
    converter.convert(raw, lake, datasets=["candidatos"])
    assert "hash" in leituras


def test_zip_interrompido_completa_na_rodada_seguinte(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Falha no segundo membro na rodada 1; a 2 completa; a 3 pula sem ler o bruto."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    escrever = LakeWriter.write_duckdb

    def falha_no_rj(self, src, *a, **kw):  # noqa: ANN001, ANN002, ANN003, ANN202
        if str(src).endswith("_SP.csv"):
            raise RuntimeError("disco cheio")
        return escrever(self, src, *a, **kw)

    with monkeypatch.context() as m:
        m.setattr(LakeWriter, "write_duckdb", falha_no_rj)
        r1 = converter.convert(raw, lake, datasets=["candidatos"])
    # members vêm ordenados (RJ antes de SP): RJ grava, SP falha
    assert (r1.converted, r1.skipped, len(r1.errors)) == (1, 0, 1)

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r2.converted, r2.skipped, r2.errors) == (1, 1, [])
    assert leituras

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r3.converted, r3.skipped, r3.errors) == (0, 2, [])
    assert leituras == []


def test_lake_sem_declaracao_reconverte_uma_vez_e_depois_pula(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    with monkeypatch.context() as m:  # lake gravado antes da declaração
        escrever = LakeWriter.write_duckdb

        def sem_decl(self, *a, **kw):  # noqa: ANN001, ANN002, ANN003, ANN202
            kw.pop("origin_outputs", None)
            return escrever(self, *a, **kw)

        m.setattr(LakeWriter, "write_duckdb", sem_decl)
        r0 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r0.converted, r0.skipped) == (2, 0)

    r1 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r1.converted, r1.skipped, r1.errors) == (2, 0, [])

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert leituras == []


def _raw_prestacao(tmp_path: Path, membros: list[str]) -> Path:
    raw = tmp_path / "raw"
    (raw / "prestacao-contas").mkdir(parents=True)
    with zipfile.ZipFile(
        raw / "prestacao-contas" / "prestacao_de_contas_eleitorais_2022@1.zip", "w"
    ) as zf:
        for nome in membros:
            zf.writestr(nome, "ano_eleicao;sg_uf;valor\n2022;SP;1\n")
    _sidecars(raw)
    return raw


def test_erro_deterministico_de_membro_volta_a_cada_build(tmp_path: Path) -> None:
    # Tabela não reconhecida pelo prefixo: erro de nome que o main reporta sempre.
    raw = _raw_prestacao(
        tmp_path, ["receitas_candidatos_2022_SP.csv", "tabela_estranha_2022_SP.csv"]
    )
    lake = tmp_path / "lake"
    r1 = converter.convert(raw, lake, datasets=["prestacao-contas"])
    r2 = converter.convert(raw, lake, datasets=["prestacao-contas"])
    assert (r1.converted, len(r1.errors)) == (1, 1)
    assert (r2.converted, r2.skipped, len(r2.errors)) == (0, 1, 1)
    assert "tabela da prestação" in r2.errors[0]


def test_zip_sem_erro_de_nome_pula_sem_ler(tmp_path: Path, leituras: list[str]) -> None:
    raw = _raw_prestacao(
        tmp_path,
        ["receitas_candidatos_2022_SP.csv", "despesas_pagas_candidatos_2022_SP.csv"],
    )
    lake = tmp_path / "lake"
    r1 = converter.convert(raw, lake, datasets=["prestacao-contas"])
    assert (r1.converted, r1.errors) == (2, [])
    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["prestacao-contas"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert leituras == []


def _tags_do_lake(lake: Path) -> set[str]:
    import pyarrow.parquet as pq

    return {
        pq.read_metadata(f).metadata[b"quantilica.converter"].decode()
        for f in (lake / "tse" / "candidatos").rglob("*.parquet")
    }


def test_revisao_do_layout_diferente_reconverte_o_zip(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Outra ``LAKE_LAYOUT_REVISION`` no rodapé: o ZIP é aberto e regravado (e o
    rodapé passa à nova revisão); com a mesma, pula sem ler o bruto."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    r1 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r1.converted, r1.skipped, r1.errors) == (2, 0, [])
    rev = lake_mod.LAKE_LAYOUT_REVISION
    assert _tags_do_lake(lake) == {f"tse-fetcher layout-{rev}"}

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert leituras == []

    monkeypatch.setattr(lake_mod, "LAKE_LAYOUT_REVISION", rev + 1)
    r3 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r3.converted, r3.skipped, r3.errors) == (2, 0, [])
    assert leituras
    assert _tags_do_lake(lake) == {f"tse-fetcher layout-{rev + 1}"}

    leituras.clear()
    r4 = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r4.converted, r4.skipped, r4.errors) == (0, 2, [])
    assert leituras == []


def test_versao_do_pacote_nao_reconverte(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["candidatos"])
    monkeypatch.setattr(lake_mod, "__version__", "99.0.0")
    leituras.clear()
    r = converter.convert(raw, lake, datasets=["candidatos"])
    assert (r.converted, r.skipped, r.errors) == (0, 2, [])
    assert leituras == []
