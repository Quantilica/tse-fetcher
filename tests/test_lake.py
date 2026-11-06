"""Tests for the TSE Parquet Lake converter."""

from __future__ import annotations

import zipfile
from pathlib import Path

import polars as pl
import pytest
from quantilica.analytics.lake import check_dataset
from quantilica.core.lake import DatasetDescriptor

from tse_fetcher.lake import LakeConverter, resolve_dataset, resolve_partitions


@pytest.fixture
def lake_converter() -> LakeConverter:
    return LakeConverter()


def test_datasets_list(lake_converter: LakeConverter) -> None:
    ds = lake_converter.datasets()
    assert "candidatos" in ds
    assert "bens-candidatos" in ds
    assert "votacao-munzona" in ds
    assert "votacao-secao" in ds
    assert "prestacao-contas" in ds


def test_resolve_dataset_and_partitions() -> None:
    p1 = Path("/data/tse/candidatos/consulta_cand_2022.zip")
    assert resolve_dataset(p1) == "candidatos"
    ano1, uf1 = resolve_partitions(p1)
    assert ano1 == 2022
    assert uf1 == "__HIVE_DEFAULT_PARTITION__"

    p2 = Path(
        "/data/tse/votacao-munzona/votacao_candidato_munzona_2022-sp@20260814.zip"
    )
    assert resolve_dataset(p2) == "votacao-munzona"
    ano2, uf2 = resolve_partitions(p2)
    assert ano2 == 2022
    assert uf2 == "sp"

    p3 = Path("/data/tse/votacao_candidato_munzona_2020_BRASIL.csv")
    assert resolve_dataset(p3) == "votacao-munzona"
    ano3, uf3 = resolve_partitions(p3)
    assert ano3 == 2020
    assert uf3 == "__HIVE_DEFAULT_PARTITION__"

    p4 = Path("/data/tse/prestacao_de_contas_eleitorais_candidatos_2022_SP.zip")
    assert resolve_dataset(p4) == "prestacao-contas"
    ano4, uf4 = resolve_partitions(p4)
    assert ano4 == 2022
    assert uf4 == "sp"

    p5 = Path("/data/tse/boletim_de_urna_2022_SP.csv")
    assert resolve_dataset(p5) == "boletim-urna"
    ano5, uf5 = resolve_partitions(p5)
    assert ano5 == 2022
    assert uf5 == "sp"


def test_convert_csv_and_zip(tmp_path: Path, lake_converter: LakeConverter) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    # 1. Plain CSV in votacao-munzona
    vm_dir = raw_dir / "votacao-munzona"
    vm_dir.mkdir(parents=True)
    csv_file = vm_dir / "votacao_candidato_munzona_2022_RJ.csv"
    csv_file.write_text(
        "ano_eleicao;sg_uf;cd_cargo;nm_urna_candidato;qt_votos_nominais\n"
        "2022;RJ;1;Candidato A;500\n"
        "2022;RJ;1;Candidato B;300\n",
        encoding="latin-1",
    )

    # 2. Zipped national candidates with multiple state CSVs
    cand_dir = raw_dir / "candidatos"
    cand_dir.mkdir(parents=True)
    zip_path = cand_dir / "consulta_cand_2022@20240101.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(
            "consulta_cand_2022_SP.csv",
            "ano_eleicao;sg_uf;sq_candidato;nm_candidato\n2022;SP;1001;Nome SP\n",
        )
        zf.writestr(
            "consulta_cand_2022_BRASIL.csv",
            "ano_eleicao;sg_uf;sq_candidato;nm_candidato\n2022;BR;1002;Nome Brasil\n",
        )

    res = lake_converter.convert(raw_dir, lake_dir)
    assert res.converted == 3
    assert res.skipped == 0
    assert not res.errors

    # Verify votacao-munzona partition and descriptor
    vm_parquet = (
        lake_dir
        / "tse"
        / "votacao-munzona"
        / "ano=2022"
        / "uf=rj"
        / "votacao_candidato_munzona_2022_rj.parquet"
    )
    assert vm_parquet.is_file()
    df_vm = pl.read_parquet(vm_parquet)
    assert df_vm.shape == (2, 5)

    desc_vm = DatasetDescriptor.load(lake_dir / "tse" / "votacao-munzona")
    assert desc_vm.partition_types == {"ano": "int", "uf": "varchar"}
    assert not check_dataset(lake_dir / "tse" / "votacao-munzona")

    # Verify candidatos state and national partitions
    sp_part = (
        lake_dir
        / "tse"
        / "candidatos"
        / "ano=2022"
        / "uf=sp"
        / "consulta_cand_2022__consulta_cand_2022_sp.parquet"
    )
    assert sp_part.is_file()

    br_part = (
        lake_dir
        / "tse"
        / "candidatos"
        / "ano=2022"
        / "uf=__HIVE_DEFAULT_PARTITION__"
        / "consulta_cand_2022__consulta_cand_2022_brasil.parquet"
    )
    assert br_part.is_file()

    desc_cand = DatasetDescriptor.load(lake_dir / "tse" / "candidatos")
    assert desc_cand.partition_types == {"ano": "int", "uf": "varchar"}
    assert not check_dataset(lake_dir / "tse" / "candidatos")

    # Idempotent second run
    res2 = lake_converter.convert(raw_dir, lake_dir)
    assert res2.converted == 0
    assert res2.skipped == 3


def test_convert_errors(tmp_path: Path, lake_converter: LakeConverter) -> None:
    non_existent = tmp_path / "does_not_exist"
    res = lake_converter.convert(non_existent, tmp_path / "lake")
    assert "não existe" in res.errors[0]

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    res_unknown = lake_converter.convert(
        raw_dir, tmp_path / "lake", datasets=["invalid-dataset"]
    )
    assert "dataset desconhecido: invalid-dataset" in res_unknown.errors[0]


def test_zip_inherits_uf_partition(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    secao_dir = raw_dir / "votacao-secao"
    secao_dir.mkdir(parents=True)
    zip_path = secao_dir / "votacao_secao_2022-sp@20260814.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Member name does not contain SP
        zf.writestr(
            "votacao_secao.csv",
            "ano_eleicao;cd_cargo;qt_votos\n2022;1;150\n",
        )

    res = lake_converter.convert(raw_dir, lake_dir)
    assert res.converted == 1
    assert not res.errors

    sp_parquet = (
        lake_dir
        / "tse"
        / "votacao-secao"
        / "ano=2022"
        / "uf=sp"
        / "votacao_secao_2022-sp__votacao_secao.parquet"
    )
    assert sp_parquet.is_file()


def test_zip_ignora_leiame_txt(tmp_path: Path, lake_converter: LakeConverter) -> None:
    """Documentacao (LEIAME.txt) no ZIP nao vira membro de dados."""
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"
    secao_dir = raw_dir / "votacao-secao"
    secao_dir.mkdir(parents=True)
    zip_path = secao_dir / "votacao_secao_2022-sp@20260814.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("votacao_secao.csv", "ano_eleicao;cd_cargo;qt_votos\n2022;1;150\n")
        zf.writestr("LEIAME.txt", "Descricao dos campos\n")

    res = lake_converter.convert(raw_dir, lake_dir)
    assert res.converted == 1
    assert not res.errors
