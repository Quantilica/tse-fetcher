"""Cliente HTTP para o CDN de estatísticas eleitorais do TSE."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from quantilica.core.http import HttpClient, is_remote_more_recent

from .constants import (
    BASE_URL,
    DATASETS,
    DEFAULT_OUTPUT,
    ELECTION_YEARS,
    PRODUCER,
    SOURCE_ID,
    UFS,
    DatasetSpec,
)

DONE_CALLBACK = Callable[[str, str], None]

__all__ = ["DONE_CALLBACK", "SyncPlanItem", "TseClient"]


@dataclass(frozen=True)
class SyncPlanItem:
    """Item de um plano de sincronização (pré-visualização de download)."""

    dataset: str
    dataset_name: str
    ano: int
    uf: str | None
    filename: str
    url: str
    target: Path


class TseClient:
    """Cliente para download de datasets do ODSele (TSE)."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 120.0,
        attempts: int = 3,
        transport=None,
    ) -> None:
        """Inicializar o cliente.

        Args:
            base_url (str): URL base do CDN do TSE.
            timeout (float): Timeout das requisições em segundos.
            attempts (int): Número de tentativas por requisição.
            transport (httpx2.BaseTransport | None): Transporte customizado
                (usado em testes). Defaults to None.
        """
        self.base_url = base_url.rstrip("/")
        self.http = HttpClient(timeout=timeout, attempts=attempts, transport=transport)

    def list_datasets(self) -> list[DatasetSpec]:
        """Listar os datasets suportados.

        Returns:
            list[DatasetSpec]: Especificações disponíveis.
        """
        return sorted(DATASETS.values(), key=lambda spec: spec.key)

    def get_dataset(self, dataset: str) -> DatasetSpec:
        """Resolver um dataset pelo nome canônico.

        Args:
            dataset (str): Nome canônico do dataset (ex: 'candidatos').

        Returns:
            DatasetSpec: A especificação correspondente.

        Raises:
            ValueError: Se o dataset não existir.
        """
        spec = DATASETS.get(dataset)
        if spec is None:
            known = ", ".join(sorted(DATASETS))
            msg = f"Dataset desconhecido: {dataset!r}. Suportados: {known}"
            raise ValueError(msg)
        return spec

    def get_download_url(self, dataset: str, ano: int, uf: str | None = None) -> str:
        """Montar a URL de download de um dataset.

        Args:
            dataset (str): Nome canônico do dataset.
            ano (int): Ano eleitoral.
            uf (str | None): Sigla da UF (apenas para datasets per_uf).
                Defaults to None.

        Returns:
            str: URL de download do arquivo ZIP.

        Raises:
            ValueError: Se dataset, ano ou UF forem inválidos.
        """
        spec = self.get_dataset(dataset)
        _validar_ano(spec, ano)
        _validar_uf(uf)
        if uf is not None and not spec.per_uf:
            msg = f"Dataset {dataset!r} não aceita UF (arquivo nacional único)."
            raise ValueError(msg)
        filename = _filename(spec, ano, uf)
        return f"{self.base_url}/{spec.prefix}/{filename}"

    def download(
        self,
        dataset: str,
        ano: int,
        uf: str | None = None,
        output_dir: Path | str = DEFAULT_OUTPUT,
        force: bool = False,
    ) -> Path:
        """Baixar um dataset com verificação de frescor e manifest SHA-256.

        Gravação atômica com sidecar de proveniência SHA-256 via
        ``HttpClient.download_with_manifest``.

        Args:
            dataset (str): Nome canônico do dataset.
            ano (int): Ano eleitoral.
            uf (str | None): Sigla da UF (datasets per_uf). Defaults to None.
            output_dir (Path | str): Diretório de saída. Defaults to "/data/tse".
            force (bool): Baixar mesmo se o arquivo local estiver fresco.

        Returns:
            Path: Caminho do arquivo gravado.

        Raises:
            ValueError: Se dataset/ano/UF forem inválidos.
        """
        spec = self.get_dataset(dataset)
        url = self.get_download_url(dataset, ano, uf)
        suffix = f"_{uf}" if uf else ""
        dataset_id = f"{spec.key}_{ano}{suffix}"
        target = Path(output_dir) / _filename(spec, ano, uf)
        return self.http.download_with_manifest(
            url,
            target,
            source_id=SOURCE_ID,
            dataset_id=dataset_id,
            producer=PRODUCER,
            force=force,
        )

    def plan_sync(
        self,
        datasets: list[str],
        anos: list[int],
        output_dir: Path | str = DEFAULT_OUTPUT,
    ) -> tuple[list[SyncPlanItem], int]:
        """Planejar a sincronização sem tocar na rede ou gravar em disco.

        Calcula a lista ordenada de arquivos elegíveis e a contagem de
        pares (dataset, ano) ignorados — fora dos anos eleitorais ou
        anteriores ao primeiro ano coberto pelo dataset.

        Args:
            datasets (list[str]): Nomes canônicos de datasets.
            anos (list[int]): Anos eleitorais desejados.
            output_dir (Path | str): Diretório de saída.

        Returns:
            tuple[list[SyncPlanItem], int]: Itens planejados e pares
                ignorados.

        Raises:
            ValueError: Se algum dataset for desconhecido.
        """
        specs = {dataset: self.get_dataset(dataset) for dataset in datasets}

        items: list[SyncPlanItem] = []
        skipped = 0
        output = Path(output_dir)
        for spec in specs.values():
            for ano in anos:
                if ano not in ELECTION_YEARS or ano < spec.first_year:
                    skipped += 1
                    continue
                if spec.per_uf:
                    items.extend(_plan_item(self, spec, ano, uf, output) for uf in UFS)
                else:
                    items.append(_plan_item(self, spec, ano, None, output))
        return items, skipped

    def sync(
        self,
        datasets: list[str],
        anos: list[int],
        output_dir: Path | str = DEFAULT_OUTPUT,
        force: bool = False,
        on_done: DONE_CALLBACK | None = None,
        dry_run: bool = False,
    ) -> tuple[int, int, int]:
        """Baixar vários datasets/anos com tolerância a falhas por item.

        Valida os datasets antes de iniciar (dataset desconhecido aborta).
        Anos fora da cobertura eleitoral do dataset são filtrados e
        reportados como ``skipped``; falhas de rede em um arquivo não
        interrompem o restante.

        Args:
            datasets (list[str]): Nomes canônicos de datasets.
            anos (list[int]): Anos eleitorais desejados.
            output_dir (Path | str): Diretório de saída.
            force (bool): Forçar re-download.
            on_done (DONE_CALLBACK | None): Callback por arquivo —
                ``(filename, result)`` com ``result`` em
                ``{"ok", "failed", "skipped"}``.
            dry_run (bool): Planejar sem executar downloads; retorna
                imediatamente ``(0, 0, skipped)``.

        Returns:
            tuple[int, int, int]: (downloads OK, falhas, pares ignorados).

        Raises:
            ValueError: Se algum dataset for desconhecido.
        """
        if dry_run:
            items, skipped = self.plan_sync(datasets, anos, output_dir)
            if on_done is not None:
                for item in items:
                    on_done(item.filename, "skipped")
                if skipped:
                    on_done("pares ignorados fora da cobertura do dataset", "skipped")
            return 0, 0, skipped

        items, skipped = self.plan_sync(datasets, anos, output_dir)
        ok, failed = self.download_items(items, output_dir, force, on_done)
        if skipped and on_done is not None:
            on_done("pares ignorados fora da cobertura do dataset", "skipped")
        return ok, failed, skipped

    def download_items(
        self,
        items: list[SyncPlanItem],
        output_dir: Path | str = DEFAULT_OUTPUT,
        force: bool = False,
        on_done: DONE_CALLBACK | None = None,
    ) -> tuple[int, int]:
        """Baixar itens já planejados, com tolerância a falhas por item.

        Args:
            items: Itens de plano (ex.: vindos de ``plan_sync`` ou de um
                plano de checagem filtrado).
            output_dir: Diretório de saída (recalcula o destino a partir do
                nome canônico do arquivo).
            force: Forçar re-download.
            on_done: Callback por arquivo — ``(filename, result)``.

        Returns:
            tuple[int, int]: (downloads OK, falhas).
        """
        ok = failed = 0
        for item in items:
            ok_one, failed_one = self._download_one(
                item.dataset, item.ano, item.uf, output_dir, force
            )
            ok += ok_one
            failed += failed_one
            if on_done is not None:
                on_done(item.filename, "ok" if ok_one else "failed")
        return ok, failed

    def check_item(self, item: SyncPlanItem) -> dict:
        """Verificar frescor de um item planejado sem baixar.

        Faz HEAD na URL e compara contra o arquivo local usando o mesmo
        predicado de freshness do download.

        Args:
            item: Item de plano de sincronização.

        Returns:
            dict: Veredicto com as chaves de ``CheckPlanItem`` do SDK mais
                ``entry`` (reconstruível para download posterior).
        """
        base = {
            "dataset": item.dataset,
            "id": item.filename,
            "url": item.url,
            "partition": str(item.ano) + (f"-{item.uf}" if item.uf else ""),
            "local_path": str(item.target),
            "entry": {
                "id": item.filename,
                "url": item.url,
                "dataset": item.dataset,
                "ano": item.ano,
                "uf": item.uf,
                "filename": item.filename,
            },
        }
        try:
            head = self.http.head(item.url)
        except Exception as exc:
            return {
                **base,
                "remote_etag": None,
                "remote_last_modified": None,
                "remote_size": None,
                "local_exists": item.target.exists(),
                "action": "download",
                "reason": f"metadata-unavailable: {exc}",
            }
        try:
            size = int(head.headers.get("Content-Length") or 0) or None
        except (TypeError, ValueError):
            size = None
        exists = item.target.exists()
        if exists and not is_remote_more_recent(head, item.target):
            action, reason = "skip-up-to-date", "local-fresh"
        else:
            action = "download"
            reason = "not-present" if not exists else "remote-newer"
        return {
            **base,
            "remote_etag": head.headers.get("ETag"),
            "remote_last_modified": head.headers.get("Last-Modified"),
            "remote_size": size,
            "local_exists": exists,
            "action": action,
            "reason": reason,
        }

    def _download_one(
        self,
        dataset: str,
        ano: int,
        uf: str | None,
        output_dir: Path | str,
        force: bool,
    ) -> tuple[int, int]:
        """Executar um download individual, capturando qualquer exceção.

        Returns:
            tuple[int, int]: (1, 0) em sucesso; (0, 1) em falha.
        """
        try:
            self.download(dataset, ano, uf, output_dir=output_dir, force=force)
        except Exception:
            return 0, 1
        return 1, 0


