"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

try:
    import typer

    try:
        from quantilica.cli.ui import (
            expand_years_cli,
            get_console,
            setup_rich_logging,
        )

        console = get_console()
    except ImportError:  # pragma: no cover - fallback sem quantilica-cli
        import logging

        from rich.console import Console

        console = Console()

        def setup_rich_logging(verbose: bool, console=None) -> None:  # noqa: ANN001
            """Fallback: logging básico sem RichHandler."""
            logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)

        def expand_years_cli(years, default_range=None, console=None):  # noqa: ANN001
            """Fallback de expansão de anos via quantilica-core.dates."""
            from quantilica.core.dates import expand_year_range

            specs = years or [default_range]
            return expand_year_range(*specs)

    _HAS_UI = True
except ImportError:
    _HAS_UI = False

from .client import TseClient
from .constants import DATASETS, DEFAULT_OUTPUT, DEFAULT_YEAR_RANGE

_DEFAULT_OUTPUT = Path(DEFAULT_OUTPUT)

if _HAS_UI:
    app = typer.Typer(help="Dados eleitorais do TSE (Tribunal Superior Eleitoral).")

    @app.command("list")
    def cmd_list() -> None:
        """Listar datasets disponíveis no ODSele."""
        setup_rich_logging(False, console=console)
        from rich.table import Table

        table = Table(show_header=True, header_style="bold")
        table.add_column("Dataset", style="cyan")
        table.add_column("Descrição", style="green")
        table.add_column("1º ano", justify="right")
        table.add_column("Por UF", justify="right")

        for spec in sorted(DATASETS.values(), key=lambda s: s.key):
            table.add_row(
                spec.key,
                spec.name,
                str(spec.first_year),
                "sim" if spec.per_uf else "não",
            )
        console.print(table)
        console.print(f"[bold]Total:[/bold] {len(DATASETS)} datasets disponíveis.")

    @app.command("sync")
    def cmd_sync(
        datasets: Annotated[
            list[str] | None,
            typer.Argument(help="Datasets a sincronizar. Omitir para baixar todos."),
        ] = None,
        years: Annotated[
            list[str] | None,
            typer.Option(
                "-y",
                "--years",
                help="Anos (ex: 2022) ou intervalos (2020:2022).",
            ),
        ] = None,
        output: Annotated[
            Path,
            typer.Option("-o", "--output", help="Diretório de saída"),
        ] = _DEFAULT_OUTPUT,
        force: Annotated[
            bool, typer.Option("--force", help="Re-baixar arquivos frescos")
        ] = False,
        verbose: Annotated[
            bool, typer.Option("--verbose", help="Logs detalhados")
        ] = False,
    ) -> None:
        """Baixar/atualizar dados do ODSele (tudo por padrão)."""
        setup_rich_logging(verbose, console=console)
        anos = expand_years_cli(
            years, default_range=DEFAULT_YEAR_RANGE, console=console
        )
        selections = datasets if datasets else sorted(DATASETS)
        client = TseClient()

        # Validação antecipada de nomes de dataset (anos são filtrados no sync).
        try:
            for dataset in selections:
                client.get_dataset(dataset)
        except ValueError as exc:
            console.print(f"[red]Erro:[/red] {exc}")
            raise typer.Exit(code=1) from None

        from rich.progress import (
            BarColumn,
            MofNCompleteColumn,
            Progress,
            SpinnerColumn,
            TextColumn,
            TimeElapsedColumn,
            TimeRemainingColumn,
        )

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        )
        ok_total = failed_total = skipped_total = 0
        with progress:
            task = progress.add_task("[cyan]Baixando datasets...[/cyan]", total=None)

            def on_done(filename: str, result: str) -> None:
                nonlocal ok_total, failed_total, skipped_total
                if result == "ok":
                    ok_total += 1
                elif result == "skipped":
                    skipped_total += 1
                else:
                    failed_total += 1
                progress.update(
                    task,
                    completed=ok_total + failed_total,
                    description=(
                        f"[cyan]{filename}[/cyan]  "
                        f"[green]{ok_total}✓[/green] [red]{failed_total}✗[/red]"
                    ),
                )

            ok, failed, skipped = client.sync(
                selections,
                anos,
                output_dir=output,
                force=force,
                on_done=on_done,
            )

        if failed:
            console.print(
                f"[yellow]⚠[/yellow]  {ok} OK · [red]{failed} falha(s)[/red]"
                f" · {skipped} skip"
            )
        else:
            console.print(
                f"[green]✓[/green]  [bold]{ok}[/bold] itens baixados."
                f" [dim]{skipped} skip[/dim]"
            )

    @app.command("info")
    def cmd_info(
        dataset: Annotated[
            str,
            typer.Argument(help="Nome canônico do dataset (veja 'list')."),
        ],
    ) -> None:
        """Exibir metadados de um dataset específico."""
        setup_rich_logging(False, console=console)
        from rich.panel import Panel

        client = TseClient()
        try:
            spec = client.get_dataset(dataset)
            url = client.get_download_url(spec.key, spec.first_year)
        except ValueError as exc:
            console.print(f"[red]Erro:[/red] {exc}")
            raise typer.Exit(code=1) from None
        console.print(
            Panel(
                f"[bold cyan]{spec.name}[/bold cyan]\n"
                f"Prefixo: [cyan]{spec.prefix}[/cyan]\n"
                f"Primeiro ano: [cyan]{spec.first_year}[/cyan]\n"
                f"Arquivo por UF: [cyan]{'sim' if spec.per_uf else 'não'}[/cyan]\n"
                f"[dim]{url}[/dim]",
                title=f"Dataset {spec.key}",
            )
        )

else:
    from . import cli as _cli

    # Fallback nativo: sem typer/rich, o entry point cai na CLI argparse.
    app = _cli.main  # type: ignore[assignment]
