from ai_portability.scoring import compute_lockin_score, compute_portability_score


def test_compute_lockin_score_uses_expected_weights() -> None:
    score = compute_lockin_score(
        {
            "torch_cuda": True,
            "cudnn": True,
            "nccl": True,
            "triton": True,
            "custom_kernel": True,
        }
    )
    assert score == 13


def test_compute_portability_score_is_inverse_of_lockin() -> None:
    assert compute_portability_score(13) == 87
    assert compute_portability_score(120) == 0
