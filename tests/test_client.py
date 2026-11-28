"""Testes do TseClient (URLs, validação e download com manifest)."""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import httpx2
import pytest

from tse_fetcher import SyncPlanItem
from tse_fetcher.client import TseClient
from tse_fetcher.constants import ALIASES, DATASETS, DatasetSpec


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
    """list_datasets cobre os quatro datasets canônicos."""
    c, _rec, _created = client
    datasets = {spec.key for spec in c.list_datasets()}
    assert datasets == {"candidatos", "bens", "votacao", "prestacao_contas"}


def test_aliases_legados_resolvidos(client) -> None:
    """Aliases legados (receitas/despesas) resolvem para prestacao_contas."""
    c, _rec, _created = client
    assert set(ALIASES) == {"receitas", "despesas"}
    for legado in ALIASES:
        spec = c.get_dataset(legado)
        assert spec.key == "prestacao_contas"
        url = c.get_download_url(legado, 2024)
        assert url.endswith(
            "prestacao_contas/prestacao_de_contas_eleitorais_candidatos_2024.zip"
        )


def test_get_download_url_per_uf(client, monkeypatch) -> None:
    """Dataset per_uf (sintético) gera URL com sufixo de UF."""
    monkeypatch.setitem(
        DATASETS,
        "teste_uf",
        DatasetSpec(
            key="teste_uf",
            name="Teste",
            prefix="teste_uf",
            first_year=2020,
            per_uf=True,
        ),
    )
    c, _rec, _created = client
    url = c.get_download_url("teste_uf", 2022, uf="SP")
    assert url.endswith("teste_uf/teste_uf_2022_SP.zip")


def test_get_download_url_nacional(client) -> None:
    """URL nacional segue o padrão diretorio/prefixo_ano.zip."""
    c, _rec, _created = client
    url = c.get_download_url("candidatos", 2022)
    assert url == (
        "https://cdn.tse.jus.br/estatistica/sead/odsele/"
        "consulta_cand/consulta_cand_2022.zip"
    )


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


def test_plan_sync_per_uf_expande_27_ufs(client, tmp_path, monkeypatch) -> None:
    """Dataset per_uf (sintético) expande o plano para uma entrada por UF."""
    monkeypatch.setitem(
        DATASETS,
        "teste_uf",
        DatasetSpec(
            key="teste_uf",
            name="Teste",
            prefix="teste_uf",
            first_year=2020,
            per_uf=True,
        ),
    )
    c, rec, _created = client
    items, skipped = c.plan_sync(["teste_uf"], [2022], output_dir=tmp_path)
    assert rec.calls == []
    assert skipped == 0
    assert len(items) == 27
    assert all(item.uf is not None for item in items)
    ufs = [item.uf for item in items]
    assert ufs[0] == "AC" and ufs[-1] == "TO"
    assert sorted(ufs) == list(ufs)  # ordem alfabética de UFS
    sp = next(item for item in items if item.uf == "SP")
    assert sp.url.endswith("teste_uf/teste_uf_2022_SP.zip")
    assert sp.target.parent == tmp_path


def test_plan_sync_alias_legado_e_deduplicado(client, tmp_path) -> None:
    """Aliases legados resolvem e deduplicam (arquivo nacional único)."""
    c, rec, _created = client
    items, skipped = c.plan_sync(["receitas", "despesas"], [2022], tmp_path)
    assert rec.calls == []
    assert skipped == 0
    assert len(items) == 1  # um único arquivo nacional
    assert items[0].dataset == "prestacao_contas"
    assert items[0].filename == "prestacao_de_contas_eleitorais_candidatos_2022.zip"


def test_plan_sync_anos_fora_da_cobertura_contam_skipped(client, tmp_path) -> None:
    """Pares fora da cobertura eleitoral entram em skipped sem item."""
    c, rec, _created = client
    items, skipped = c.plan_sync(
        ["receitas", "bens"], [2018, 2020], output_dir=tmp_path
    )
    assert rec.calls == []
    # receitas (alias de prestacao_contas) não cobre 2018; bens cobre ambos.
    assert skipped == 1
    planned = {(item.dataset, item.ano) for item in items}
    assert ("bens", 2018) in planned
    assert ("prestacao_contas", 2020) in planned
    assert not any(ano == 2018 for ds, ano in planned if ds != "bens")


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


# --- Conferência do conteúdo e escrita atômica (cliente HTTP real, só a rede é dublê)


