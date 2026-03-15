"""GitHub crawler for AI Portability."""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests import HTTPError

from .scanner import scan_repository

SEARCH_URL = "https://api.github.com/search/repositories"
CONTENT_URL = "https://api.github.com/repos/{repo}/contents/{path}"
DEFAULT_QUERY = "topic:machine-learning stars:>1000 language:python"
TOPIC_QUERIES = {
    "ai": "topic:machine-learning stars:>1000 language:python",
    "llm": "topic:llm stars:>500 language:python",
    "diffusion": "topic:diffusion stars:>200 language:python",
    "inference": "topic:inference stars:>500 language:python",
    "benchmark": "topic:inference stars:>500 language:python",
}
DEFAULT_FILE_PATHS = (
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements/base.txt",
    "requirements/dev.txt",
)


def _github_headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request_json(url: str, **kwargs: Any) -> requests.Response:
    response = requests.get(url, headers=_github_headers(), timeout=30, **kwargs)
    try:
        response.raise_for_status()
    except HTTPError as exc:
        if response.status_code == 403:
            raise RuntimeError(
                "GitHub API rate limit exceeded. Set GITHUB_TOKEN and rerun the command."
            ) from exc
        raise
    return response


def current_index_year() -> int:
    """Return the current UTC year for versioned index artifacts."""
    return datetime.now(timezone.utc).year


def default_dataset_path(year: int | None = None) -> Path:
    """Return the default versioned dataset path."""
    resolved_year = year or current_index_year()
    return Path(f"datasets/ai_portability_index_{resolved_year}.json")


def default_report_path(year: int | None = None) -> Path:
    """Return the default versioned report path."""
    resolved_year = year or current_index_year()
    return Path(f"report/AI_CUDA_Lockin_Report_{resolved_year}.md")


def resolve_query(query: str | None = None, topic: str | None = None) -> str:
    """Resolve explicit query or topic preset into a GitHub search query."""
    if query:
        return query
    if topic:
        try:
            return TOPIC_QUERIES[topic]
        except KeyError as exc:
            raise ValueError(
                f"Unknown topic preset: {topic}. Available presets: {', '.join(sorted(TOPIC_QUERIES))}"
            ) from exc
    return DEFAULT_QUERY


def fetch_top_repositories_page(
    page: int,
    per_page: int = 100,
    query: str = DEFAULT_QUERY,
) -> list[dict[str, Any]]:
    """Fetch one page of repository search results from GitHub."""
    response = _request_json(
        SEARCH_URL,
        params={
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        },
    )
    return response.json().get("items", [])


def fetch_top_repositories(limit: int = 25, query: str = DEFAULT_QUERY) -> list[dict[str, Any]]:
    """Fetch enough repositories to satisfy the requested limit."""
    results: list[dict[str, Any]] = []
    page = 1
    per_page = min(max(limit * 2, 50), 100)
    while len(results) < limit:
        items = fetch_top_repositories_page(page=page, per_page=per_page, query=query)
        if not items:
            break
        results.extend(items)
        page += 1
    return results[:limit]


def fetch_repo_file_texts(
    repo: str,
    branch: str | None = None,
    file_paths: tuple[str, ...] = DEFAULT_FILE_PATHS,
) -> dict[str, str] | None:
    """Fetch a lightweight set of manifest files from the GitHub contents API."""
    texts: dict[str, str] = {}
    params = {"ref": branch} if branch else None
    for file_path in file_paths:
        url = CONTENT_URL.format(repo=repo, path=file_path)
        response = requests.get(url, headers=_github_headers(), params=params, timeout=30)
        if response.status_code == 404:
            continue
        try:
            response.raise_for_status()
        except HTTPError:
            if response.status_code == 403:
                return None
            raise
        payload = response.json()
        if payload.get("type") != "file":
            continue
        content = payload.get("content", "")
        encoding = payload.get("encoding")
        if not content:
            continue
        if encoding == "base64":
            texts[file_path] = base64.b64decode(content).decode("utf-8", errors="ignore")
        else:
            texts[file_path] = content
    return texts


def crawl_repositories(
    limit: int = 25,
    output_path: str | Path | None = None,
    max_repo_size: int = 200_000,
    clone_fallback: bool = False,
    query: str | None = None,
    topic: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch, scan, and persist repository results."""
    resolved_query = resolve_query(query=query, topic=topic)
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    page = 1
    per_page = min(max(limit * 2, 50), 100)

    while len(results) < limit:
        repos = fetch_top_repositories_page(
            page=page, per_page=per_page, query=resolved_query
        )
        if not repos:
            break
        for repo in repos:
            if len(results) >= limit:
                break

            full_name = repo["full_name"]
            if full_name in seen:
                continue
            seen.add(full_name)

            if repo.get("size", 0) > max_repo_size:
                continue

            branch = repo.get("default_branch")
            file_texts = fetch_repo_file_texts(full_name, branch=branch)

            if file_texts:
                scan_result = scan_repository(full_name, file_texts=file_texts)
            elif clone_fallback or file_texts is None:
                scan_result = scan_repository(full_name)
            else:
                scan_result = scan_repository(full_name, file_texts={})

            scan_result["repo"] = full_name
            scan_result["stars"] = repo.get("stargazers_count", 0)
            scan_result["size"] = repo.get("size", 0)
            scan_result["html_url"] = repo.get("html_url")
            scan_result["description"] = repo.get("description")
            scan_result["last_updated"] = (
                repo.get("pushed_at") or repo.get("updated_at") or ""
            )[:10]
            scan_result["query"] = resolved_query
            results.append(scan_result)
        page += 1

    destination = Path(output_path) if output_path is not None else default_dataset_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
