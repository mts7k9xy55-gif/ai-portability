from pathlib import Path

from ai_portability.report import generate_report


def test_generate_report_includes_median_and_distribution(tmp_path: Path) -> None:
    dataset = tmp_path / "ai_portability_index_2026.json"
    dataset.write_text(
        '{"snapshot_year": 2026, "query": "topic:ai", "limit": 2, "scan_mode": "manifest+clone", "generated_at": "2026-03-16T00:00:00+00:00",'
        '"repositories": [{"repo":"a","stars":10,"lockin_score":10,"portability_score":90,"signals":{"triton":false}},'
        '{"repo":"b","stars":20,"lockin_score":70,"portability_score":30,"signals":{"triton":true}}]}',
        encoding="utf-8",
    )

    output = tmp_path / "report.md"
    generate_report(dataset_path=dataset, output_path=output)
    text = output.read_text(encoding="utf-8")

    assert "# AI CUDA Lock-in Report 2026" in text
    assert "Top 20 Most Locked Repositories" in text
    assert "Average Lock-in Score" in text
    assert "Median Lock-in Score" in text
    assert "## 4. Lock-in Distribution" in text
    assert "- 60-79: 1" in text
    assert "- Query: `topic:ai`" in text
    assert "- Scan mode: `manifest+clone`" in text
    assert "- Triton appears in 1 repositories, NCCL appears in 0, and custom CUDA kernels appear in 0." in text
    assert "- However, portability varies significantly across the benchmark set, with a, b landing at the portable end." in text
