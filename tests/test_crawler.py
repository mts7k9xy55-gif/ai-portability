import json
from pathlib import Path

import ai_portability.crawler as crawler
import requests


def test_crawl_repositories_paginates_until_limit(
    monkeypatch, tmp_path: Path
) -> None:
    pages = {
        1: [
            {
                "full_name": "org/too-big",
                "size": 300000,
                "stargazers_count": 100,
                "html_url": "https://github.com/org/too-big",
                "description": "skip",
                "default_branch": "main",
            },
            {
                "full_name": "org/one",
                "size": 10,
                "stargazers_count": 10,
                "html_url": "https://github.com/org/one",
                "description": "one",
                "default_branch": "main",
            },
        ],
        2: [
            {
                "full_name": "org/two",
                "size": 10,
                "stargazers_count": 20,
                "html_url": "https://github.com/org/two",
                "description": "two",
                "default_branch": "main",
            }
        ],
        3: [],
    }

    def fake_fetch_page(
        page: int, per_page: int = 100, query: str = crawler.DEFAULT_QUERY
    ):
        return pages[page]

    def fake_fetch_texts(
        repo: str, branch: str | None = None, file_paths=crawler.DEFAULT_FILE_PATHS
    ):
        return {"requirements.txt": "cupy\n"} if repo.endswith(("one", "two")) else {}

    def fake_scan(repo: str, file_texts=None):
        return {
            "repo": repo,
            "source": f"github:{repo}",
            "scan_mode": "manifest",
            "signals": {"cupy": True},
            "signal_counts": {"cupy": 1},
            "detected_dependencies": ["cupy"],
            "evidence": {"cupy": ["requirements.txt"]},
            "lockin_score": 2,
            "portability_score": 98,
        }

    monkeypatch.setattr(crawler, "fetch_top_repositories_page", fake_fetch_page)
    monkeypatch.setattr(crawler, "fetch_repo_file_texts", fake_fetch_texts)
    monkeypatch.setattr(crawler, "scan_repository", fake_scan)

    output = tmp_path / "dataset.json"
    result = crawler.crawl_repositories(limit=2, output_path=output, max_repo_size=200000)

    assert [row["repo"] for row in result] == ["org/one", "org/two"]
    assert json.loads(output.read_text(encoding="utf-8"))[1]["stars"] == 20


def test_resolve_query_prefers_explicit_query() -> None:
    assert crawler.resolve_query(query="stars:>1", topic="llm") == "stars:>1"


def test_resolve_query_uses_topic_preset() -> None:
    assert crawler.resolve_query(topic="llm") == crawler.TOPIC_QUERIES["llm"]


def test_benchmark_topic_matches_inference_preset() -> None:
    assert crawler.TOPIC_QUERIES["benchmark"] == crawler.TOPIC_QUERIES["inference"]


def test_request_json_surfaces_rate_limit_guidance(monkeypatch) -> None:
    response = requests.Response()
    response.status_code = 403
    response.url = "https://api.github.com/search/repositories"

    monkeypatch.setattr(crawler.requests, "get", lambda *args, **kwargs: response)

    try:
        crawler._request_json("https://api.github.com/search/repositories")
    except RuntimeError as exc:
        assert "GITHUB_TOKEN" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError for rate-limited response")


def test_crawl_repositories_includes_last_updated_and_query(
    monkeypatch, tmp_path: Path
) -> None:
    def fake_fetch_page(
        page: int, per_page: int = 100, query: str = crawler.DEFAULT_QUERY
    ):
        if page > 1:
            return []
        return [
            {
                "full_name": "org/one",
                "size": 10,
                "stargazers_count": 10,
                "html_url": "https://github.com/org/one",
                "description": "one",
                "default_branch": "main",
                "pushed_at": "2026-03-01T10:00:00Z",
            }
        ]

    monkeypatch.setattr(crawler, "fetch_top_repositories_page", fake_fetch_page)
    monkeypatch.setattr(
        crawler, "fetch_repo_file_texts", lambda repo, branch=None: {"pyproject.toml": ""}
    )
    monkeypatch.setattr(
        crawler,
        "scan_repository",
        lambda repo, file_texts=None: {
            "repo": repo,
            "source": f"github:{repo}",
            "scan_mode": "manifest",
            "signals": {},
            "signal_counts": {},
            "detected_dependencies": [],
            "evidence": {},
            "lockin_score": 0,
            "portability_score": 100,
        },
    )

    output = tmp_path / "dataset.json"
    result = crawler.crawl_repositories(
        limit=1, output_path=output, topic="llm", max_repo_size=200000
    )

    assert result[0]["last_updated"] == "2026-03-01"
    assert result[0]["query"] == crawler.TOPIC_QUERIES["llm"]


def test_crawl_repositories_falls_back_to_clone_on_rate_limit(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        crawler,
        "fetch_top_repositories_page",
        lambda page, per_page=100, query=crawler.DEFAULT_QUERY: []
        if page > 1
        else [
            {
                "full_name": "org/rate-limited",
                "size": 10,
                "stargazers_count": 5,
                "html_url": "https://github.com/org/rate-limited",
                "description": "rate limited",
                "default_branch": "main",
                "pushed_at": "2026-03-04T10:00:00Z",
            }
        ],
    )
    monkeypatch.setattr(crawler, "fetch_repo_file_texts", lambda repo, branch=None: None)
    monkeypatch.setattr(
        crawler,
        "scan_repository",
        lambda repo, file_texts=None: {
            "repo": repo,
            "source": f"github:{repo}",
            "scan_mode": "clone" if file_texts is None else "manifest",
            "signals": {},
            "signal_counts": {},
            "detected_dependencies": [],
            "evidence": {},
            "lockin_score": 0,
            "portability_score": 100,
        },
    )

    output = tmp_path / "dataset.json"
    result = crawler.crawl_repositories(limit=1, output_path=output)

    assert result[0]["scan_mode"] == "clone"
