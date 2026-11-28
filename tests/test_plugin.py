"""Testes do plugin Typer (FetcherApp) do tse-fetcher."""

from __future__ import annotations

import json

import httpx2
import pytest
from quantilica.cli.sdk import CheckPlan, FetcherApp
from typer.testing import CliRunner

from tse_fetcher import plugin as plugin_module
from tse_fetcher.client import TseClient
from tse_fetcher.plugin import app, fetcher

runner = CliRunner()


class _FakeHttp:
    """Dublê de HttpClient que registra downloads e serve HEAD fake."""

    def __init__(self) -> None:
        self.urls: list[str] = []
        self.kwargs: list[dict] = []
        self.head_headers: dict[str, str] = {
            "Content-Length": "17",
            "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT",
            "ETag": '"fake1"',
        }

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        self.urls.append(url)
        self.kwargs.append(kwargs)
        return target

    def head(self, url, **kwargs):  # noqa: ANN001, ANN002
        return httpx2.Response(200, headers=dict(self.head_headers))


@pytest.fixture
def fake_http(monkeypatch) -> _FakeHttp:
    """Substitui o HttpClient do TseClient pelo dublê no namespace plugin."""
    fake = _FakeHttp()
    original = plugin_module.TseClient

    def make_client(*args, **kwargs):  # noqa: ANN001, ANN002
        real = original(*args, **kwargs)
        real.http = fake  # type: ignore[method-assign]
        return real

    monkeypatch.setattr(plugin_module, "TseClient", make_client)
    return fake


def test_fetcher_app_canonica() -> None:
    """plugin expõe a FetcherApp canônica e usa fetcher.app como app."""
    assert isinstance(fetcher, FetcherApp)
    assert fetcher.name == "tse-fetcher"
    assert app is fetcher.app


