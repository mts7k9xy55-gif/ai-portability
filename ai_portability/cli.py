"""Typer CLI entrypoint for AI Portability."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from .crawler import (
    TOPIC_QUERIES,
    crawl_repositories,
    default_dataset_path,
    default_report_path,
)
from .report import generate_report
from .scanner import scan_repository

app = typer.Typer(help="Measure CUDA lock-in in AI repositories.")


@app.command("scan")
def scan_command(
    repo: str = typer.Argument(..., help="GitHub repo slug or local path."),
    json_output: Path | None = typer.Option(
        None, "--json-output", help="Optional file path to save the JSON scan result."
    ),
) -> None:
    """Scan a single repository."""
    result = scan_repository(repo)
    typer.echo(f"Repository: {result['repo']}")
    typer.echo(f"CUDA Lock-in Score: {result['lockin_score']}")
    typer.echo(f"Portability Score: {result['portability_score']}")
    typer.echo("Signals:")
    for key, value in result["signals"].items():
        if value:
            typer.echo(f"- {key}: {value}")
    if json_output is not None:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        typer.echo(f"Saved JSON to {json_output}")


@app.command("crawl")
def crawl_command(
    limit: int = typer.Option(25, min=1, max=100, help="Number of repos to scan."),
    output: Path = typer.Option(
        default_dataset_path(),
        "--output",
        help="Where to save the dataset.",
    ),
    query: str | None = typer.Option(
        None,
        "--query",
        help="Raw GitHub repository search query.",
    ),
    topic: str | None = typer.Option(
        None,
        "--topic",
        help=f"Topic preset ({', '.join(sorted(TOPIC_QUERIES))}).",
    ),
    max_repo_size: int = typer.Option(
        200_000,
        "--max-repo-size",
        help="Skip repositories larger than this GitHub size value.",
    ),
    clone_fallback: bool = typer.Option(
        False,
        "--clone-fallback/--no-clone-fallback",
        help="Clone only when manifest-only scanning is insufficient.",
    ),
) -> None:
    """Fetch and scan top AI repositories from GitHub."""
    results = crawl_repositories(
        limit=limit,
        output_path=output,
        max_repo_size=max_repo_size,
        clone_fallback=clone_fallback,
        query=query,
        topic=topic,
    )
    typer.echo(f"Scanned {len(results)} repositories.")
    typer.echo(f"Saved dataset to {output}")


@app.command("snapshot")
def snapshot_command(
    output: Path = typer.Option(
        default_dataset_path(),
        "--output",
        help="Where to save the benchmark snapshot dataset.",
    ),
    report_output: Path = typer.Option(
        default_report_path(),
        "--report-output",
        help="Where to save the benchmark snapshot report.",
    ),
    clone_fallback: bool = typer.Option(
        False,
        "--clone-fallback/--no-clone-fallback",
        help="Clone only when manifest-only scanning is insufficient.",
    ),
) -> None:
    """Generate the canonical yearly AI Portability Index snapshot."""
    results = crawl_repositories(
        limit=25,
        output_path=output,
        max_repo_size=200_000,
        clone_fallback=clone_fallback,
        topic="benchmark",
    )
    destination = generate_report(dataset_path=output, output_path=report_output)
    typer.echo(f"Scanned {len(results)} repositories.")
    typer.echo(f"Saved snapshot dataset to {output}")
    typer.echo(f"Saved snapshot report to {destination}")


@app.command("report")
def report_command(
    dataset_path: Path = typer.Argument(
        default_dataset_path(),
        help="Path to the crawler JSON dataset.",
    ),
    output: Path = typer.Option(
        default_report_path(),
        "--output",
        help="Where to save the markdown report.",
    ),
) -> None:
    """Generate a report from a dataset file."""
    destination = generate_report(dataset_path=dataset_path, output_path=output)
    typer.echo(f"Saved report to {destination}")


def main() -> None:
    """CLI wrapper for the package entry point."""
    app()


if __name__ == "__main__":
    main()
