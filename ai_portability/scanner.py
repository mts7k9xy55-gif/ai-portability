"""Repository scanner for CUDA lock-in signals."""

from __future__ import annotations

import re
import tempfile
from os import environ
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Any, Mapping
from urllib.parse import urlparse

from .scoring import compute_lockin_score, compute_portability_score

FILE_PATTERNS = (
    "*.py",
    "*.c",
    "*.cc",
    "*.cpp",
    "*.cxx",
    "*.h",
    "*.hh",
    "*.hpp",
    "*.cu",
    "*.cuh",
    "*.metal",
    "*.ttir",
    "*.ttgir",
    "*.triton",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "CMakeLists.txt",
    "Makefile",
    "Dockerfile",
    "BUILD",
    "BUILD.bazel",
    "meson.build",
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
TRITON_KERNEL_PATTERNS = (
    re.compile(r"@triton\.jit"),
    re.compile(r"\btriton\.language\b"),
    re.compile(r"\bimport\s+triton(?:\.language)?\b"),
    re.compile(r"\bfrom\s+triton(?:\.language)?\s+import\b"),
)
CUSTOM_KERNEL_PATTERNS = (
    re.compile(r"__global__\s+void"),
    re.compile(r"torch\.utils\.cpp_extension"),
    re.compile(r"\bload_inline\b"),
    re.compile(r"\bCUDAExtension\b"),
    re.compile(r"\bTORCH_EXTENSION_NAME\b"),
)
CUDA_BUILD_PATTERNS = (
    re.compile(r"\bCUDAExtension\b"),
    re.compile(r"\bfind_package\s*\(\s*CUDA\b", re.IGNORECASE),
    re.compile(r"\benable_language\s*\(\s*CUDA\b", re.IGNORECASE),
    re.compile(r"\bproject\s*\(.*LANGUAGES[^)]*CUDA", re.IGNORECASE),
    re.compile(r"\bnvcc\b"),
    re.compile(r"\bcudart\b", re.IGNORECASE),
    re.compile(r"\bTORCH_CUDA_ARCH_LIST\b"),
)
BACKEND_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "rocm": (
        re.compile(r"\brocm\b", re.IGNORECASE),
        re.compile(r"\bhip(?:cc|ify|Malloc|Memcpy|Module|Launch)?\b"),
        re.compile(r"\btorch\.version\.hip\b"),
        re.compile(r"\brocblas\b", re.IGNORECASE),
        re.compile(r"\bmiopen\b", re.IGNORECASE),
        re.compile(r"\brccl\b", re.IGNORECASE),
    ),
    "metal": (
        re.compile(r"\btorch\.backends\.mps\b"),
        re.compile(r"\btorch\.mps\b"),
        re.compile(r"\bmlx\b"),
        re.compile(r"\bmetal(?:performance shaders)?\b", re.IGNORECASE),
    ),
    "oneapi": (
        re.compile(r"\boneapi\b", re.IGNORECASE),
        re.compile(r"\bintel_extension_for_pytorch\b"),
        re.compile(r"\bxpu\b"),
        re.compile(r"\bdpcpp\b", re.IGNORECASE),
        re.compile(r"\bsycl\b", re.IGNORECASE),
        re.compile(r"\blevel[-_ ]zero\b", re.IGNORECASE),
    ),
    "cpu_only": (
        re.compile(r"\bcpu[-_ ]?only\b", re.IGNORECASE),
        re.compile(r"\bonnxruntime\b", re.IGNORECASE),
        re.compile(r"\bopenvino\b", re.IGNORECASE),
        re.compile(r"\bdeepsparse\b", re.IGNORECASE),
        re.compile(r"\bggml\b", re.IGNORECASE),
    ),
}
IMPORT_ONLY_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "torch_cuda": (
        re.compile(r"^\s*import\s+torch\.cuda(?:\s+as\s+\w+)?\s*$"),
        re.compile(r"^\s*from\s+torch(?:\.\w+)*\s+import\s+cuda\s*$"),
    ),
    "triton": (
        re.compile(r"^\s*import\s+triton(?:\.language)?(?:\s+as\s+\w+)?\s*$"),
        re.compile(r"^\s*from\s+triton(?:\.language)?\s+import\s+.+$"),
    ),
}
CUDA_KERNEL_SUFFIXES = {".cu", ".cuh"}
TRITON_KERNEL_SUFFIXES = {".ttir", ".ttgir", ".triton"}
BUILD_FILE_NAMES = {
    "cmakelists.txt",
    "makefile",
    "dockerfile",
    "build",
    "build.bazel",
    "meson.build",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
}
SKIP_DIR_NAMES = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "doc",
    "vendor",
    "third_party",
    "tests",
    "test",
    "benchmarks",
}


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
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts[:-1]
        if any(part in SKIP_DIR_NAMES for part in relative_parts):
            continue
        if path.name in BUILD_FILE_NAMES or any(path.match(pattern) for pattern in FILE_PATTERNS):
            files.append(path)
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
    backend_signal_counts: Mapping[str, int],
    backend_evidence: Mapping[str, list[str]],
    scan_mode: str,
) -> dict[str, Any]:
    signals = {key: bool(value) for key, value in signal_counts.items()}
    backend_signals = {key: bool(value) for key, value in backend_signal_counts.items()}
    lockin_score = compute_lockin_score(signal_counts)
    portability_score = compute_portability_score(lockin_score)
    detected = [key for key, enabled in signals.items() if enabled]
    return {
        "repo": repo_name,
        "source": source,
        "scan_mode": scan_mode,
        "signals": signals,
        "signal_counts": dict(signal_counts),
        "backend_signals": backend_signals,
        "backend_signal_counts": dict(backend_signal_counts),
        "backend_compatibility": {
            "cuda": lockin_score > 0,
            "rocm": backend_signals["rocm"],
            "metal": backend_signals["metal"],
            "oneapi": backend_signals["oneapi"],
            "cpu": backend_signals["cpu_only"],
        },
        "detected_dependencies": sorted(detected),
        "evidence": {key: paths for key, paths in evidence.items() if paths},
        "backend_evidence": {
            key: paths for key, paths in backend_evidence.items() if paths
        },
        "lockin_score": lockin_score,
        "portability_score": portability_score,
    }


