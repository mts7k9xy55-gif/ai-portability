from ai_portability.scoring import compute_lockin_score, compute_portability_score


def test_compute_lockin_score_supports_boolean_signals() -> None:
    score = compute_lockin_score(
        {
            "torch_cuda": True,
            "cudnn": True,
            "nccl": True,
            "triton": True,
            "custom_kernel": True,
        }
    )
    assert score == 16


def test_compute_lockin_score_scales_with_signal_counts() -> None:
    low_score = compute_lockin_score({"torch_cuda": 1, "triton": 1})
    high_score = compute_lockin_score({"torch_cuda": 200, "triton": 200})

    assert low_score < high_score
    assert high_score <= 100


def test_compute_portability_score_is_inverse_of_lockin() -> None:
    assert compute_portability_score(16) == 84
    assert compute_portability_score(120) == 0
