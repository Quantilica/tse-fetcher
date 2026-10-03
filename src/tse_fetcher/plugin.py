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
        # Fallback: sem `quantilica-cli` os stubs abaixo recriam uma
        # superfície de API compatível com a UI do hub, permitindo que
        # o pacote rode standalone apontando para a `Console` local do
        # Rich e para a expansão de anos canônica de `quantilica-core`.
        import logging

        from rich.console import Console

        console = Console()

        def setup_rich_logging(verbose: bool, console=None) -> None:  # noqa: ANN001
            """Stub de degradação: logging básico, sem ``RichHandler``.

            Args:
                verbose (bool): Nível verbose (DEBUG) ou padrão (WARNING).
                console (Console | None): Ignorado; mantido pela paridade
                    de assinatura com ``quantilica.cli.ui``.
            """
            logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)

        def expand_years_cli(years, default_range=None, console=None):  # noqa: ANN001
            """Stub de degradação: expansão de anos via ``quantilica-core``.

            Args:
                years (list[str] | None): Anos/intervalos informados.
                default_range (str | None): Faixa padrão quando ``years``
                    for vazio (ex.: ``"2018:2026"``).
                console (Console | None): Ignorado; mantido pela paridade
                    de assinatura com ``quantilica.cli.ui``. Avisos de
                    formato inválido vão pelo logging, não pelo Rich.

            Returns:
                list[int]: Anos eleitorais expandidos e validados.
            """
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
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run", help="Listar arquivos a baixar sem executar download."
            ),
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

        if dry_run:
            from rich.table import Table

            items, skipped = client.plan_sync(selections, anos, output_dir=output)
            table = Table(show_header=True, header_style="bold")
            table.add_column("Dataset", style="cyan")
            table.add_column("Ano", justify="right")
            table.add_column("UF", style="magenta")
            table.add_column("Arquivo", style="green")
            table.add_column("URL", style="dim")
            for item in items:
                table.add_row(
                    item.dataset,
                    str(item.ano),
                    item.uf or "—",
                    item.filename,
                    item.url,
                )
            console.print(table)
            console.print(
                f"\n[bold]Total:[/bold] {len(items)} arquivo(s) planejados para "
                f"download. {skipped} par(es) ignorado(s) fora da cobertura."
            )
            return

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

    # Fallback nativo (degradação graciosa): quando `typer` não está
    # disponível (instalação minimalista sem os extras de UI do hub),
    # o entry point `quantilica.fetchers` aponta para a CLI argparse
    # nativa (`tse_fetcher.cli.main`). Assim `quantilica tse ...`
    # continua funcional com o mesmo vocabulário de subcomandos —
    # `list`, `sync` e `info` — incluindo `sync --dry-run`, apenas
    # sem a renderização Rich de tabelas/progresso. Nenhuma importação
    # de `quantilica-cli` é feita: o pacote permanece puro, dependendo
    # estritamente de `quantilica-core`.
    app = _cli.main  # type: ignore[assignment]