def _count_signal_matches(signal_name: str, text: str) -> int:
    if signal_name == "triton":
        return sum(len(pattern.findall(text)) for pattern in TRITON_KERNEL_PATTERNS)

    pattern = SIGNAL_PATTERNS[signal_name]
    if signal_name not in IMPORT_ONLY_PATTERNS:
        return len(pattern.findall(text))

    total = 0
    for line in text.splitlines():
        if not pattern.search(line):
            continue
        if any(ignore.search(line) for ignore in IMPORT_ONLY_PATTERNS[signal_name]):
            total += 1
        else:
            total += len(pattern.findall(line))
    return total


def _append_evidence(store: dict[str, list[str]], key: str, relative: str) -> None:
    if relative not in store[key]:
        store[key].append(relative)


def scan_file_texts(
    file_texts: Mapping[str, str],
    repo_name: str,
    source: str,
    scan_mode: str = "manifest",
) -> dict[str, Any]:
    """Scan an in-memory file mapping and return structured CUDA lock-in signals."""
    signal_counts = {key: 0 for key in SIGNAL_PATTERNS}
    signal_counts["custom_kernel"] = 0
    signal_counts["cuda_build"] = 0
    evidence: dict[str, list[str]] = {key: [] for key in signal_counts}
    backend_signal_counts = {key: 0 for key in BACKEND_PATTERNS}
    backend_evidence: dict[str, list[str]] = {key: [] for key in BACKEND_PATTERNS}

    for relative, text in file_texts.items():
        path = Path(relative)
        lower_name = path.name.lower()
        for signal_name in SIGNAL_PATTERNS:
            match_count = _count_signal_matches(signal_name, text)
            if match_count:
                signal_counts[signal_name] += match_count
                _append_evidence(evidence, signal_name, relative)

        triton_file_hits = int(path.suffix.lower() in TRITON_KERNEL_SUFFIXES)
        if triton_file_hits:
            signal_counts["triton"] += triton_file_hits
            _append_evidence(evidence, "triton", relative)

        build_hits = sum(1 for pattern in CUDA_BUILD_PATTERNS if pattern.search(text))
        if lower_name in BUILD_FILE_NAMES and build_hits:
            signal_counts["cuda_build"] += build_hits
            _append_evidence(evidence, "cuda_build", relative)

        custom_hits = sum(1 for pattern in CUSTOM_KERNEL_PATTERNS if pattern.search(text))
        if path.suffix.lower() in CUDA_KERNEL_SUFFIXES:
            custom_hits += 1
        if custom_hits:
            signal_counts["custom_kernel"] += custom_hits
            _append_evidence(evidence, "custom_kernel", relative)

        for backend_name, patterns in BACKEND_PATTERNS.items():
            match_count = sum(len(pattern.findall(text)) for pattern in patterns)
            if path.suffix.lower() == ".metal" and backend_name == "metal":
                match_count += 1
            if match_count:
                backend_signal_counts[backend_name] += match_count
                _append_evidence(backend_evidence, backend_name, relative)

    return _build_result(
        repo_name,
        source,
        signal_counts,
        evidence,
        backend_signal_counts,
        backend_evidence,
        scan_mode,
    )


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
