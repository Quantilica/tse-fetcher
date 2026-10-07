"""Testes do TseClient (URLs, validação e download com manifest)."""

from __future__ import annotations

from pathlib import Path

import httpx2
import pytest

from tse_fetcher import SyncPlanItem
from tse_fetcher.client import TseClient


class _RecordingHttp:
    """Dublê do HttpClient que registra os argumentos de download."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"conteudo-zip-fake")
        self.calls.append({"url": url, "target": target, **kwargs})
        return target


@pytest.fixture
def client(tmp_path) -> tuple[TseClient, _RecordingHttp, list[Path]]:
    """Client com HttpClient dublê que cria arquivos fake."""
    rec = _RecordingHttp()
    created: list[Path] = []
    c = TseClient(base_url="https://cdn.tse.jus.br/estatistica/sead/odsele")
    c.http = rec  # type: ignore[assignment]
    return c, rec, created


def test_list_datasets(client) -> None:
    """list_datasets cobre os cinco datasets canônicos."""
    c, _rec, _created = client
    datasets = {spec.key for spec in c.list_datasets()}
    assert datasets == {"candidatos", "bens", "votacao", "receitas", "despesas"}


def test_get_download_url_nacional(client) -> None:
    """URL nacional segue o padrão diretorio/prefixo_ano.zip."""
    c, _rec, _created = client
    url = c.get_download_url("candidatos", 2022)
    assert url == (
        "https://cdn.tse.jus.br/estatistica/sead/odsele/"
        "consulta_cand/consulta_cand_2022.zip"
    )


def test_get_download_url_per_uf(client) -> None:
    """Datasets per_uf geram URL com sufixo de UF."""
    c, _rec, _created = client
    url = c.get_download_url("receitas", 2022, uf="SP")
    assert url.endswith("receitas_candidato_2022_SP.zip")


def test_get_download_url_uf_em_dataset_nacional_rejeitada(client) -> None:
    """Dataset nacional não aceita UF."""
    c, _rec, _created = client
    with pytest.raises(ValueError, match="não aceita UF"):
        c.get_download_url("bens", 2022, uf="SP")


def test_dataset_desconhecido(client) -> None:
    """Dataset inválido gera ValueError com lista de suportados."""
    c, _rec, _created = client
    with pytest.raises(ValueError, match="Dataset desconhecido"):
        c.get_download_url("nao-existe", 2022)


def test_ano_nao_eleitoral_rejeitado(client) -> None:
    """Ano ímpar de eleição inexistente gera ValueError."""
    c, _rec, _created = client
    with pytest.raises(ValueError):  # noqa: PT011
        c.get_download_url("candidatos", 2021)


def test_ano_antes_do_primeiro_ano_rejeitado(client) -> None:
    """Dataset com recorte temporal mais recente rejeita anos anteriores."""
    c, _rec, _created = client
    with pytest.raises(ValueError, match="início 2020"):
        c.get_download_url("receitas", 1998)


def test_uf_invalida_rejeitada(client) -> None:
    """Sigla inexistente gera ValueError."""
    c, _rec, _created = client
    with pytest.raises(ValueError, match="UF inválida"):
        c.get_download_url("receitas", 2022, uf="XX")


def test_download_gera_manifest_e_retorna_path(client, tmp_path) -> None:
    """download grava o arquivo no destino e registra chamada com manifest."""
    c, rec, _created = client
    path = c.download("candidatos", 2022, output_dir=tmp_path / "out")
    assert path.exists()
    assert rec.calls, "download_with_manifest não foi chamado"
    call = rec.calls[0]
    assert call["url"].endswith("consulta_cand_2022.zip")
    assert call["source_id"] == "tse"
    assert call["producer"].startswith("Tribunal")
    assert call["dataset_id"] == "candidatos_2022"


def test_sync_plan_item_imutavel() -> None:
    """SyncPlanItem é frozen — atribuição gera erro."""
    item = SyncPlanItem(
        dataset="bens",
        dataset_name="Bens de candidatos (bem_candidato)",
        ano=2022,
        uf=None,
        filename="bem_candidato_2022.zip",
        url="https://cdn.tse.jus.br/bem_candidato_2022.zip",
        target=Path("/data/tse/bem_candidato_2022.zip"),
    )
    with pytest.raises(Exception):  # noqa: B017, PT011
        item.ano = 2024


# --- plan_sync / sync(dry_run) ---


def test_plan_sync_nacional(client, tmp_path) -> None:
    """plan_sync lista URLs/alvos sem tocar na rede nem gravar em disco."""
    c, rec, _created = client
    items, skipped = c.plan_sync(["candidatos"], [2022], output_dir=tmp_path)
    assert rec.calls == [], "plan_sync não deve fazer download"
    assert skipped == 0
    assert len(items) == 1
    item = items[0]
    assert item.dataset == "candidatos"
    assert item.dataset_name.startswith("Candidatos")
    assert item.ano == 2022
    assert item.uf is None
    assert item.filename == "consulta_cand_2022.zip"
    assert item.url.endswith("consulta_cand/consulta_cand_2022.zip")
    assert item.target == tmp_path / "consulta_cand_2022.zip"
    assert not (tmp_path / "consulta_cand_2022.zip").exists()


def test_plan_sync_per_uf_expande_27_ufs(client, tmp_path) -> None:
    """Dataset per_uf expande o plano para uma entrada por UF."""
    c, rec, _created = client
    items, skipped = c.plan_sync(["receitas"], [2022], output_dir=tmp_path)
    assert rec.calls == []
    assert skipped == 0
    assert len(items) == 27
    assert all(item.uf is not None for item in items)
    ufs = [item.uf for item in items]
    assert ufs[0] == "AC" and ufs[-1] == "TO"
    assert sorted(ufs) == list(ufs)  # ordem alfabética de UFS
    sp = next(item for item in items if item.uf == "SP")
    assert sp.filename == "receitas_candidato_2022_SP.zip"
    assert sp.url.endswith("receitas_candidato_2022_SP.zip")
    assert sp.target.parent == tmp_path


def test_plan_sync_anos_fora_da_cobertura_contam_skipped(client, tmp_path) -> None:
    """Pares fora da cobertura eleitoral entram em skipped sem item."""
    c, rec, _created = client
    items, skipped = c.plan_sync(
        ["receitas", "bens"], [2018, 2020], output_dir=tmp_path
    )
    assert rec.calls == []
    # receitas não cobre 2018 (first_year=2020); bens cobre ambos.
    assert skipped == 1
    planned = {(item.dataset, item.ano) for item in items}
    assert ("bens", 2018) in planned
    assert ("receitas", 2018) not in planned
    assert ("receitas", 2020) in planned


def test_plan_sync_dataset_desconhecido(client) -> None:
    """Dataset inválido aborta o planejamento com ValueError."""
    c, _rec, _created = client
    with pytest.raises(ValueError, match="Dataset desconhecido"):
        c.plan_sync(["nao-existe"], [2022])


def test_sync_dry_run_nao_baixa(client, tmp_path) -> None:
    """sync(dry_run=True) retorna (0, 0, skipped) sem chamar a rede."""
    c, rec, _created = client
    ok, failed, skipped = c.sync(
        ["bens"], [2018, 2020], output_dir=tmp_path, dry_run=True
    )
    assert (ok, failed, skipped) == (0, 0, 0)
    assert rec.calls == []
    assert not any(tmp_path.rglob("*.zip"))


def test_sync_dry_run_com_callback(client, tmp_path) -> None:
    """sync(dry_run=True) emite on_done por item planejado e skipped."""
    c, rec, _created = client
    eventos: list[tuple[str, str]] = []
    ok, failed, skipped = c.sync(
        ["receitas"],
        [2018, 2020],
        output_dir=tmp_path,
        on_done=lambda filename, result: eventos.append((filename, result)),
        dry_run=True,
    )
    assert (ok, failed, skipped) == (0, 0, 1)
    assert rec.calls == []
    assert all(result == "skipped" for _, result in eventos)
    assert eventos[-1] == ("pares ignorados fora da cobertura do dataset", "skipped")


def _mock_transport(
    head_status: int = 200,
    head_headers: dict | None = None,
    content: bytes = b"zip-bytes-fake",
    fail_head: bool = False,
):
    """Transporte mock com HEAD configurável e GET com conteúdo fixo."""

    def handler(request):
        if request.method == "HEAD":
            if fail_head:
                raise httpx2.ConnectError("rede fora")
            return httpx2.Response(head_status, headers=head_headers or {})
        return httpx2.Response(200, content=content)

    return httpx2.MockTransport(handler)


_HEAD_OK = {
    "Content-Length": "14",
    "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT",
    "ETag": '"tse1"',
}


def test_check_item_missing_downloads(tmp_path) -> None:
    """Sem arquivo local, o veredicto é download/not-present."""
    c = TseClient(transport=_mock_transport(head_headers=_HEAD_OK))
    items, _ = c.plan_sync(["bens"], [2022], output_dir=tmp_path)
    assert items, "esperava ao menos um item planejado"
    verdict = c.check_item(items[0])
    assert verdict["action"] == "download"
    assert verdict["reason"] == "not-present"
    assert verdict["remote_etag"] == '"tse1"'
    assert verdict["remote_size"] == 14
    assert verdict["local_exists"] is False
    assert verdict["entry"]["filename"] == items[0].filename


def test_check_item_fresh_skips(tmp_path) -> None:
    """Arquivo local fresco gera skip-up-to-date."""
    c = TseClient(transport=_mock_transport(head_headers=_HEAD_OK))
    items, _ = c.plan_sync(["bens"], [2022], output_dir=tmp_path)
    target = items[0].target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"0" * 14)
    verdict = c.check_item(items[0])
    assert verdict["action"] == "skip-up-to-date"
    assert verdict["reason"] == "local-fresh"
    assert verdict["local_exists"] is True


def test_check_item_head_error_downloads(tmp_path) -> None:
    """HEAD falhando gera download/metadata-unavailable (sync tentará)."""
    c = TseClient(transport=_mock_transport(fail_head=True))
    items, _ = c.plan_sync(["bens"], [2022], output_dir=tmp_path)
    verdict = c.check_item(items[0])
    assert verdict["action"] == "download"
    assert verdict["reason"].startswith("metadata-unavailable")


def test_download_items_baixa_lista_planejada(tmp_path) -> None:
    """download_items baixa exatamente os itens recebidos."""
    rec = _RecordingHttp()
    c = TseClient()
    c.http = rec  # type: ignore[assignment]
    items, _ = c.plan_sync(["bens"], [2022], output_dir=tmp_path)
    ok, failed = c.download_items(items, tmp_path)
    assert failed == 0
    assert ok == len(items) > 0
    assert len(rec.calls) == len(items)
