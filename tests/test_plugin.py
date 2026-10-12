"""Testes do plugin Typer (FetcherApp) do tse-fetcher."""

from __future__ import annotations

import json

import httpx2
import pytest
from quantilica.cli.sdk import CheckPlan, FetcherApp
from typer.testing import CliRunner

from tse_fetcher import plugin as plugin_module
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
