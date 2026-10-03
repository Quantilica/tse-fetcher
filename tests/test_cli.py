"""Testes da CLI nativa (argparse) do tse-fetcher."""

from __future__ import annotations

import pytest

from tse_fetcher import __version__
from tse_fetcher.cli import get_parser, main


class _FakeHttp:
    """Hub dublê de HttpClient para não tocar em rede."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def download_with_manifest(self, url, target, **kwargs):  # noqa: ANN001
        self.calls.append((url, str(target)))
        return target


def _with_fake_http(monkeypatch) -> _FakeHttp:
    fake = _FakeHttp()

    def make_client(*args, **kwargs):  # noqa: ANN001, ANN002
        from tse_fetcher.client import TseClient

        client = TseClient(*args, **kwargs)
        client.http = fake  # type: ignore[method-assign]
        return client

    monkeypatch.setattr("tse_fetcher.cli.TseClient", make_client)
    return fake


def test_parser_tem_subcomandos() -> None:
    """Parser expõe list, sync e info."""
    parser = get_parser()
    actions = [action for action in parser._actions if getattr(action, "choices", None)]
    choices = set()
    for action in actions:
        choices |= set(action.choices)
    assert {"list", "sync", "info"} <= choices


def test_version(capsys) -> None:
    """--version imprime a versão do pacote."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_list(capsys) -> None:
    """list imprime os datasets com chave e nome."""
    main(["list"])
    out = capsys.readouterr().out
    assert "candidatos" in out
    assert "receitas" in out


def test_info(capsys) -> None:
    """info exibe metadados do dataset."""
    main(["info", "candidatos"])
    out = capsys.readouterr().out
    assert "consulta_cand" in out
    assert "1994" in out


def test_info_dataset_invalido(capsys) -> None:
    """info com dataset inválido encerra com código 1."""
    with pytest.raises(SystemExit) as exc_info:
        main(["info", "nao-existe"])
    assert exc_info.value.code == 1


def test_sync_dataset_especifico(monkeypatch, tmp_path) -> None:
    """sync baixa o dataset informado no diretório de saída."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "candidatos", "-y", "2022", "-o", str(tmp_path)])
    assert fake.calls
    url, target = fake.calls[0]
    assert url.endswith("consulta_cand_2022.zip")
    assert target.startswith(str(tmp_path))


def test_sync_dataset_desconhecido_captura_erro(capsys) -> None:
    """sync com dataset desconhecido encerra com código 1."""
    with pytest.raises(SystemExit) as exc_info:
        main(["sync", "nao-existe", "-y", "2022"])
    assert exc_info.value.code == 1
    assert "desconhecido" in capsys.readouterr().err


def test_sync_intervalo_de_anos(monkeypatch, tmp_path) -> None:
    """sync aceita intervalo INICIO:FIM e baixa os anos eleitorais da faixa."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "bens", "-y", "2018:2022", "-o", str(tmp_path)])
    urls = [url for url, _ in fake.calls]
    assert any("bem_candidato_2018.zip" in url for url in urls)
    assert any("bem_candidato_2020.zip" in url for url in urls)
    assert any("bem_candidato_2022.zip" in url for url in urls)
    assert not any("bem_candidato_2019" in url for url in urls)


def test_sync_anos_fora_da_cobertura_sao_filtrados(monkeypatch, tmp_path) -> None:
    """sync filtra anos anteriores ao recorte do dataset (per_uf incluído)."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "receitas", "-y", "2018:2022", "-o", str(tmp_path)])
    urls = [url for url, _ in fake.calls]
    assert any("receitas_candidato_2020_" in url for url in urls)
    assert not any("receitas_candidato_2018" in url for url in urls)
    assert not any("receitas_candidato_2019" in url for url in urls)


def test_sync_dry_run_nao_baixa(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run imprime o plano e não faz nenhum download."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "bens", "-y", "2020:2022", "-o", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out
    assert fake.calls == [], "dry-run não deve tocar na rede"
    assert "[bens] 2020 — -> bem_candidato_2020.zip" in out
    assert "(https://cdn.tse.jus.br/" in out
    assert "Total: 2 arquivo(s) planejados" in out
    # 2021 está na faixa mas não é ano eleitoral → conta como skipped.
    assert "1 par(es) ignorado(s) fora da cobertura" in out


def test_sync_dry_run_sem_skipped(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run com anos exatos não reporta pares ignorados."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "bens", "-y", "2020", "-o", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out
    assert fake.calls == []
    assert "Total: 1 arquivo(s) planejados" in out
    assert "0 par(es) ignorado(s) fora da cobertura" in out


def test_sync_dry_run_per_uf_e_skipped(monkeypatch, tmp_path, capsys) -> None:
    """sync --dry-run expande UFs e contabiliza pares fora da cobertura."""
    fake = _with_fake_http(monkeypatch)
    main(["sync", "receitas", "-y", "2018:2020", "-o", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out
    assert fake.calls == []
    assert "[receitas] 2020 AC -> receitas_candidato_2020_AC.zip" in out
    assert "[receitas] 2018" not in out
    assert "Total: 27 arquivo(s) planejados" in out
    # 2018 e 2019 anteriores ao recorte do dataset → 2 pares ignorados.
    assert "2 par(es) ignorado(s) fora da cobertura" in out
