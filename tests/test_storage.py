"""Tests for DataRepository in tse-fetcher."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from tse_fetcher.storage import DataRepository


def test_storage_path_for_entry_explicit(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path / "tse")
    entry = {
        "group": "candidatos",
        "prefix": "consulta_cand",
        "ano": 2022,
    }
    path = repo.path_for_entry(entry)
    expected = tmp_path / "tse" / "candidatos" / "consulta_cand_2022.zip"
    assert path == expected


def test_storage_path_for_entry_with_stamp(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path / "tse")
    entry = {
        "group": "votacao-munzona",
        "prefix": "votacao_candidato_munzona",
        "ano": 2022,
        "uf": "SP",
    }
    stamp = dt.date(2026, 8, 14)
    path = repo.path_for_entry(entry, last_modified=stamp)
    expected = (
        tmp_path
        / "tse"
        / "votacao-munzona"
        / "votacao_candidato_munzona_2022-sp@20260814.zip"
    )
    assert path == expected


def test_storage_path_for_entry_from_id(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path / "tse")
    entry = {"id": "consulta_cand_2022.zip"}
    path = repo.path_for_entry(entry)
    expected = tmp_path / "tse" / "candidatos" / "consulta_cand_2022.zip"
    assert path == expected


def test_storage_path_for_dataset_helper(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path / "tse")
    path = repo.path_for_dataset(
        "bens-candidatos",
        2024,
        prefix="bem_candidato",
        last_modified=dt.date(2024, 10, 1),
    )
    expected = tmp_path / "tse" / "bens-candidatos" / "bem_candidato_2024@20241001.zip"
    assert path == expected