def _plan_item(
    client: TseClient,
    spec: DatasetSpec,
    ano: int,
    uf: str | None,
    output_dir: Path,
) -> SyncPlanItem:
    """Montar um SyncPlanItem para o par (dataset, ano, UF).

    Args:
        client (TseClient): Cliente base (para resolver a URL).
        spec (DatasetSpec): Especificação do dataset.
        ano (int): Ano eleitoral.
        uf (str | None): Sigla da UF, se houver.
        output_dir (Path): Diretório de saída.

    Returns:
        SyncPlanItem: Item prontinho para download/preview.
    """
    filename = _filename(spec, ano, uf)
    return SyncPlanItem(
        dataset=spec.key,
        dataset_name=spec.name,
        ano=ano,
        uf=uf,
        filename=filename,
        url=client.get_download_url(spec.key, ano, uf),
        target=output_dir / filename,
    )


def _filename(spec: DatasetSpec, ano: int, uf: str | None) -> str:
    """Montar o nome canônico do arquivo ZIP.

    Args:
        spec (DatasetSpec): Especificação do dataset.
        ano (int): Ano eleitoral.
        uf (str | None): Sigla da UF, se houver.

    Returns:
        str: Nome do arquivo (ex: 'consulta_cand_2022.zip').
    """
    if uf is not None:
        return f"{spec.prefix}_{ano}_{uf}.zip"
    return f"{spec.prefix}_{ano}.zip"


def _validar_ano(spec: DatasetSpec, ano: int) -> None:
    """Validar ano eleitoral para o dataset.

    Args:
        spec (DatasetSpec): Especificação do dataset.
        ano (int): Ano a validar.

    Raises:
        ValueError: Se o ano não for eleitoral ou for anterior ao primeiro
            ano coberto pelo dataset.
    """
    if ano not in ELECTION_YEARS:
        msg = (
            f"Ano eleitoral inválido: {ano}. "
            f"Válidos: {ELECTION_YEARS[0]}–{ELECTION_YEARS[-1]}"
        )
        raise ValueError(msg)
    if ano < spec.first_year:
        msg = f"Dataset {spec.key!r} não cobre o ano {ano} (início {spec.first_year})."
        raise ValueError(msg)


def _validar_uf(uf: str | None) -> None:
    """Validar sigla de UF.

    Args:
        uf (str | None): Sigla a validar; None é aceito.

    Raises:
        ValueError: Se a UF informada não existir.
    """
    if uf is not None and uf not in UFS:
        msg = f"UF inválida ou inexistente: {uf!r}."
        raise ValueError(msg)
