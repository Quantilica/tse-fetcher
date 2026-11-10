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

import logging
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

logger = logging.getLogger(__name__)

SOURCE_ID = "tse"

# Dialeto dos CSVs do TSE: campos entre aspas duplas, aspa interna dobrada e
# quebra de linha dentro do campo (descricao de bem, historico de prestacao de
# contas). DuckDB so le campo que atravessa linhas com uma thread.
_CSV_DIALECT = {
    "separator": ";",
    "encoding": "latin-1",
    "quote": '"',
    "escape": '"',
    "parallel": False,
}

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
    # nome com que a fonte publica o ZIP (``rede_social_candidato_<ano>.zip``)
    "rede_social_candidato": "redes-sociais",
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


#: Datasets cujo ZIP traz um CSV por UF, o ``BR`` (registros de âmbito nacional) e o
#: ``BRASIL`` (consolidado que repete as UFs e o ``BR``). Neles o ``BRASIL`` só é
#: lido se o ZIP não tiver os arquivos por UF, e o ``BR`` vai para ``uf=br``.
NACIONAL_DATASETS = frozenset(
    {"candidatos", "bens-candidatos", "votacao-munzona", "prestacao-contas"}
)

_DEFAULT_PARTITION = "__HIVE_DEFAULT_PARTITION__"

#: ``prestacao-contas`` reúne quatro tabelas de colunas diferentes; a partição
#: ``tabela`` as separa. Prefixo do nome do membro do ZIP -> valor da partição
#: (do mais específico ao mais geral: ``receitas_candidatos`` é prefixo de
#: ``receitas_candidatos_doador_originario``).
PRESTACAO_TABELAS: tuple[tuple[str, str], ...] = (
    ("receitas_candidatos_doador_originario", "doador-originario"),
    ("receitas_candidatos", "receitas"),
    ("despesas_contratadas_candidatos", "despesas-contratadas"),
    ("despesas_pagas_candidatos", "despesas-pagas"),
)


_ERRO_TABELA = (
    "{nome}: tabela da prestação de contas não reconhecida pelo prefixo do nome "
    "(esperado: receitas_candidatos, receitas_candidatos_doador_originario, "
    "despesas_contratadas_candidatos ou despesas_pagas_candidatos)"
)


def resolve_tabela(name: str) -> str | None:
    """Valor da partição ``tabela`` de um arquivo da prestação, ou ``None``."""
    low = name.lower()
    for prefixo, tabela in PRESTACAO_TABELAS:
        if low.startswith(prefixo + "_") or low == prefixo:
            return tabela
    return None


def _partitions(
    dataset_id: str, ano: int, uf: str, name: str
) -> dict[str, int | str] | None:
    """Partições do arquivo na ordem das chaves do dataset (``None`` se a tabela
    da prestação de contas não for reconhecida)."""
    if dataset_id != "prestacao-contas":
        return {"ano": ano, "uf": uf}
    tabela = resolve_tabela(name)
    if tabela is None:
        return None
    return {"ano": ano, "tabela": tabela, "uf": uf}


_MEMBER_UF_RE = re.compile(r"^(?P<base>.+?)[-_](?P<uf>[A-Za-z]{2}|brasil)$", re.I)


def redundant_brasil(members: list[Path]) -> dict[Path, list[Path]]:
    """Membros ``..._BRASIL`` de um ZIP que só repetem os arquivos por UF.

    Devolve ``{membro BRASIL: arquivos de UF e BR da mesma família}``. Os membros
    são agrupados pelo nome sem a UF final (uma família de arquivos:
    ``receitas_candidatos_2026`` não se mistura com ``despesas_pagas_candidatos_2026``).
    O ``BRASIL`` de uma família é redundante quando ela tem ao menos um arquivo de
    UF (qualquer sigla que não seja ``BR`` nem ``BRASIL``); sem arquivos por UF ele
    é a única cópia dos dados e não aparece no resultado.
    """
    por_familia: dict[str, dict[str, list[Path]]] = {}
    for member in members:
        m = _MEMBER_UF_RE.match(member.stem)
        if not m or m["uf"].lower() not in VALID_UFS:
            continue
        por_familia.setdefault(m["base"].lower(), {}).setdefault(
            m["uf"].lower(), []
        ).append(member)
    redundantes: dict[Path, list[Path]] = {}
    for ufs in por_familia.values():
        if not any(uf not in {"br", "brasil"} for uf in ufs):
            continue
        irmaos = [p for uf, ps in ufs.items() if uf != "brasil" for p in ps]
        for brasil in ufs.get("brasil", []):
            redundantes[brasil] = irmaos
    return redundantes


def _e_br(path: Path) -> bool:
    m = _MEMBER_UF_RE.match(path.stem)
    return bool(m) and m["uf"].lower() == "br"


