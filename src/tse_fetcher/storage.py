"""Storage layer for tse-fetcher datasets."""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from quantilica.core.storage import BaseDataRepository, build_stamped_filename

SOURCE_ID = "tse"

_PREFIX_TO_GROUP: dict[str, str] = {
    "consulta_cand": "candidatos",
    "bem_candidato": "bens-candidatos",
    "votacao_candidato_munzona": "votacao-munzona",
    "votacao_secao": "votacao-secao",
    "detalhe_votacao_munzona": "detalhe-votacao-munzona",
    "detalhe_votacao_secao": "detalhe-votacao-secao",
    "perfil_eleitorado": "eleitorado",
    "prestacao_de_contas_eleitorais_candidatos": "prestacao-contas",
    "prestacao_contas": "prestacao-contas",
    "redes_sociais_candidatos": "redes-sociais",
    "motivo_cassacao": "motivo-cassacao",
    "consulta_vagas": "vagas",
    "bweb": "boletim-urna",
}

_FILE_RE = re.compile(
    r"^(?P<prefix>.+?)_(?P<ano>(?:19|20)\d{2})(?:[_-](?P<uf>[a-zA-Z]{2}|brasil|br))?(?:@.*)?(?:\.zip)?$",
    re.IGNORECASE,
)


class DataRepository(BaseDataRepository):
    """Manages raw dataset files and manifests for tse-fetcher."""

    def __init__(self, root: Path | str) -> None:
        super().__init__(root)
        self.source_id = SOURCE_ID

    def path_for_entry(
        self,
        entry: Mapping[str, Any],
        *,
        last_modified: dt.date | dt.datetime | None = None,
    ) -> Path:
        """Compute local path for a TSE dataset entry.

        Layout: ``{output_dir}/{group}/{prefix}_{ano}[-{uf_lower}]@{YYYYMMDD}.zip``
        """
        raw_id = str(entry.get("id") or entry.get("filename") or "")
        ano = entry.get("ano") or entry.get("year")
        uf = entry.get("uf")
        prefix = entry.get("prefix") or entry.get("slug")
        group = entry.get("group") or entry.get("dataset")

        if (not ano or not prefix) and raw_id:
            m = _FILE_RE.match(Path(raw_id).name)
            if m:
                if not prefix:
                    prefix = m.group("prefix")
                if not ano:
                    ano = int(m.group("ano"))
                if not uf and m.group("uf"):
                    uf = m.group("uf")

        if not group:
            if prefix and prefix in _PREFIX_TO_GROUP:
                group = _PREFIX_TO_GROUP[prefix]
            elif prefix:
                group = prefix.replace("_", "-")
            else:
                group = "dados"
        else:
            group = str(group).replace("_", "-")

        if not prefix:
            prefix = group.replace("-", "_")

        parts: list[str] = []
        if ano is not None:
            parts.append(str(ano))
        if uf:
            parts.append(str(uf).lower())
        partition = "-".join(parts) if parts else None

        filename = build_stamped_filename(
            prefix,
            partition,
            ext="zip",
            timestamp=last_modified,
        )
        return self.dataset_path(group, filename)

    def path_for_dataset(
        self,
        dataset: str,
        ano: int,
        uf: str | None = None,
        *,
        last_modified: dt.date | dt.datetime | None = None,
        prefix: str | None = None,
    ) -> Path:
        """Helper to compute path given dataset, ano, and optional uf."""
        entry: dict[str, Any] = {
            "group": dataset,
            "prefix": prefix,
            "ano": ano,
            "uf": uf,
        }
        return self.path_for_entry(entry, last_modified=last_modified)
