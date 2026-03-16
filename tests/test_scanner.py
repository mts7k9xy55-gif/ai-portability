from pathlib import Path

from ai_portability.scanner import normalize_repo_input, scan_path


def test_scanner_detects_cuda_signals(tmp_path: Path) -> None:
    (tmp_path / "module.py").write_text(
        "import torch\n"
        "torch.cuda.is_available()\n"
        "import cupy\n"
        "import triton\n"
        "backend = 'cudnn'\n"
        "dist = 'nccl'\n",
        encoding="utf-8",
    )
    (tmp_path / "kernel.cu").write_text(
        "__global__ void kernel() {}\n"
        "cudaMalloc(ptr, 1);\n"
        "cudaMemcpy(dst, src, 1, 0);\n",
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text("cupy-cuda12x\n", encoding="utf-8")
    (tmp_path / "CMakeLists.txt").write_text(
        "project(demo LANGUAGES CUDA CXX)\nfind_package(CUDA REQUIRED)\n",
        encoding="utf-8",
    )

    result = scan_path(tmp_path, repo_name="demo/repo")

    assert result["repo"] == "demo/repo"
    assert result["signals"]["torch_cuda"] is True
    assert result["signals"]["cupy"] is True
    assert result["signals"]["triton"] is True
    assert result["signals"]["cudnn"] is True
    assert result["signals"]["nccl"] is True
    assert result["signals"]["cuda_malloc"] is True
    assert result["signals"]["cuda_memcpy"] is True
    assert result["signals"]["cuda_build"] is True
    assert result["signals"]["custom_kernel"] is True
    assert result["signal_counts"]["torch_cuda"] >= 1
    assert result["lockin_score"] > 0
    assert result["portability_score"] < 100


def test_scanner_detects_alternate_backends(tmp_path: Path) -> None:
    (tmp_path / "backends.py").write_text(
        "import torch\n"
        "torch.backends.mps.is_available()\n"
        "import intel_extension_for_pytorch\n"
        "backend = 'rocm'\n"
        "engine = 'deepsparse'\n",
        encoding="utf-8",
    )
    (tmp_path / "kernel.ttir").write_text("// triton ir kernel\n", encoding="utf-8")
    (tmp_path / "shader.metal").write_text("kernel void demo() {}\n", encoding="utf-8")

    result = scan_path(tmp_path, repo_name="demo/repo")

    assert result["signals"]["triton"] is True
    assert result["backend_signals"]["rocm"] is True
    assert result["backend_signals"]["metal"] is True
    assert result["backend_signals"]["oneapi"] is True
    assert result["backend_signals"]["cpu_only"] is True
    assert result["backend_compatibility"]["metal"] is True
    assert result["backend_compatibility"]["cpu"] is True


def test_normalize_repo_input_accepts_github_urls() -> None:
    assert (
        normalize_repo_input("https://github.com/vllm-project/vllm")
        == "vllm-project/vllm"
    )
