# AI Portability

AI models should run on any hardware.

But today many of them are locked into CUDA.

**AI Portability measures this.**

This project scans open-source AI repositories and estimates how portable they actually are across hardware platforms.

```text
AI Software
      ↓
 CUDA Lock-in
      ↓
 Hardware Monopoly
```

---

# AI Portability Index

We analyze AI repositories and compute two metrics:

- **CUDA Lock-in Score**
- **AI Portability Score**
- **Yearly AI Portability Index snapshots**

Illustrative example:

| Repo | CUDA Lock-in | Portability |
| ----- | ------------ | ----------- |
| DeepSpeed | 92 | 18 |
| vLLM | 88 | 24 |
| Diffusers | 65 | 41 |
| llama.cpp | 22 | 76 |

---

# Why this matters

The AI ecosystem currently depends heavily on CUDA.

That means many models cannot easily run on:

- AMD GPUs
- TPUs
- AI ASICs
- emerging AI hardware

AI Portability aims to provide a way to **measure this dependency**.

---

# Example

CLI usage:

```bash
ai-portability scan https://github.com/vllm-project/vllm
```

Example output:

```text
Repository: vllm-project/vllm
CUDA Lock-in Score: 98
Portability Score: 2
Signals:
- torch_cuda: True
- cupy: True
- cudnn: True
- nccl: True
- triton: True
- cuda_malloc: True
- cuda_memcpy: True
- custom_kernel: True
- cuda_build: True
Backend Compatibility:
- cuda: True
- rocm: True
- metal: False
- oneapi: True
- cpu: True
```

---

# Features

- CUDA dependency detection
- Alternate backend signal detection
- Hardware portability scoring
- GitHub repository scanning
- AI Portability Index dataset
- Automatic CUDA Lock-in reports

---

# Installation

```bash
pip install -e .
```

Optional for higher GitHub API limits:

```bash
export GITHUB_TOKEN=your_token_here
```

---

# CLI Usage

Scan a repository:

```bash
ai-portability scan <repo>
```

Example:

```bash
ai-portability scan https://github.com/vllm-project/vllm
ai-portability scan https://github.com/huggingface/diffusers
```

Crawl top repositories and save a dataset:

```bash
ai-portability crawl
```

The crawler defaults to a lighter initial snapshot and skips very large repositories unless you opt into clone fallback.

Use a custom GitHub search query:

```bash
ai-portability crawl --query "topic:machine-learning stars:>1000 language:python"
```

Use a topic preset:

```bash
ai-portability crawl --topic llm
```

Generate the canonical yearly snapshot:

```bash
ai-portability snapshot --clone-fallback
```

Or override the preset and sample size:

```bash
ai-portability snapshot --topic benchmark --limit 25 --clone-fallback
```

The canonical snapshot uses a curated AI infra benchmark set instead of a broad machine-learning search query, so the resulting index is more relevant to CUDA lock-in discussions.

This writes:

- `datasets/ai_portability_index_2026.json`
- `report/AI_CUDA_Lockin_Report_2026.md`

The dataset stores top-level metadata:

- `snapshot_year`
- `query`
- `scan_mode`
- `limit`
- `generated_at`
- `repositories`

Generate the markdown report:

```bash
ai-portability report
```

---

# AI CUDA Lock-in Report

The project generates a versioned **AI CUDA Lock-in Report** such as `report/AI_CUDA_Lockin_Report_2026.md`, including:

- Top AI repos by CUDA dependency
- Top AI repos by portability
- Hardware compatibility analysis
- Average and median lock-in scores
- Score distribution
- Key observations for discussion and sharing

---

# Roadmap

- CUDA lock-in scanner
- AI Portability Index dataset
- yearly benchmark snapshots
- lightweight GitHub manifest scanning
- benchmark methodology refinement
- broader repo coverage

---

# Contributing

We welcome contributions from:

- ML researchers
- infrastructure engineers
- hardware developers

---

# Vision

AI models should not depend on a single hardware stack.

AI Portability aims to make AI software **hardware-independent**.

---

If you care about AI hardware portability, consider starring the repo.
