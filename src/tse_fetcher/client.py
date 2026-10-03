"""Cliente HTTP para o CDN de estatísticas eleitorais do TSE."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from quantilica.core.http import HttpClient

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

    def sync(
        self,
        datasets: list[str],
        anos: list[int],
        output_dir: Path | str = DEFAULT_OUTPUT,
        force: bool = False,
        on_done: DONE_CALLBACK | None = None,
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

        Returns:
            tuple[int, int, int]: (downloads OK, falhas, pares ignorados).

        Raises:
            ValueError: Se algum dataset for desconhecido.
        """
        specs = {dataset: self.get_dataset(dataset) for dataset in datasets}

        members: list[tuple[DatasetSpec, int, str | None]] = []
        skipped = 0
        for spec in specs.values():
            for ano in anos:
                if ano not in ELECTION_YEARS or ano < spec.first_year:
                    skipped += 1
                    continue
                if spec.per_uf:
                    members.extend((spec, ano, uf) for uf in UFS)
                else:
                    members.append((spec, ano, None))

        ok = failed = 0
        for spec, ano, uf in members:
            filename = _filename(spec, ano, uf)
            ok_one, failed_one = self._download_one(
                spec.key, ano, uf, output_dir, force
            )
            ok += ok_one
            failed += failed_one
            if on_done is not None:
                on_done(filename, "ok" if ok_one else "failed")
        if skipped and on_done is not None:
            on_done("pares ignorados fora da cobertura do dataset", "skipped")
        return ok, failed, skipped

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
