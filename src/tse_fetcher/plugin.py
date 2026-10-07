"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated, Any

import typer
from quantilica.cli.sdk import CheckPlan, CheckPlanItem, FetcherApp
from quantilica.cli.ui import expand_years_cli, get_console, setup_rich_logging
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from .client import SyncPlanItem, TseClient
from .constants import DATASETS, DEFAULT_OUTPUT, DEFAULT_YEAR_RANGE

_DEFAULT_OUTPUT = Path(DEFAULT_OUTPUT)
console = get_console()

# Catálogo de grupos no schema do SDK (``FetcherApp.groups_dict``).
GROUPS: dict[str, dict[str, Any]] = {
    spec.key: {"name": spec.name} for spec in DATASETS.values()
}


def tse_list_datasets(group: str) -> list[dict[str, Any]]:
    """Hook de catálogo exigido pelo ``FetcherApp``.

    O TSE não publica um catálogo navegável por grupo: a expansão de
    arquivos (anos eleitorais e UFs) é feita pelo ``TseClient`` durante o
    ``sync``/``plan_sync``, então o hook não pré-enumerada entradas.

    Args:
        group (str): Chave canônica do grupo (dataset).

    Returns:
        list[dict[str, Any]]: Lista vazia por contrato.
    """
    return []


def tse_path_builder(
    output_dir: Path,
    entry: dict[str, Any],
    last_modified: dt.date | None = None,
) -> Path:
    """Montar o caminho destino de um arquivo (layout plano do CDN).

    Args:
        output_dir (Path): Diretório de saída.
        entry (dict[str, Any]): Entrada de dataset (chave ``id`` com o nome
            canônico do arquivo).
        last_modified (dt.date | None): Ignorado; o TSE não publica
            timestamps no nome do arquivo.

    Returns:
        Path: Caminho destino ``{output_dir}/{id}``.
    """
    return output_dir / str(entry.get("id", "unknown"))


fetcher = FetcherApp(
    name="tse-fetcher",
    help="Dados eleitorais do TSE (Tribunal Superior Eleitoral).",
    groups_dict=GROUPS,
    aliases_dict={},
    list_datasets=tse_list_datasets,
    path_builder=tse_path_builder,
    default_output=_DEFAULT_OUTPUT,
    build_default_commands=False,  # list/sync próprios (anos eleitorais e UF).
)

app = fetcher.app


def cmd_list() -> None:
    """Listar datasets disponíveis no ODSele."""
    setup_rich_logging(False, console=console)

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
    from_plan: Annotated[
        Path | None,
        typer.Option(
            "--from-plan",
            help="Baixar somente as entradas com ação 'download' de um plano "
            "gerado por 'check' (ignora datasets/anos).",
        ),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Listar arquivos a baixar sem executar download."
        ),
    ] = False,
) -> None:
    """Baixar/atualizar dados do ODSele (tudo por padrão)."""
    setup_rich_logging(verbose, console=console)
    client = TseClient()

    if from_plan is not None:
        try:
            plan = CheckPlan.from_json(from_plan.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            console.print(f"[red]Plano inválido:[/red] {exc}")
            raise typer.Exit(code=1) from None
        items = []
        for v in plan.items:
            if v.action != "download":
                continue
            e = v.entry
            spec = DATASETS.get(str(e.get("dataset", "")))
            items.append(
                SyncPlanItem(
                    dataset=str(e.get("dataset", "")),
                    dataset_name=spec.name if spec else str(e.get("dataset", "")),
                    ano=int(e.get("ano", 0)),
                    uf=e.get("uf"),
                    filename=str(e.get("filename", "")),
                    url=str(e.get("url", "")),
                    target=output / str(e.get("filename", "")),
                )
            )
        console.print(
            f"[dim]Plano {from_plan}: {len(items)} entrada(s) com ação "
            f"'download' de {len(plan.items)} verificada(s).[/dim]"
        )
        ok, failed = client.download_items(items, output)
        if failed:
            console.print(f"[yellow]⚠[/yellow]  {ok} OK · [red]{failed} falha(s)[/red]")
        else:
            console.print(f"[green]✓[/green]  [bold]{ok}[/bold] itens baixados.")
        return

    anos = expand_years_cli(years, default_range=DEFAULT_YEAR_RANGE, console=console)
    selections = datasets if datasets else sorted(DATASETS)

    # Validação antecipada de nomes de dataset (anos são filtrados no sync).
    try:
        for dataset in selections:
            client.get_dataset(dataset)
    except ValueError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from None

    if dry_run:
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

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )
    ok_total = failed_total = 0
    with progress:
        task = progress.add_task("[cyan]Baixando datasets...[/cyan]", total=None)

        def on_done(filename: str, result: str) -> None:
            nonlocal ok_total, failed_total
            if result == "ok":
                ok_total += 1
            elif result != "skipped":
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


def cmd_check(
    datasets: Annotated[
        list[str] | None,
        typer.Argument(help="Datasets a verificar. Omitir para verificar todos."),
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
    as_json: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Imprime o plano em JSON (para 'sync --from-plan').",
        ),
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Verificar remoto × local sem baixar (plano de freshness)."""
    setup_rich_logging(verbose, console=console)
    anos = expand_years_cli(years, default_range=DEFAULT_YEAR_RANGE, console=console)
    selections = datasets if datasets else sorted(DATASETS)
    client = TseClient()

    try:
        for dataset in selections:
            client.get_dataset(dataset)
    except ValueError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from None

    planned, skipped = client.plan_sync(selections, anos, output_dir=output)
    verdicts = [client.check_item(item) for item in planned]
    generated = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    plan = CheckPlan(
        fetcher="tse-fetcher",
        output_dir=str(output),
        generated_at=generated,
        items=[CheckPlanItem(**v) for v in verdicts],
    )
    if as_json:
        print(plan.to_json())
    else:
        plan.render_table()
    if skipped:
        console.print(f"[dim]{skipped} par(es) ignorado(s) fora da cobertura.[/dim]")


def cmd_info(
    dataset: Annotated[
        str,
        typer.Argument(help="Nome canônico do dataset (veja 'list')."),
    ],
) -> None:
    """Exibir metadados de um dataset específico."""
    setup_rich_logging(False, console=console)

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


fetcher.attach_command(cmd_list, name="list")
fetcher.attach_command(cmd_sync, name="sync")
fetcher.attach_command(cmd_check, name="check")
fetcher.attach_command(cmd_info, name="info")
