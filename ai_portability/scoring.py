"""Scoring logic for CUDA lock-in and portability."""

from __future__ import annotations

import math
from typing import Mapping

MAX_SIGNAL_CONTRIBUTIONS: dict[str, int] = {
    "torch_cuda": 14,
    "cupy": 6,
    "cudnn": 10,
    "nccl": 12,
    "triton": 18,
    "cuda_malloc": 10,
    "cuda_memcpy": 10,
    "cuda_build": 8,
    "custom_kernel": 20,
}

SATURATION_COUNTS: dict[str, int] = {
    "torch_cuda": 50,
    "cupy": 10,
    "cudnn": 10,
    "nccl": 20,
    "triton": 30,
    "cuda_malloc": 10,
    "cuda_memcpy": 10,
    "cuda_build": 10,
    "custom_kernel": 20,
}


def _signal_count(value: int | bool | float | None) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    return max(0, int(value))


def compute_lockin_score(signals: Mapping[str, int | bool]) -> int:
    """Compute a bounded lock-in score from detected signal counts."""
    total = 0.0
    for key, max_points in MAX_SIGNAL_CONTRIBUTIONS.items():
        count = _signal_count(signals.get(key))
        if count <= 0:
            continue
        saturation = SATURATION_COUNTS[key]
        normalized = min(1.0, math.log1p(count) / math.log1p(saturation))
        total += max_points * normalized
    return max(0, min(100, round(total)))


def compute_portability_score(lockin_score: int) -> int:
    """Convert lock-in score into a portability score."""
    return max(0, 100 - max(0, lockin_score))
