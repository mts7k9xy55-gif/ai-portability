"""Repository scanner for CUDA lock-in signals."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from os import environ
from subprocess import CalledProcessError, run
from typing import Any, Mapping
from urllib.parse import urlparse

from .scoring import compute_lockin_score, compute_portability_score

FILE_PATTERNS = (
    "*.py",
    "*.c",
    "*.cc",
    "*.cpp",
    "*.cu",
    "*.cuh",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
)

SIGNAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "torch_cuda": re.compile(r"\btorch\.cuda\b"),
    "cupy": re.compile(r"\bcupy\b"),
    "cudnn": re.compile(r"\bcudnn\b", re.IGNORECASE),
    "nccl": re.compile(r"\bnccl\b", re.IGNORECASE),
    "triton": re.compile(r"\btriton\b"),
    "cuda_malloc": re.compile(r"\bcudaMalloc\b"),
    "cuda_memcpy": re.compile(r"\bcudaMemcpy\b"),
}
CUSTOM_KERNEL_PATTERNS = (
    re.compile(r"__global__\s+void"),
    re.compile(r"torch\.utils\.cpp_extension"),
    re.compile(r"\bload_inline\b"),
)


def normalize_repo_input(repo: str) -> str:
    """Normalize GitHub URLs into owner/repo form."""
    if repo.startswith(("http://", "https://")):
        parsed = urlparse(repo)
        if parsed.netloc != "github.com":
            raise ValueError(f"Unsupported repository URL: {repo}")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {repo}")
        owner, name = parts[0], parts[1]
        if name.endswith(".git"):
            name = name[:-4]
        return f"{owner}/{name}"
    return repo.removesuffix(".git").strip()


def _iter_scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in FILE_PATTERNS:
        files.extend(path for path in root.rglob(pattern) if path.is_file())
    return sorted(set(files))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _clone_repo(repo: str, destination: Path) -> Path:
    repo_url = f"https://github.com/{repo}.git"
    git_env = dict(environ)
    git_env["GIT_LFS_SKIP_SMUDGE"] = "1"
    try:
        run(
            [
                "git",
                "-c",
                "filter.lfs.smudge=",
                "-c",
                "filter.lfs.process=",
                "-c",
                "filter.lfs.required=false",
                "clone",
                "--depth",
                "1",
                repo_url,
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
            env=git_env,
        )
    except CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"Failed to clone {repo}: {stderr}") from exc
    return destination


def _build_result(
    repo_name: str,
    source: str,
    signal_counts: Mapping[str, int],
    evidence: Mapping[str, list[str]],
    scan_mode: str,
) -> dict[str, Any]:
    signals = {key: bool(value) for key, value in signal_counts.items()}
    lockin_score = compute_lockin_score(signals)
    portability_score = compute_portability_score(lockin_score)
    detected = [key for key, enabled in signals.items() if enabled]
    return {
        "repo": repo_name,
        "source": source,
        "scan_mode": scan_mode,
        "signals": signals,
        "signal_counts": dict(signal_counts),
        "detected_dependencies": sorted(detected),
        "evidence": {key: paths for key, paths in evidence.items() if paths},
        "lockin_score": lockin_score,
        "portability_score": portability_score,
    }


def scan_file_texts(
    file_texts: Mapping[str, str],
    repo_name: str,
    source: str,
    scan_mode: str = "manifest",
) -> dict[str, Any]:
    """Scan an in-memory file mapping and return structured CUDA lock-in signals."""
    signal_counts = {key: 0 for key in SIGNAL_PATTERNS}
    signal_counts["custom_kernel"] = 0
    evidence: dict[str, list[str]] = {key: [] for key in signal_counts}

    for relative, text in file_texts.items():
        for signal_name, pattern in SIGNAL_PATTERNS.items():
            matches = list(pattern.finditer(text))
            if matches:
                signal_counts[signal_name] += len(matches)
                evidence[signal_name].append(relative)

        custom_hits = sum(1 for pattern in CUSTOM_KERNEL_PATTERNS if pattern.search(text))
        if Path(relative).suffix in {".cu", ".cuh"}:
            custom_hits += 1
        if custom_hits:
            signal_counts["custom_kernel"] += custom_hits
            evidence["custom_kernel"].append(relative)

    return _build_result(repo_name, source, signal_counts, evidence, scan_mode)


def scan_path(path: str | Path, repo_name: str | None = None) -> dict[str, Any]:
    """Scan a local repository path and return structured CUDA lock-in signals."""
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    file_texts = {
        file_path.relative_to(root).as_posix(): _read_text(file_path)
        for file_path in _iter_scan_files(root)
    }
    file_texts = {name: text for name, text in file_texts.items() if text}
    return scan_file_texts(
        file_texts,
        repo_name=repo_name or root.name,
        source=str(root),
        scan_mode="clone",
    )


def scan_repository(repo: str, file_texts: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Scan either a local path, a GitHub repo slug, or a GitHub URL."""
    candidate = Path(repo).expanduser()
    if candidate.exists():
        return scan_path(candidate)

    normalized_repo = normalize_repo_input(repo)
    if file_texts is not None:
        return scan_file_texts(
            file_texts,
            repo_name=normalized_repo,
            source=f"github:{normalized_repo}",
            scan_mode="manifest",
        )

    with tempfile.TemporaryDirectory(prefix="ai-portability-scan-") as temp_dir:
        checkout_path = _clone_repo(
            normalized_repo, Path(temp_dir) / normalized_repo.replace("/", "-")
        )
        return scan_path(checkout_path, repo_name=normalized_repo)