def _zip_valido() -> bytes:
    """Bytes de um ZIP de verdade, com um membro."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("consulta_cand_2022_SP.csv", "a;b\n1;2\n" * 50)
    return buf.getvalue()


def _cliente_resposta(content: bytes, *, content_type: str = "application/zip"):
    """TseClient real (um só tentativa) cujo GET devolve ``content`` com 200."""

    def handler(request):
        headers = {
            "Content-Length": str(len(content)),
            "Content-Type": content_type,
            "Last-Modified": "Sat, 28 Nov 2026 06:00:00 GMT",
        }
        if request.method == "HEAD":
            return httpx2.Response(200, headers=headers)
        return httpx2.Response(200, content=content, headers=headers)

    return TseClient(attempts=1, transport=httpx2.MockTransport(handler))


def test_download_grava_zip_valido_com_manifest(tmp_path) -> None:
    """Um ZIP íntegro é gravado no destino, com o sidecar de proveniência."""
    bom = _zip_valido()
    c = _cliente_resposta(bom)
    path = c.download("candidatos", 2022, output_dir=tmp_path)
    assert path == tmp_path / "consulta_cand_2022.zip"
    assert path.read_bytes() == bom
    assert (tmp_path / "consulta_cand_2022.zip.manifest.json").exists()


@pytest.mark.parametrize(
    "resposta",
    [
        b"<!DOCTYPE html><html><body>Pagina de bloqueio</body></html>",
        b"The requested URL was rejected. Please consult with your administrator.",
        _zip_valido()[:-40],  # truncado: sem o diretório central
    ],
    ids=["html-com-200", "bloqueio-waf", "zip-truncado"],
)
def test_download_resposta_ruim_nao_substitui_o_arquivo_bom(tmp_path, resposta) -> None:
    """HTML, bloqueio ou ZIP truncado com status 200 não vira o ZIP do destino.

    O arquivo que já estava lá permanece intacto e nenhum temporário sobra.
    """
    bom = _zip_valido()
    destino = tmp_path / "consulta_cand_2022.zip"
    destino.write_bytes(bom)
    c = _cliente_resposta(resposta, content_type="text/html")
    with pytest.raises(Exception) as excinfo:  # noqa: PT011
        c.download("candidatos", 2022, output_dir=tmp_path, force=True)
    assert not isinstance(excinfo.value, ValueError)
    assert destino.read_bytes() == bom
    assert sorted(p.name for p in tmp_path.iterdir()) == [destino.name]


def test_download_item_com_resposta_ruim_vira_falha_registrada(
    tmp_path, caplog
) -> None:
    """Uma resposta ruim conta como falha e o log diz o arquivo e a causa."""
    c = _cliente_resposta(b"<html><body>Manutencao</body></html>")
    items, _ = c.plan_sync(["candidatos"], [2022], output_dir=tmp_path)
    with caplog.at_level(logging.WARNING, logger="tse_fetcher.client"):
        ok, failed = c.download_items(items, tmp_path, force=True)
    assert (ok, failed) == (0, 1)
    assert not (tmp_path / "consulta_cand_2022.zip").exists()
    [(nome, causa)] = c.failures
    assert nome == "consulta_cand_2022.zip"
    assert "CorruptPayloadError" in causa
    avisos = [r for r in caplog.records if r.name == "tse_fetcher.client"]
    assert len(avisos) == 1
    mensagem = avisos[0].getMessage()
    assert "consulta_cand_2022.zip" in mensagem
    assert "CorruptPayloadError" in mensagem


class _FalhaNaUrl:
    """Dublê de HttpClient que falha numa URL e conclui as demais."""

    def __init__(self, falha: str) -> None:
        self.falha = falha

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        if self.falha in url:
            raise OSError("disco cheio\ncom quebra de linha")
        progress = kwargs.get("progress")
        if progress is not None:
            progress(0, 0)
            progress(100, 100)
        return Path(target)


def test_falhas_listadas_por_arquivo_e_zeradas_a_cada_rodada(tmp_path, caplog) -> None:
    """sync registra QUAL arquivo falhou e por quê; a lista não acumula."""
    c = TseClient()
    c.http = _FalhaNaUrl("bem_candidato_2022")  # type: ignore[assignment]
    with caplog.at_level(logging.WARNING, logger="tse_fetcher.client"):
        ok, failed, _ = c.sync(["bens", "candidatos"], [2022], output_dir=tmp_path)
    assert (ok, failed) == (1, 1)
    assert c.failures == [
        ("bem_candidato_2022.zip", "OSError: disco cheio com quebra de linha")
    ]
    assert "bem_candidato_2022.zip" in caplog.text
    ok, failed, _ = c.sync(["candidatos"], [2022], output_dir=tmp_path)
    assert (ok, failed) == (1, 0)
    assert c.failures == []


def test_download_encaminha_progress_e_formato_zip(client, tmp_path) -> None:
    """download pede a conferência do ZIP ao cliente HTTP e repassa o progresso."""
    c, rec, _ = client
    cb = lambda baixado, total: None  # noqa: E731
    c.download("bens", 2022, output_dir=tmp_path, progress=cb)
    assert rec.calls[0]["expected_format"] == "zip"
    assert rec.calls[0]["progress"] is cb


def test_cliente_http_do_host_e_usado_quando_informado() -> None:
    """Com ``http=``, o TseClient não cria um HttpClient próprio."""
    http = object()
    c = TseClient(http=http)  # type: ignore[arg-type]
    assert c.http is http
