"""CLI standalone para tse-fetcher (argparse, sem typer/rich)."""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .client import TseClient
from .constants import DATASETS, DEFAULT_OUTPUT, DEFAULT_YEAR_RANGE


def get_parser() -> argparse.ArgumentParser:
    """Construir o parser argparse da CLI nativa.

    Returns:
        argparse.ArgumentParser: Parser configurado com os subcomandos
        ``list``, ``sync`` e ``info``.
    """
    parser = argparse.ArgumentParser(
        prog="tse-fetcher",
        description="Coletor de dados eleitorais do TSE (Tribunal Superior Eleitoral).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- subcomando: list ---
    subparsers.add_parser(
        "list",
        help="Listar datasets disponíveis no ODSele.",
    )

    # --- subcomando: sync ---
    sync = subparsers.add_parser(
        "sync",
        help="Baixar/atualizar dados (tudo por padrão).",
    )
    sync.add_argument(
        "datasets",
        nargs="*",
        metavar="DATASET",
        help="Datasets a sincronizar. Omitir para baixar todos.",
    )
    sync.add_argument(
        "-y",
        "--years",
        nargs="*",
        default=[DEFAULT_YEAR_RANGE],
        metavar="ANO",
        help="Anos eleitorais (ex: 2022) ou intervalos (2020:2022).",
    )
    sync.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        default=DEFAULT_OUTPUT,
        help=f"Diretório de saída (padrão: {DEFAULT_OUTPUT}).",
    )
    sync.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Re-baixar mesmo se o arquivo local estiver fresco.",
    )
    sync.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Exibir logs detalhados.",
    )

    # --- subcomando: info ---
    info = subparsers.add_parser(
        "info",
        help="Exibir metadados de um dataset específico.",
    )
    info.add_argument(
        "dataset",
        metavar="DATASET",
        help="Nome canônico do dataset (veja 'list').",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    """Executar a CLI nativa do tse-fetcher.

    Args:
        argv (list[str] | None): Argumentos a parsear; None usa sys.argv.
    """
    parser = get_parser()
    args = parser.parse_args(argv)

    from quantilica.core.logging import configure_cli_logging

    configure_cli_logging(verbose=args.verbose if args.command == "sync" else False)

    if args.command == "list":
        _cmd_list()
    elif args.command == "sync":
        _cmd_sync(args)
    elif args.command == "info":
        _cmd_info(args)


def _cmd_list() -> None:
    """Listar datasets suportados."""
    client = TseClient()
    for spec in client.list_datasets():
        print(f"{spec.key:10s} {spec.name} (a partir de {spec.first_year})")


def _cmd_sync(args: argparse.Namespace) -> None:
    """Baixar datasets selecionados (ou todos) para os anos informados."""
    from quantilica.core.dates import expand_year_range

    if args.years:
        try:
            anos = expand_year_range(*args.years)
        except ValueError as exc:
            print(f"Erro: ano/intervalo inválido. {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        anos = []

    datasets = args.datasets if args.datasets else sorted(DATASETS)
    for dataset in datasets:
        if dataset not in DATASETS:
            print(f"Erro: dataset desconhecido: {dataset}", file=sys.stderr)
            sys.exit(1)

    if not args.verbose:
        logging.getLogger("quantilica.core").setLevel(logging.WARNING)
        logging.getLogger("tse_fetcher").setLevel(logging.WARNING)

    client = TseClient()
    ok, failed, skipped = client.sync(
        datasets,
        anos,
        output_dir=args.output,
        force=args.force,
        on_done=lambda filename, result: print(f"[{result}] {filename}"),
    )
    print(f"Concluído: {ok} OK · {failed} falha(s) · {skipped} ignorado(s)")
    if failed and ok == 0:
        sys.exit(1)


def _cmd_info(args: argparse.Namespace) -> None:
    """Exibir metadados de um dataset."""
    client = TseClient()
    try:
        spec = client.get_dataset(args.dataset)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)
    url = client.get_download_url(spec.key, spec.first_year)
    print(f"Nome: {spec.name}")
    print(f"Chave: {spec.key}")
    print(f"Prefixo: {spec.prefix}")
    print(f"Primeiro ano: {spec.first_year}")
    print(f"Arquivo por UF: {'sim' if spec.per_uf else 'não'}")
    print(f"URL de exemplo: {url}")


if __name__ == "__main__":
    main()
