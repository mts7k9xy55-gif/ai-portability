"""Markdown report generation for AI Portability."""

from __future__ import annotations

from pathlib import Path
from statistics import mean, median
from typing import Any

from .crawler import current_index_year, default_report_path, load_dataset


def _format_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Repo | Stars | Lock-in | Portability |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['repo']} | {row.get('stars', 0)} | {row['lockin_score']} | {row['portability_score']} |"
        )
    return lines


def _build_observations(
    rows: list[dict[str, Any]], metadata: dict[str, Any] | None = None
) -> list[str]:
    if not rows:
        return ["- No repositories were analyzed."]

    triton_count = sum(1 for row in rows if row.get("signals", {}).get("triton"))
    nccl_count = sum(1 for row in rows if row.get("signals", {}).get("nccl"))
    custom_kernel_count = sum(
        1 for row in rows if row.get("signals", {}).get("custom_kernel")
    )
    most_locked = max(rows, key=lambda row: row["lockin_score"])
    most_portable = max(rows, key=lambda row: row["portability_score"])
    avg_lockin = mean(row["lockin_score"] for row in rows)
    scan_mode = (metadata or {}).get("scan_mode", "unknown")
    top_locked = sorted(rows, key=lambda row: row["lockin_score"], reverse=True)[:3]
    top_portable = sorted(
        rows, key=lambda row: row["portability_score"], reverse=True
    )[:3]
    locked_names = ", ".join(row["repo"] for row in top_locked)
    portable_names = ", ".join(row["repo"] for row in top_portable)

    return [
        f"- We analyzed {len(rows)} repositories with scan mode `{scan_mode}`.",
        f"- The average CUDA lock-in score is {avg_lockin:.2f}.",
        f"- Triton appears in {triton_count} repositories, NCCL appears in {nccl_count}, and custom CUDA kernels appear in {custom_kernel_count}.",
        f"- The highest lock-in cluster in this snapshot is {locked_names}.",
        f"- However, portability varies significantly across the benchmark set, with {portable_names} landing at the portable end.",
        f"- The most locked repository in this snapshot is {most_locked['repo']} with a score of {most_locked['lockin_score']}.",
        f"- The most portable repository in this snapshot is {most_portable['repo']} with a score of {most_portable['portability_score']}.",
    ]


def _distribution_lines(rows: list[dict[str, Any]]) -> list[str]:
    bins = [
        ("0-19", 0, 19),
        ("20-39", 20, 39),
        ("40-59", 40, 59),
        ("60-79", 60, 79),
        ("80-100", 80, 100),
    ]
    lines: list[str] = []
    for label, lower, upper in bins:
        count = sum(lower <= row["lockin_score"] <= upper for row in rows)
        lines.append(f"- {label}: {count}")
    return lines


def generate_report(
    dataset_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Generate a markdown report from a dataset file."""
    dataset = Path(dataset_path)
    metadata, rows = load_dataset(dataset)
    top_lockin = sorted(rows, key=lambda row: row["lockin_score"], reverse=True)[:20]
    top_portability = sorted(
        rows, key=lambda row: row["portability_score"], reverse=True
    )[:20]

    avg_lockin = mean(row["lockin_score"] for row in rows) if rows else 0
    avg_portability = mean(row["portability_score"] for row in rows) if rows else 0
    median_lockin = median(row["lockin_score"] for row in rows) if rows else 0
    median_portability = median(row["portability_score"] for row in rows) if rows else 0
    report_year = str(
        metadata.get("snapshot_year")
        or "".join(ch for ch in dataset.stem if ch.isdigit())
        or current_index_year()
    )
    summary_lines = [
        f"- Repositories analyzed: {len(rows)}",
        f"- Average Lock-in Score: {avg_lockin:.2f}",
        f"- Median Lock-in Score: {median_lockin:.2f}",
        f"- Average Portability Score: {avg_portability:.2f}",
        f"- Median Portability Score: {median_portability:.2f}",
    ]
    if metadata:
        summary_lines = [
            f"- Snapshot year: {metadata.get('snapshot_year', report_year)}",
            f"- Query: `{metadata.get('query', 'n/a')}`",
            f"- Requested limit: {metadata.get('limit', len(rows))}",
            f"- Scan mode: `{metadata.get('scan_mode', 'n/a')}`",
            f"- Generated at: {metadata.get('generated_at', 'n/a')}",
            *summary_lines,
        ]

    content: list[str] = [
        f"# AI CUDA Lock-in Report {report_year}",
        "",
        "## 1. Top 20 Most Locked Repositories",
        "",
        *_format_table(top_lockin),
        "",
        "## 2. Top 20 Most Portable Repositories",
        "",
        *_format_table(top_portability),
        "",
        "## 3. Summary Stats",
        "",
        *summary_lines,
        "",
        "## 4. Lock-in Distribution",
        "",
        *_distribution_lines(rows),
        "",
        "## 5. Key Observations",
        "",
        *_build_observations(rows, metadata),
    ]

    destination = (
        Path(output_path)
        if output_path is not None
        else default_report_path(int(report_year))
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(content) + "\n", encoding="utf-8")
    return destination
