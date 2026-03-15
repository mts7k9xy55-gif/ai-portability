"""AI Portability package."""

from .scoring import compute_lockin_score, compute_portability_score
from .scanner import scan_path, scan_repository

__all__ = [
    "compute_lockin_score",
    "compute_portability_score",
    "scan_path",
    "scan_repository",
]

__version__ = "0.1.0"

