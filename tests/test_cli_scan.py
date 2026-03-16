from typer.testing import CliRunner

import ai_portability.cli as cli


def test_scan_prints_backend_compatibility(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "scan_repository",
        lambda repo: {
            "repo": repo,
            "lockin_score": 42,
            "portability_score": 58,
            "signals": {"torch_cuda": True},
            "backend_compatibility": {
                "cuda": True,
                "rocm": False,
                "metal": True,
                "oneapi": False,
                "cpu": True,
            },
        },
    )

    result = CliRunner().invoke(cli.app, ["scan", "demo/repo"])

    assert result.exit_code == 0
    assert "Backend Compatibility:" in result.stdout
    assert "- metal: True" in result.stdout
