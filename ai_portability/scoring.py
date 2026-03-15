"""Scoring logic for CUDA lock-in and portability."""

from __future__ import annotations

from typing import Mapping

WEIGHTS: dict[str, int] = {
    "torch_cuda": 2,
    "cupy": 2,
    "cudnn": 2,
    "nccl": 2,
    "triton": 3,
    "cuda_malloc": 2,
    "cuda_memcpy": 2,
    "custom_kernel": 4,
}


def compute_lockin_score(signals: Mapping[str, int | bool]) -> int:
    """Compute a bounded lock-in score from detected signals."""
    total = 0
    for key, weight in WEIGHTS.items():
        if signals.get(key):
            total += weight
    return max(0, min(100, total))


def compute_portability_score(lockin_score: int) -> int:
    """Convert lock-in score into a portability score."""
    return max(0, 100 - max(0, lockin_score))

