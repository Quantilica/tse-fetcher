"""Testes do TseClient (URLs, validação e download com manifest)."""

from __future__ import annotations

from pathlib import Path

import pytest

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
