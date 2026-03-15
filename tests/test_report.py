from pathlib import Path

from ai_portability.report import generate_report


def test_generate_report_includes_median_and_distribution(tmp_path: Path) -> None:
    dataset = tmp_path / "ai_portability_index_2026.json"
    dataset.write_text(
        '[{"repo":"a","stars":10,"lockin_score":10,"portability_score":90,"signals":{"triton":false}},'
        '{"repo":"b","stars":20,"lockin_score":70,"portability_score":30,"signals":{"triton":true}}]',
        encoding="utf-8",
    )

    output = tmp_path / "report.md"
    generate_report(dataset_path=dataset, output_path=output)
    text = output.read_text(encoding="utf-8")

    assert "# AI CUDA Lock-in Report 2026" in text
    assert "Median lock-in score" in text
    assert "## 4. Distribution" in text
    assert "- 60-79: 1" in text
