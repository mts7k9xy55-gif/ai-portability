# Launch Posts

Repository:

- https://github.com/mts7k9xy55-gif/ai-portability

Snapshot artifacts:

- `datasets/ai_portability_index_2026.json`
- `report/AI_CUDA_Lockin_Report_2026.md`

## Hacker News

Title option 1:

Show HN: AI Portability Index 2026

Title option 2:

Show HN: Measuring CUDA lock-in in open-source AI repositories

Body:

I built a small OSS tool that scans open-source AI repos and estimates CUDA lock-in.

It generates:

- a CUDA lock-in score
- a portability score
- a dataset snapshot
- a markdown report

Repo:
https://github.com/mts7k9xy55-gif/ai-portability

Current snapshot:

- 25 AI / inference repos analyzed
- average lock-in score: 1.16
- median lock-in score: 0.00
- vllm appears with a lock-in score of 4

The current methodology is intentionally simple: scan repo manifests and source files for CUDA-linked signals such as `torch.cuda`, `cudnn`, `nccl`, `triton`, `cudaMalloc`, and `cudaMemcpy`, then compute a portability score from that signal set.

This is not meant to be the final word on portability. The goal is to create a benchmark and a dataset people can argue with, improve, and extend over time.

Feedback on methodology is the main thing I want.

## X

Launched `ai-portability`: an OSS tool that measures CUDA lock-in in open-source AI repos.

It scans GitHub repos, computes a lock-in score + portability score, and generates an `AI Portability Index 2026` snapshot.

Current snapshot:
- 25 repos
- avg lock-in: 1.16
- median: 0
- `vllm-project/vllm`: 4

Repo: https://github.com/mts7k9xy55-gif/ai-portability
Report: https://github.com/mts7k9xy55-gif/ai-portability/blob/main/report/AI_CUDA_Lockin_Report_2026.md

The interesting part is not the number itself yet. It is making hardware lock-in measurable and debatable.

## Reddit

Title:

I built an OSS tool to measure CUDA lock-in in AI repositories

Body:

I built a small open-source project called `ai-portability`.

It scans AI repositories on GitHub and estimates:

- CUDA lock-in score
- portability score
- backend compatibility signals

The project also generates a versioned dataset and report:

- `datasets/ai_portability_index_2026.json`
- `report/AI_CUDA_Lockin_Report_2026.md`

Repo:
https://github.com/mts7k9xy55-gif/ai-portability

This is the current snapshot:

- 25 repos analyzed
- average lock-in: 1.16
- median lock-in: 0
- `vllm-project/vllm` shows up with a score of 4

Methodology is deliberately simple right now: scan manifests and source files for signals like `torch.cuda`, `cupy`, `cudnn`, `nccl`, `triton`, `cudaMalloc`, and `cudaMemcpy`, then aggregate them into a score.

The point is less "this score is perfect" and more "can we make hardware lock-in visible enough to benchmark over time?"

I would especially like feedback on:

- false positives / false negatives
- better weighting
- better benchmark repo selection
- whether portability should be split into training vs inference
