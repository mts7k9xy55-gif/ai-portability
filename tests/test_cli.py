from pathlib import Path

from typer.testing import CliRunner

import ai_portability.cli as cli


def test_snapshot_accepts_topic_and_limit(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_crawl_repositories(**kwargs):
        captured.update(kwargs)
        return [{"repo": "org/one", "lockin_score": 1, "portability_score": 99}]

    def fake_generate_report(dataset_path, output_path=None):
        Path(output_path).write_text("# report\n", encoding="utf-8")
        return Path(output_path)

    monkeypatch.setattr(cli, "crawl_repositories", fake_crawl_repositories)
    monkeypatch.setattr(cli, "generate_report", fake_generate_report)

    runner = CliRunner()
    dataset_path = tmp_path / "snapshot.json"
    report_path = tmp_path / "report.md"
    result = runner.invoke(
        cli.app,
        [
            "snapshot",
            "--topic",
            "ai",
            "--limit",
            "5",
            "--clone-fallback",
            "--output",
            str(dataset_path),
            "--report-output",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["topic"] == "ai"
    assert captured["limit"] == 5
    assert captured["clone_fallback"] is True