def _conferir_brasil(zip_path: Path, brasil: Path, irmaos: list[Path]) -> None:
    """Registra no log por que o ``BRASIL`` não é lido e se ele bate com as UFs.

    O ``BRASIL`` nunca é lido quando há arquivos por UF (seria dupla contagem).
    Se o número de linhas dele diferir da soma das UFs e do ``BR`` da mesma
    família, o aviso traz as três contagens: a divergência fica visível e as UFs
    e o ``BR`` continuam sendo a fonte do lake.
    """
    n_brasil = count_csv_records(brasil)
    n_br = sum(count_csv_records(p) for p in irmaos if _e_br(p))
    n_ufs = sum(count_csv_records(p) for p in irmaos if not _e_br(p))
    if n_brasil == n_ufs + n_br:
        logger.info(
            "%s: %s não é lido: as %d linhas repetem as UFs (%d) e o BR (%d)",
            zip_path.name,
            brasil.name,
            n_brasil,
            n_ufs,
            n_br,
        )
        return
    logger.warning(
        "%s: %s não é lido e NÃO bate com os arquivos por UF: BRASIL tem %d linhas, "
        "as UFs somam %d e o BR tem %d (UFs + BR = %d); o lake fica com as UFs e o BR",
        zip_path.name,
        brasil.name,
        n_brasil,
        n_ufs,
        n_br,
        n_ufs + n_br,
    )


def count_csv_records(path: Path) -> int:
    """Linhas de dados de um CSV (sem o cabeçalho), sem carregá-lo na memória.

    Campos entre aspas podem ter quebra de linha: um registro só termina na
    quebra em que o número de aspas lidas até ali é par (``""`` conta duas).
    """
    registros = 0
    abertas = False
    with open(path, "rb") as f:
        for linha in f:
            if linha.count(b'"') % 2:
                abertas = not abertas
            if not abertas:
                registros += 1
    return max(registros - 1, 0)


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


def _uf_partition(val: str, br_partition: str) -> str:
    if val == "br":
        return br_partition
    return _DEFAULT_PARTITION if val == "brasil" else val


def resolve_partitions(
    path: Path, *, br_partition: str = _DEFAULT_PARTITION
) -> tuple[int | None, str]:
    """Extract integer ano and normalized uf from filename or path.

    ``BRASIL`` sempre cai em ``__HIVE_DEFAULT_PARTITION__``; ``BR`` cai na
    partição ``br_partition`` (a mesma, por padrão).
    """
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
            return ano, _uf_partition(val, br_partition)

    # 2. Otherwise scan tokens delimited by _ or - in reverse and check
    # against VALID_UFS
    tokens = re.split(r"[@_.\-\s]+", path.name)
    uf = "__HIVE_DEFAULT_PARTITION__"
    for token in reversed(tokens):
        val = token.lower()
        if val in VALID_UFS:
            uf = _uf_partition(val, br_partition)
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

            part_keys = (
                ["ano", "tabela", "uf"]
                if dataset_id == "prestacao-contas"
                else ["ano", "uf"]
            )
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
                    ano, uf = resolve_partitions(
                        path,
                        br_partition="br"
                        if dataset_id in NACIONAL_DATASETS
                        else _DEFAULT_PARTITION,
                    )
                    if ano is None:
                        result.errors.append(
                            f"{path.name}: não foi possível inferir o ano"
                        )
                        continue
                    part_vals = _partitions(dataset_id, ano, uf, path.name)
                    if part_vals is None:
                        result.errors.append(_ERRO_TABELA.format(nome=path.name))
                        continue
                    key = file_key(path).lower()
                    written = writer.write_duckdb(
                        path,
                        partitions=part_vals,
                        file_key_name=key,
                        converter=f"tse-fetcher {__version__}",
                        **_CSV_DIALECT,
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
                            if m.is_file()
                            and m.suffix.lower() in {".csv", ".txt"}
                            and not m.stem.lower().startswith(("leia", "readme"))
                        )
                        if not all_members and extracted.is_file():
                            all_members = [extracted]

                        if not all_members:
                            result.errors.append(
                                f"{path.name}: nenhum arquivo CSV encontrado"
                            )
                            continue

                        nacional = dataset_id in NACIONAL_DATASETS
                        repetidos = redundant_brasil(all_members) if nacional else {}
                        br_part = "br" if nacional else _DEFAULT_PARTITION
                        for member in all_members:
                            if member in repetidos:
                                _conferir_brasil(path, member, repetidos[member])
                                continue
                            ano_m, uf_m = resolve_partitions(
                                member, br_partition=br_part
                            )
                            ano_p, uf_p = resolve_partitions(path, br_partition=br_part)
                            ano = ano_m if ano_m is not None else ano_p
                            uf = uf_m if uf_m != "__HIVE_DEFAULT_PARTITION__" else uf_p
                            if ano is None:
                                result.errors.append(
                                    f"{member.name}: não foi possível inferir o ano"
                                )
                                continue
                            part_vals = _partitions(dataset_id, ano, uf, member.name)
                            if part_vals is None:
                                result.errors.append(
                                    _ERRO_TABELA.format(
                                        nome=f"{path.name}: {member.name}"
                                    )
                                )
                                continue
                            member_name = member.stem
                            key = composite_file_key(path, member_name).lower()
                            written = writer.write_duckdb(
                                member,
                                partitions=part_vals,
                                file_key_name=key,
                                src_origin=path,
                                converter=f"tse-fetcher {__version__}",
                                **_CSV_DIALECT,
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