def test_list() -> None:
    """lista datasets no terminal Rich."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "candidatos" in result.output


def test_info(fake_http) -> None:
    """info mostra metadados do dataset."""
    result = runner.invoke(app, ["info", "bens"])
    assert result.exit_code == 0
    assert "bem_candidato" in result.output


def test_info_dataset_invalido(fake_http) -> None:
    """info com dataset desconhecido encerra com código 1."""
    result = runner.invoke(app, ["info", "qualquer"])
    assert result.exit_code == 1


def test_sync_dataset_especifico(fake_http, tmp_path) -> None:
    """sync baixa apenas o dataset informado."""
    result = runner.invoke(
        app, ["sync", "candidatos", "-y", "2022", "-o", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert any(url.endswith("consulta_cand_2022.zip") for url in fake_http.urls)


def test_sync_dataset_invalido_aborta(fake_http, tmp_path) -> None:
    """sync com dataset inválido aborta com código 1 e não baixa nada."""
    result = runner.invoke(app, ["sync", "foofetch", "-y", "2022", "-o", str(tmp_path)])
    assert result.exit_code == 1
    assert fake_http.urls == []


def test_sync_dry_run_nao_baixa(fake_http, tmp_path) -> None:
    """sync --dry-run renderiza tabela de plano e não faz download."""
    result = runner.invoke(
        app, ["sync", "bens", "-y", "2020:2022", "-o", str(tmp_path), "--dry-run"]
    )
    assert result.exit_code == 0
    assert fake_http.urls == []
    assert "bem_candidato_2020.zip" in result.output
    assert "bem_candidato_2022.zip" in result.output
    assert "Total:" in result.output
    assert "2 arquivo(s) planejados" in result.output


def test_sync_dry_run_dataset_invalido_aborta(fake_http, tmp_path) -> None:
    """sync --dry-run valida datasets antes de planejar."""
    result = runner.invoke(
        app, ["sync", "foofetch", "-y", "2022", "-o", str(tmp_path), "--dry-run"]
    )
    assert result.exit_code == 1
    assert fake_http.urls == []


def test_check_lista_veredictos_sem_baixar(fake_http, tmp_path) -> None:
    """check renderiza a tabela e não faz download."""
    result = runner.invoke(app, ["check", "bens", "-y", "2022", "-o", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert fake_http.urls == []
    assert "download" in result.output
    assert "not-present" in result.output
    assert "1 verificado(s)" in result.output


def test_check_dataset_invalido_aborta(fake_http, tmp_path) -> None:
    """check valida datasets como o sync."""
    result = runner.invoke(
        app, ["check", "foofetch", "-y", "2022", "-o", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert fake_http.urls == []


def test_check_json_e_roundtrip(fake_http, tmp_path) -> None:
    """check --json emite plano parseável com os mesmos ids."""
    result = runner.invoke(
        app, ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--json"]
    )
    assert result.exit_code == 0, result.output
    plan = CheckPlan.from_json(result.output)
    assert plan.fetcher == "tse-fetcher"
    assert len(plan.items) > 0
    assert all(it.action == "download" for it in plan.items)
    assert plan.items[0].id == "bem_candidato_2022.zip"


def test_sync_from_plan_baixa_so_planejado(fake_http, tmp_path) -> None:
    """sync --from-plan baixa só entradas com ação download."""
    check = runner.invoke(
        app, ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--json"]
    )
    assert check.exit_code == 0, check.output
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(check.output, encoding="utf-8")

    result = runner.invoke(
        app, ["sync", "--from-plan", str(plan_file), "-o", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    plan = CheckPlan.from_json(check.output)
    assert len(fake_http.urls) == len(plan.items) > 0


def test_sync_from_plan_pula_skip(fake_http, tmp_path) -> None:
    """Entradas skip-up-to-date no plano não são baixadas."""
    check = runner.invoke(
        app, ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--json"]
    )
    assert check.exit_code == 0, check.output
    data = json.loads(check.output)
    first = data["items"][0]
    local = tmp_path / first["entry"]["filename"]
    local.write_bytes(b"0" * 17)

    check2 = runner.invoke(
        app, ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--json"]
    )
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(check2.output, encoding="utf-8")
    result = runner.invoke(
        app, ["sync", "--from-plan", str(plan_file), "-o", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    assert first["url"] not in fake_http.urls
    assert len(fake_http.urls) == len(data["items"]) - 1


def test_sync_from_plan_invalido_aborta(fake_http, tmp_path) -> None:
    """Plano inválido aborta com exit 1."""
    bad = tmp_path / "bad.json"
    bad.write_text('{"nao": "eh-plano"}', encoding="utf-8")
    result = runner.invoke(app, ["sync", "--from-plan", str(bad)])
    assert result.exit_code == 1
    assert "Plano inválido" in result.output
    assert fake_http.urls == []


def test_check_out_grava_plano_atomico(fake_http, tmp_path) -> None:
    """check --out grava JSON válido, sem JSON no stdout."""
    out = tmp_path / "sub" / "raw.json"
    result = runner.invoke(
        app, ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    plan = CheckPlan.from_json(out.read_text(encoding="utf-8"))
    assert plan.fetcher == "tse-fetcher"
    assert len(plan.items) > 0
    assert '"items"' not in result.output
    assert "Plano gravado em" in result.output
    assert [p.name for p in out.parent.iterdir()] == ["raw.json"]


def test_check_out_prevalece_sobre_json(fake_http, tmp_path) -> None:
    """--out prevalece sobre --json: nada de JSON no stdout."""
    out = tmp_path / "raw.json"
    result = runner.invoke(
        app,
        [
            "check",
            "bens",
            "-y",
            "2022",
            "-o",
            str(tmp_path),
            "--json",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert '"items"' not in result.output


def test_check_out_em_diretorio_falha(fake_http, tmp_path) -> None:
    """--out apontando para diretório existente encerra com exit 1."""
    result = runner.invoke(
        app,
        ["check", "bens", "-y", "2022", "-o", str(tmp_path), "--out", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Falha ao gravar o plano" in result.output


def _plano_reescrito(fake_http, tmp_path):  # noqa: ANN001, ANN202
    raw = tmp_path / "raw.json"
    check = runner.invoke(
        app,
        ["check", "bens", "-y", "2020:2022", "-o", str(tmp_path), "--out", str(raw)],
    )
    assert check.exit_code == 0, check.output
    data = json.loads(raw.read_text(encoding="utf-8"))
    data["items"][0]["action"] = "skip-up-to-date"
    data["items"][0]["reason"] = "ingest verified"
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(data), encoding="utf-8")
    return plan_file, data


def test_sync_from_plan_force_repassa_force(fake_http, tmp_path) -> None:
    """--force chega ao download_with_manifest; só itens download são baixados."""
    plan_file, data = _plano_reescrito(fake_http, tmp_path)
    result = runner.invoke(
        app,
        ["sync", "--from-plan", str(plan_file), "--force", "-o", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert len(fake_http.urls) == len(data["items"]) - 1 > 0
    assert data["items"][0]["entry"]["url"] not in fake_http.urls
    assert all(kw.get("force") is True for kw in fake_http.kwargs)


def test_sync_from_plan_sem_force_mantem_force_falso(fake_http, tmp_path) -> None:
    """Sem --force, o download recebe force=False."""
    plan_file, data = _plano_reescrito(fake_http, tmp_path)
    result = runner.invoke(
        app, ["sync", "--from-plan", str(plan_file), "-o", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    assert len(fake_http.urls) == len(data["items"]) - 1 > 0
    assert all(kw.get("force") is False for kw in fake_http.kwargs)


def _fake_download_one(ok_por_ano: dict[int, int]):
    """``_download_one`` falso: devolve ``(ok, failed)`` conforme o ano do item."""

    def fake(self, dataset, ano, uf, output_dir, force):  # noqa: ANN001
        ok = ok_por_ano[ano]
        return (ok, 1 - ok)

    return fake


def test_sync_exit_code_helper() -> None:
    assert plugin_module.sync_exit_code(3, 0) == 0
    assert plugin_module.sync_exit_code(2, 1) == plugin_module.EXIT_SYNC_PARTIAL == 3
    assert plugin_module.sync_exit_code(0, 2) == 1


@pytest.mark.parametrize(
    ("resultado", "codigo"),
    [({2020: 1, 2022: 1}, 0), ({2020: 1, 2022: 0}, 3), ({2020: 0, 2022: 0}, 1)],
)
def test_sync_sai_com_codigo_conforme_as_falhas(
    fake_http, tmp_path, monkeypatch, resultado, codigo
) -> None:
    """0 sem falhas, 3 se parte baixou e parte falhou, 1 se nada baixou."""
    monkeypatch.setattr(TseClient, "_download_one", _fake_download_one(resultado))
    result = runner.invoke(
        app, ["sync", "candidatos", "-y", "2020", "-y", "2022", "-o", str(tmp_path)]
    )
    assert result.exit_code == codigo, result.output


def test_sync_from_plan_com_falha_parcial_sai_com_tres(
    fake_http, tmp_path, monkeypatch
) -> None:
    check = runner.invoke(
        app,
        [
            "check",
            "candidatos",
            "-y",
            "2020",
            "-y",
            "2022",
            "-o",
            str(tmp_path),
            "--json",
        ],
    )
    assert check.exit_code == 0, check.output
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(check.output, encoding="utf-8")
    monkeypatch.setattr(
        TseClient, "_download_one", _fake_download_one({2020: 1, 2022: 0})
    )
    result = runner.invoke(
        app, ["sync", "--from-plan", str(plan_file), "-o", str(tmp_path)]
    )
    assert result.exit_code == 3, result.output


# --- --summary-json (mesmo contrato do ``sync`` do host)


class _FakeHttpComFalha(_FakeHttp):
    """Dublê que mede a transferência e falha nas URLs que contêm ``falha``."""

    def __init__(self, falha: str | None = None) -> None:
        super().__init__()
        self.falha = falha

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        if self.falha and self.falha in url:
            raise OSError("conexão encerrada pelo servidor")
        progress = kwargs.get("progress")
        if progress is not None:
            progress(0, 0)
            progress(1000, 1000)
        return super().download_with_manifest(url, target, **kwargs)


@pytest.fixture
def http_falha(monkeypatch):
    """Fábrica de dublês: ``http_falha("trecho-da-url")`` falha nessa URL."""

    def fabricar(falha: str | None = None) -> _FakeHttpComFalha:
        fake = _FakeHttpComFalha(falha)
        original = plugin_module.TseClient

        def make_client(*args, **kwargs):  # noqa: ANN001, ANN002
            real = original(*args, **kwargs)
            real.http = fake  # type: ignore[method-assign]
            return real

        monkeypatch.setattr(plugin_module, "TseClient", make_client)
        return fake

    return fabricar


def _sync_com_resumo(tmp_path, *args):
    resumo = tmp_path / "pasta" / "resumo.json"
    result = runner.invoke(
        app,
        ["sync", *args, "-o", str(tmp_path / "saida"), "--summary-json", str(resumo)],
    )
    return result, json.loads(resumo.read_text(encoding="utf-8"))


def test_sync_anuncia_summary_json_na_ajuda() -> None:
    """A opção aparece na ajuda do sync (o host só a repassa se a ajuda a anuncia)."""
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "--summary-json" in result.output


def test_summary_json_sucesso(http_falha, tmp_path) -> None:
    http_falha()
    result, resumo = _sync_com_resumo(tmp_path, "candidatos", "-y", "2022")
    assert result.exit_code == 0, result.output
    assert resumo["schema_version"] == 1
    assert resumo["fetcher"] == "tse-fetcher"
    assert resumo["command"] == "sync"
    assert resumo["status"] == "success"
    assert resumo["exit_code"] == 0
    assert resumo["dry_run"] is False
    assert (resumo["total"], resumo["succeeded"], resumo["failed"]) == (1, 1, 0)
    assert (resumo["downloaded"], resumo["skipped"]) == (1, 0)
    assert resumo["bytes_downloaded"] == 1000
    assert resumo["errors"] == []


def test_summary_json_parcial_lista_arquivo_e_causa(http_falha, tmp_path) -> None:
    http_falha("bem_candidato_2022")
    result, resumo = _sync_com_resumo(tmp_path, "bens", "candidatos", "-y", "2022")
    assert result.exit_code == 3, result.output
    assert resumo["status"] == "partial"
    assert resumo["exit_code"] == 3
    assert (resumo["total"], resumo["succeeded"], resumo["failed"]) == (2, 1, 1)
    [erro] = resumo["errors"]
    assert erro["id"] == "bem_candidato_2022.zip"
    assert "OSError" in erro["message"]
    assert "conexão encerrada" in erro["message"]
    # O resumo na tela também diz qual arquivo falhou e por quê.
    assert "bem_candidato_2022.zip" in result.output
    assert "OSError" in result.output


def test_summary_json_tudo_falha_sai_com_um(http_falha, tmp_path) -> None:
    http_falha("consulta_cand")
    result, resumo = _sync_com_resumo(tmp_path, "candidatos", "-y", "2022")
    assert result.exit_code == 1, result.output
    assert resumo["status"] == "failed"
    assert (resumo["succeeded"], resumo["failed"]) == (0, 1)


def test_summary_json_dry_run(http_falha, tmp_path) -> None:
    fake = http_falha()
    result, resumo = _sync_com_resumo(tmp_path, "bens", "-y", "2022", "--dry-run")
    assert result.exit_code == 0, result.output
    assert fake.urls == []
    assert resumo["dry_run"] is True
    assert (resumo["total"], resumo["succeeded"], resumo["failed"]) == (1, 0, 0)


def test_summary_json_dataset_invalido(http_falha, tmp_path) -> None:
    http_falha()
    result, resumo = _sync_com_resumo(tmp_path, "foofetch", "-y", "2022")
    assert result.exit_code == 1
    assert resumo["status"] == "failed"
    assert "foofetch" in resumo["error"]


def test_summary_json_from_plan(http_falha, tmp_path) -> None:
    http_falha("bem_candidato_2022")
    check = runner.invoke(
        app,
        ["check", "bens", "candidatos", "-y", "2022", "-o", str(tmp_path), "--json"],
    )
    assert check.exit_code == 0, check.output
    plano = tmp_path / "plan.json"
    plano.write_text(check.output, encoding="utf-8")
    result, resumo = _sync_com_resumo(tmp_path, "--from-plan", str(plano))
    assert result.exit_code == 3, result.output
    assert (resumo["total"], resumo["succeeded"], resumo["failed"]) == (2, 1, 1)
    assert resumo["errors"][0]["id"] == "bem_candidato_2022.zip"


def test_sync_sem_summary_json_nao_grava_nada(http_falha, tmp_path) -> None:
    http_falha()
    result = runner.invoke(
        app, ["sync", "candidatos", "-y", "2022", "-o", str(tmp_path / "saida")]
    )
    assert result.exit_code == 0, result.output
    assert not list(tmp_path.glob("**/*.json"))


def test_cliente_do_plugin_usa_o_cliente_http_padrao_do_host(monkeypatch) -> None:
    """O sync/check do plugin usam o ``default_client()`` do host (env e CA)."""
    sentinela = object()
    monkeypatch.setattr(plugin_module, "default_client", lambda: sentinela)
    assert plugin_module._new_client().http is sentinela


def test_plugin_carrega_em_host_sem_modulo_de_resumo(monkeypatch, tmp_path) -> None:
    """Sem ``quantilica.cli.summary`` o plugin carrega e não anuncia --summary-json."""
    import importlib
    import sys

    chave = "tse_fetcher.plugin"
    original = sys.modules[chave]
    monkeypatch.setitem(sys.modules, "quantilica.cli.summary", None)
    monkeypatch.delitem(sys.modules, chave)
    try:
        novo = importlib.import_module(chave)
        assert novo.SummaryRecorder is None
        ajuda = runner.invoke(novo.app, ["sync", "--help"])
        assert ajuda.exit_code == 0
        assert "--summary-json" not in ajuda.output
        assert "--dry-run" in ajuda.output
        # Sem o módulo o sync segue funcionando (e sai com o código do contrato).
        novo.TseClient = plugin_module.TseClient
        result = runner.invoke(
            novo.app, ["sync", "foofetch", "-y", "2022", "-o", str(tmp_path)]
        )
        assert result.exit_code == 1
    finally:
        sys.modules[chave] = original
