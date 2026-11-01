"""Convert raw TSE election data into the Hive Parquet lake.

Datasets in the Lake:
- ``candidatos``
- ``bens-candidatos``
- ``votacao-munzona``
- ``votacao-secao``
- ``detalhe-votacao-munzona``
- ``detalhe-votacao-secao``
- ``eleitorado``
- ``prestacao-contas``
- ``redes-sociais``
- ``motivo-cassacao``
- ``vagas``
- ``boletim-urna``
"""

from __future__ import annotations

import re
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    import duckdb
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.files import decompress_archive
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
        file_key,
        partition_types_for,
        select_current,
    )
except ImportError as exc:
    raise ImportError(
        "tse_fetcher.lake requer o extra 'analysis': "
        "uv add 'tse-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from tse_fetcher import __version__

SOURCE_ID = "tse"

ALL_DATASETS = [
    "candidatos",
    "bens-candidatos",
    "votacao-munzona",
    "votacao-secao",
    "detalhe-votacao-munzona",
    "detalhe-votacao-secao",
    "eleitorado",
    "prestacao-contas",
    "redes-sociais",
    "motivo-cassacao",
    "vagas",
    "boletim-urna",
]

_ALIASES: dict[str, str] = {
    "bens": "bens-candidatos",
    "votacao": "votacao-munzona",
    "prestacao_contas": "prestacao-contas",
    "prestacao_de_contas": "prestacao-contas",
    "prestacao_de_contas_eleitorais_candidatos": "prestacao-contas",
    "receitas": "prestacao-contas",
    "despesas": "prestacao-contas",
    "consulta_cand": "candidatos",
    "bem_candidato": "bens-candidatos",
    "votacao_candidato_munzona": "votacao-munzona",
    "votacao_secao": "votacao-secao",
    "detalhe_votacao_munzona": "detalhe-votacao-munzona",
    "detalhe_votacao_secao": "detalhe-votacao-secao",
    "perfil_eleitorado": "eleitorado",
    "redes_sociais_candidatos": "redes-sociais",
    "motivo_cassacao": "motivo-cassacao",
    "consulta_vagas": "vagas",
    "bweb": "boletim-urna",
    "boletim_urna": "boletim-urna",
    "boletim_de_urna": "boletim-urna",
}

_YEAR_RE = re.compile(r"[-_](?P<ano>(?:19|20)\d{2})(?:@|[_-]|\.|$|\b)")

VALID_UFS: frozenset[str] = frozenset(
    {
        "ac",
        "al",
        "ap",
        "am",
        "ba",
        "ce",
        "df",
        "es",
        "go",
        "ma",
        "mt",
        "ms",
        "mg",
        "pa",
        "pb",
        "pr",
        "pe",
        "pi",
        "rj",
        "rn",
        "rs",
        "ro",
        "rr",
        "sc",
        "sp",
        "se",
        "to",
        "zz",
        "br",
        "brasil",
    }
)


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def resolve_dataset(path: Path) -> str | None:
    """Infer canonical dataset id from parent directory or filename."""
    parent = path.parent.name.lower().replace("_", "-")
    if parent in ALL_DATASETS:
        return parent
    if parent in _ALIASES:
        return _ALIASES[parent]

    stem = path.stem.lower()
    for prefix, target in _ALIASES.items():
        if stem.startswith(prefix):
            return target
    for ds in ALL_DATASETS:
        if stem.startswith(ds.replace("-", "_")) or stem.startswith(ds):
            return ds
    return None


def resolve_partitions(path: Path) -> tuple[int | None, str]:
    """Extract integer ano and normalized uf from filename or path."""
    year_match = _YEAR_RE.search(path.name)
    ano = int(year_match["ano"]) if year_match else None
    if ano is None and path.parent.name.isdigit() and len(path.parent.name) == 4:
        ano = int(path.parent.name)

    # 1. First look for UF immediately following the year (e.g. _2022_SP or _2022-sp)
    if ano is not None:
        m_after_year = re.search(
            rf"{ano}[-_](?P<uf>[a-zA-Z]{{2}}|brasil|br)(?:@|[_-]|\.|$|\b)",
            path.name,
            re.IGNORECASE,
        )
        if m_after_year and m_after_year.group("uf").lower() in VALID_UFS:
            val = m_after_year.group("uf").lower()
            return ano, (
                "__HIVE_DEFAULT_PARTITION__" if val in {"brasil", "br"} else val
            )

    # 2. Otherwise scan tokens delimited by _ or - in reverse and check
    # against VALID_UFS
    tokens = re.split(r"[@_.\-\s]+", path.name)
    uf = "__HIVE_DEFAULT_PARTITION__"
    for token in reversed(tokens):
        val = token.lower()
        if val in VALID_UFS:
            uf = "__HIVE_DEFAULT_PARTITION__" if val in {"brasil", "br"} else val
            break

    return ano, uf


class LakeConverter:
    """Converter registered under the ``quantilica.lake`` entry point."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        """Dataset ids this converter writes to the lake."""
        return list(ALL_DATASETS)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        """Convert raw TSE files into ``lake_dir``.

        Args:
            input_dir: Root directory containing raw files.
            lake_dir: Root of the lake.
            datasets: Optional list of dataset ids to convert; None converts all.
            force: Reconvert even if sha256 already matches in the lake.

        Returns:
            ConvertResult: Files converted, skipped, and error messages.
        """
        input_dir = Path(input_dir)
        lake_dir = Path(lake_dir)
        result = ConvertResult()
        if not input_dir.is_dir():
            result.errors.append(f"diretório '{input_dir}' não existe")
            return result

        raw_allowed = set(datasets) if datasets else set(ALL_DATASETS)
        allowed: set[str] = set()
        for d in raw_allowed:
            canonical = _ALIASES.get(d, d)
            if canonical in ALL_DATASETS:
                allowed.add(canonical)
            else:
                result.errors.append(f"dataset desconhecido: {d}")
        if result.errors:
            return result

        candidates = sorted(
            p
            for p in input_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".csv", ".zip"}
        )

        current = set(
            select_current(p.relative_to(input_dir).as_posix() for p in candidates)
        )
        files = []
        for path in candidates:
            if path.relative_to(input_dir).as_posix() in current:
                files.append(path)
                continue
            ds = resolve_dataset(path)
            if ds and ds in allowed:
                result.skipped += 1

        writers: dict[str, LakeWriter] = {}

        for path in files:
            dataset_id = resolve_dataset(path)
            if not dataset_id or dataset_id not in allowed:
                continue

            part_keys = ["ano", "uf"]
            writer_key = f"{dataset_id}:" + ",".join(part_keys)
            if writer_key not in writers:
                writers[writer_key] = LakeWriter(
                    lake_dir / SOURCE_ID / dataset_id,
                    DatasetDescriptor(
                        source_id=SOURCE_ID,
                        dataset_id=dataset_id,
                        alias=dataset_id.replace("-", "_"),
                        partition_keys=part_keys,
                        partition_types=partition_types_for(part_keys),
                    ),
                    force=force,
                )
            writer = writers[writer_key]

            suffix = path.suffix.lower()
            try:
                if suffix == ".csv":
                    ano, uf = resolve_partitions(path)
                    if ano is None:
                        result.errors.append(
                            f"{path.name}: não foi possível inferir o ano"
                        )
                        continue
                    part_vals = {"ano": ano, "uf": uf}
                    key = file_key(path).lower()
                    written = writer.write_duckdb(
                        path,
                        partitions=part_vals,
                        file_key_name=key,
                        separator=";",
                        encoding="latin-1",
                        converter=f"tse-fetcher {__version__}",
                    )
                    if written.status == "skipped":
                        result.skipped += 1
                    else:
                        result.converted += 1

                elif suffix == ".zip":
                    with tempfile.TemporaryDirectory() as tmp:
                        extracted = decompress_archive(path, Path(tmp))
                        all_members = sorted(
                            m
                            for m in Path(tmp).rglob("*")
                            if m.is_file() and m.suffix.lower() in {".csv", ".txt"}
                        )
                        if not all_members and extracted.is_file():
                            all_members = [extracted]

                        if not all_members:
                            result.errors.append(
                                f"{path.name}: nenhum arquivo CSV encontrado"
                            )
                            continue

                        for member in all_members:
                            ano_m, uf_m = resolve_partitions(member)
                            ano_p, uf_p = resolve_partitions(path)
                            ano = ano_m if ano_m is not None else ano_p
                            uf = uf_m if uf_m != "__HIVE_DEFAULT_PARTITION__" else uf_p
                            if ano is None:
                                result.errors.append(
                                    f"{member.name}: não foi possível inferir o ano"
                                )
                                continue
                            part_vals = {"ano": ano, "uf": uf}
                            key = composite_file_key(path, member.stem).lower()
                            written = writer.write_duckdb(
                                member,
                                partitions=part_vals,
                                file_key_name=key,
                                src_origin=path,
                                separator=";",
                                encoding="latin-1",
                                converter=f"tse-fetcher {__version__}",
                            )
                            if written.status == "skipped":
                                result.skipped += 1
                            else:
                                result.converted += 1

            except (
                LakeError,
                OSError,
                zipfile.BadZipFile,
                duckdb.Error,
                Exception,
            ) as exc:
                message = str(exc).strip()
                first_line = message.splitlines()[0] if message else repr(exc)
                result.errors.append(f"{path.name}: {first_line}")
                continue

        return result


converter = LakeConverter()
