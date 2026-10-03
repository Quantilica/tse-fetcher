"""Testes da CLI standalone (fina) do tse-fetcher via a CLI unificada."""

from __future__ import annotations

import pytest

from tse_fetcher.cli import main


class _FakeHttp:
    """Hub dublê de HttpClient para não tocar em rede."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        self.calls.append((url, str(target)))
        return target


def _run_cli(argv: list[str]) -> int:
    """Executar a CLI unificada (main) e retornar o código de saída.

    O modo standalone do Click encerra com ``SystemExit`` mesmo em caso de
    sucesso (código 0).

    Args:
        argv (list[str]): Argumentos da linha de comando.

    Returns:
        int: Código de saída do processo.
    """
    with pytest.raises(SystemExit) as exc_info:
        main(argv)
    return exc_info.value.code


def _with_fake_http(monkeypatch) -> _FakeHttp:
    fake = _FakeHttp()

    def make_client(*args, **kwargs):  # noqa: ANN001, ANN002
        from tse_fetcher.client import TseClient

        client = TseClient(*args, **kwargs)
        client.http = fake  # type: ignore[method-assign]
        return client

    monkeypatch.setattr("tse_fetcher.plugin.TseClient", make_client)
    return fake


def test_list(capsys) -> None:
    """list imprime os datasets com chave e nome."""
    assert _run_cli(["list"]) == 0
    out = capsys.readouterr().out
    assert "candidatos" in out
    assert "receitas" in out


def test_info(capsys) -> None:
    """info exibe metadados do dataset."""
    assert _run_cli(["info", "candidatos"]) == 0
    out = capsys.readouterr().out
    assert "consulta_cand" in out
    assert "1994" in out


def test_info_dataset_invalido(capsys) -> None:
    """info com dataset inválido encerra com código 1."""
    assert _run_cli(["info", "nao-existe"]) == 1


def test_sync_dataset_especifico(monkeypatch, tmp_path) -> None:
    """sync baixa o dataset informado no diretório de saída."""
    fake = _with_fake_http(monkeypatch)
    assert _run_cli(["sync", "candidatos", "-y", "2022", "-o", str(tmp_path)]) == 0
    assert fake.calls
    url, target = fake.calls[0]
    assert url.endswith("consulta_cand_2022.zip")
    assert target.startswith(str(tmp_path))


def test_sync_dataset_desconhecido_captura_erro(capsys) -> None:
    """sync com dataset desconhecido encerra com código 1."""
    assert _run_cli(["sync", "nao-existe", "-y", "2022"]) == 1
    assert "desconhecido" in capsys.readouterr().out


def test_sync_intervalo_de_anos(monkeypatch, tmp_path) -> None:
    """sync aceita intervalo INICIO:FIM e baixa os anos eleitorais da faixa."""
    fake = _with_fake_http(monkeypatch)
    assert _run_cli(["sync", "bens", "-y", "2018:2022", "-o", str(tmp_path)]) == 0
    urls = [url for url, _ in fake.calls]
    assert any("bem_candidato_2018.zip" in url for url in urls)
    assert any("bem_candidato_2020.zip" in url for url in urls)
    assert any("bem_candidato_2022.zip" in url for url in urls)
    assert not any("bem_candidato_2019" in url for url in urls)


def test_sync_anos_fora_da_cobertura_sao_filtrados(monkeypatch, tmp_path) -> None:
    """sync filtra anos anteriores ao recorte do dataset (per_uf incluído)."""
    fake = _with_fake_http(monkeypatch)
    assert _run_cli(["sync", "receitas", "-y", "2018:2022", "-o", str(tmp_path)]) == 0
    urls = [url for url, _ in fake.calls]
    assert any("receitas_candidato_2020_" in url for url in urls)
    assert not any("receitas_candidato_2018" in url for url in urls)
    assert not any("receitas_candidato_2019" in url for url in urls)


def test_sync_dry_run_nao_baixa(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run imprime o plano (plan_sync) e não faz nenhum download."""
    fake = _with_fake_http(monkeypatch)
    assert (
        _run_cli(["sync", "bens", "-y", "2020:2022", "-o", str(tmp_path), "--dry-run"])
        == 0
    )
    out = capsys.readouterr().out
    assert fake.calls == [], "dry-run não deve tocar na rede"
    assert "bem_candidato_2020.zip" in out
    assert "Total:" in out
    assert "2 arquivo(s) planejados" in out
    # 2021 está na faixa mas não é ano eleitoral → conta como skipped.
    assert "1 par(es) ignorado(s)" in out


def test_sync_dry_run_sem_skipped(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run com anos exatos não reporta pares ignorados."""
    fake = _with_fake_http(monkeypatch)
    argv = ["sync", "bens", "-y", "2020", "-o", str(tmp_path), "--dry-run"]
    assert _run_cli(argv) == 0
    out = capsys.readouterr().out
    assert fake.calls == []
    assert "Total:" in out
    assert "1 arquivo(s) planejados" in out
    assert "0 par(es) ignorado(s)" in out


def test_sync_dry_run_per_uf_e_skipped(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run expande UFs e contabiliza pares fora da cobertura."""
    fake = _with_fake_http(monkeypatch)
    assert (
        _run_cli(
            ["sync", "receitas", "-y", "2018:2020", "-o", str(tmp_path), "--dry-run"]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert fake.calls == []
    assert "AC" in out
    assert "2018" not in out
    assert "Total:" in out
    assert "27 arquivo(s) planejados" in out
    # 2018 e 2019 anteriores ao recorte do dataset → 2 pares ignorados.
    assert "2 par(es) ignorado(s)" in out
