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
    assert res.converted == 2
    assert res.skipped == 0  # o BRASIL descartado não conta como "já no lake"
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

    brasil_part = lake_dir / "tse" / "candidatos" / "ano=2022"
    assert [p.name for p in brasil_part.iterdir()] == ["uf=sp"]

    desc_cand = DatasetDescriptor.load(lake_dir / "tse" / "candidatos")
    assert desc_cand.partition_types == {"ano": "int", "uf": "varchar"}
    assert not check_dataset(lake_dir / "tse" / "candidatos")

    # Idempotent second run
    res2 = lake_converter.convert(raw_dir, lake_dir)
    assert res2.converted == 0
    assert res2.skipped == 2


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


def test_quebra_de_linha_dentro_de_aspas(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    """Descricao de bem com quebra de linha entre aspas continua um registro so."""
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"
    bens_dir = raw_dir / "bens-candidatos"
    bens_dir.mkdir(parents=True)
    linhas = ['"ANO_ELEICAO";"SG_UF";"DS_BEM_CANDIDATO";"VR_BEM_CANDIDATO"']
    # muitas linhas simples antes, para o erro nao depender da amostra do sniffer
    linhas += [f'2022;"RN";"BEM {i}";"1,00"' for i in range(3000)]
    linhas += ['2022;"RN";"APTO EM ED. MOACYR MAIA,\nAV. APODI, 500";"122259,61"']
    linhas += ['2022;"RN";"CASA COM ""VARANDA""";"10,00"']
    zip_path = bens_dir / "bem_candidato_2022@20261106.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("bem_candidato_2022_RN.csv", "\n".join(linhas).encode("latin-1"))

    res = lake_converter.convert(raw_dir, lake_dir)
    assert not res.errors, res.errors
    assert res.converted == 1
    (parquet,) = (lake_dir / "tse" / "bens-candidatos").rglob("*.parquet")
    df = pl.read_parquet(parquet)
    assert df.height == 3002
    descr = df["ds_bem_candidato"].to_list()
    assert descr[-2] == "APTO EM ED. MOACYR MAIA,\nAV. APODI, 500"
    assert descr[-1] == 'CASA COM "VARANDA"'


def _zip_com(path: Path, membros: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        for nome, conteudo in membros.items():
            zf.writestr(nome, conteudo)


def _linhas(lake: Path, dataset: str) -> pl.DataFrame:
    return pl.read_parquet(
        lake / "tse" / dataset / "**" / "*.parquet", hive_partitioning=True
    )


def test_brasil_nao_e_lido_quando_o_zip_tem_as_ufs(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    """``BRASIL`` repete as UFs e o ``BR``; ler os três contava tudo em dobro."""
    cab = "ano_eleicao;sg_uf;sq_candidato\n"
    _zip_com(
        tmp_path / "raw" / "candidatos" / "consulta_cand_2018.zip",
        {
            "consulta_cand_2018_AC.csv": cab + "2018;AC;1\n",
            "consulta_cand_2018_SP.csv": cab + "2018;SP;2\n2018;SP;3\n",
            "consulta_cand_2018_BR.csv": cab + "2018;BR;4\n",
            "consulta_cand_2018_BRASIL.csv": cab
            + "2018;AC;1\n2018;SP;2\n2018;SP;3\n2018;BR;4\n",
        },
    )
    lake = tmp_path / "lake"
    res = lake_converter.convert(tmp_path / "raw", lake)
    assert not res.errors, res.errors
    assert res.converted == 3
    assert res.skipped == 0  # o BRASIL descartado não conta como "já no lake"
    df = _linhas(lake, "candidatos")
    assert df.height == 4
    assert sorted(df["sq_candidato"].to_list()) == ["1", "2", "3", "4"]
    ds = lake / "tse" / "candidatos" / "ano=2018"
    assert sorted(p.name for p in ds.iterdir()) == ["uf=ac", "uf=br", "uf=sp"]
    assert not list(ds.rglob("*brasil*"))
    assert not check_dataset(lake / "tse" / "candidatos")


def test_brasil_e_lido_quando_o_zip_so_tem_ele(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    cab = "ano_eleicao;sq_candidato\n"
    _zip_com(
        tmp_path / "raw" / "bens-candidatos" / "bem_candidato_2024.zip",
        {"bem_candidato_2024_BRASIL.csv": cab + "2024;1\n2024;2\n"},
    )
    lake = tmp_path / "lake"
    res = lake_converter.convert(tmp_path / "raw", lake)
    assert (res.converted, res.skipped, res.errors) == (1, 0, [])
    ds = lake / "tse" / "bens-candidatos" / "ano=2024"
    assert [p.name for p in ds.iterdir()] == ["uf=__HIVE_DEFAULT_PARTITION__"]
    assert _linhas(lake, "bens-candidatos").height == 2


def test_prestacao_decide_o_brasil_por_familia_de_arquivos(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    """Cada família (receitas, despesas...) tem o seu ``BRASIL``."""
    _zip_com(
        tmp_path
        / "raw"
        / "prestacao-contas"
        / ("prestacao_de_contas_eleitorais_candidatos_2026.zip"),
        {
            "receitas_candidatos_2026_AC.csv": "sq_receita\n1\n",
            "receitas_candidatos_2026_BR.csv": "sq_receita\n2\n",
            "receitas_candidatos_2026_BRASIL.csv": "sq_receita\n1\n2\n",
            # família sem arquivos por UF: o BRASIL é a única cópia
            "despesas_pagas_candidatos_2026_BRASIL.csv": "sq_despesa\n7\n8\n",
        },
    )
    lake = tmp_path / "lake"
    res = lake_converter.convert(tmp_path / "raw", lake)
    assert not res.errors, res.errors
    assert (res.converted, res.skipped) == (3, 0)
    df = _linhas_uniao(lake, "prestacao-contas")
    assert df["sq_receita"].drop_nulls().sort().to_list() == ["1", "2"]
    assert df["sq_despesa"].drop_nulls().sort().to_list() == ["7", "8"]


def _linhas_uniao(lake: Path, dataset: str) -> pl.DataFrame:
    arquivos = sorted((lake / "tse" / dataset).rglob("*.parquet"))
    return pl.concat([pl.read_parquet(a) for a in arquivos], how="diagonal")


def test_brasil_de_dataset_fora_da_lista_continua_sendo_lido(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    cab = "ano_eleicao;qt_votos\n"
    _zip_com(
        tmp_path / "raw" / "votacao-secao" / "votacao_secao_2022.zip",
        {
            "votacao_secao_2022_SP.csv": cab + "2022;1\n",
            "votacao_secao_2022_BRASIL.csv": cab + "2022;1\n",
        },
    )
    res = lake_converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.skipped, res.errors) == (2, 0, [])


def test_redes_sociais_aceita_o_nome_publicado_pela_fonte() -> None:
    novo = Path("/data/tse/rede_social_candidato_2024.zip")
    antigo = Path("/data/tse/redes_sociais_candidatos_2024.zip")
    assert resolve_dataset(novo) == "redes-sociais"
    assert resolve_dataset(antigo) == "redes-sociais"
    assert resolve_dataset(Path("/data/tse/redes-sociais/x_2024.zip")) == (
        "redes-sociais"
    )


def test_redes_sociais_converte_o_zip_com_o_nome_da_fonte(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    _zip_com(
        tmp_path / "raw" / "rede_social_candidato_2024.zip",
        {"rede_social_candidato_2024_BRASIL.csv": "sq_candidato;ds_url\n1;x\n"},
    )
    res = lake_converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (1, [])
    assert _linhas(tmp_path / "lake", "redes-sociais").height == 1


def test_resolve_partitions_br_so_muda_quando_pedido() -> None:
    p = Path("consulta_cand_2018_BR.csv")
    assert resolve_partitions(p) == (2018, "__HIVE_DEFAULT_PARTITION__")
    assert resolve_partitions(p, br_partition="br") == (2018, "br")
    brasil = Path("consulta_cand_2018_BRASIL.csv")
    assert resolve_partitions(brasil, br_partition="br") == (
        2018,
        "__HIVE_DEFAULT_PARTITION__",
    )


def test_contagem_de_registros_respeita_quebra_de_linha_entre_aspas(
    tmp_path: Path,
) -> None:
    from tse_fetcher.lake import count_csv_records

    arq = tmp_path / "x.csv"
    arq.write_bytes(
        b'"a";"b"\n"1";"linha um\nlinha dois"\n"2";"com ""aspas"""\n"3";"fim"\n'
    )
    assert count_csv_records(arq) == 3


def _zip_candidatos(raw: Path, brasil: str) -> None:
    cab = "ano_eleicao;sg_uf;sq_candidato\n"
    _zip_com(
        raw / "candidatos" / "consulta_cand_2018.zip",
        {
            "consulta_cand_2018_AC.csv": cab + "2018;AC;1\n",
            "consulta_cand_2018_SP.csv": cab + "2018;SP;2\n2018;SP;3\n",
            "consulta_cand_2018_BR.csv": cab + "2018;BR;4\n",
            "consulta_cand_2018_BRASIL.csv": cab + brasil,
        },
    )


def test_brasil_que_bate_com_as_ufs_e_descartado_sem_aviso(
    tmp_path: Path, lake_converter: LakeConverter, caplog
) -> None:
    _zip_candidatos(tmp_path / "raw", "2018;AC;1\n2018;SP;2\n2018;SP;3\n2018;BR;4\n")
    with caplog.at_level("INFO"):
        res = lake_converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.skipped, res.errors) == (3, 0, [])
    assert "NÃO bate" not in caplog.text
    assert "repetem as UFs (3) e o BR (1)" in caplog.text


def test_brasil_que_nao_bate_avisa_com_as_tres_contagens(
    tmp_path: Path, lake_converter: LakeConverter, caplog
) -> None:
    # o BRASIL tem uma linha a mais do que UFs + BR
    _zip_candidatos(
        tmp_path / "raw", "2018;AC;1\n2018;SP;2\n2018;SP;3\n2018;BR;4\n2018;ZZ;9\n"
    )
    with caplog.at_level("WARNING"):
        res = lake_converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.skipped, res.errors) == (3, 0, [])
    assert "NÃO bate" in caplog.text
    assert "BRASIL tem 5 linhas" in caplog.text
    assert "as UFs somam 3 e o BR tem 1" in caplog.text
    # sem dupla contagem: só UFs e BR no lake
    assert _linhas(tmp_path / "lake", "candidatos").height == 4


def test_csv_avulso_do_br_vai_para_uf_br(
    tmp_path: Path, lake_converter: LakeConverter
) -> None:
    d = tmp_path / "raw" / "candidatos"
    d.mkdir(parents=True)
    (d / "consulta_cand_2018_BR.csv").write_text(
        "ano_eleicao;sg_uf;sq_candidato\n2018;BR;4\n", encoding="latin-1"
    )
    res = lake_converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (1, [])
    ds = tmp_path / "lake" / "tse" / "candidatos" / "ano=2018"
    assert [p.name for p in ds.iterdir()] == ["uf=br"]
