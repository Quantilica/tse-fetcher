"""Testes do plugin Typer do tse-fetcher."""

from __future__ import annotations

import pytest

from tse_fetcher import plugin as plugin_module

typer = pytest.importorskip("typer")

from typer.testing import CliRunner  # noqa: E402

runner = CliRunner()

app = plugin_module.app


class _FakeHttp:
    """Dublê de HttpClient que registra downloads."""

    def __init__(self) -> None:
        self.urls: list[str] = []

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        self.urls.append(url)
        return target


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
