# AI Portability Master Prompt

Paste the prompt below into Cursor, Claude, GPT, or Copilot to generate the initial repository scaffold.

```text
You are a senior ML infrastructure engineer.

Your task is to build an open-source project called:

AI Portability

Goal:
Measure CUDA lock-in in open-source AI repositories and compute an AI Portability Index.

The tool scans GitHub repositories and detects how strongly they depend on CUDA.

The output should include:

1. CUDA Lock-in Score (0-100)
2. Portability Score (0-100)
3. Detected dependencies
4. Hardware backend compatibility estimation

The system should consist of the following modules:

scanner/
- scans a repo for CUDA related dependencies
- detects:
    torch.cuda
    cupy
    cudnn
    nccl
    triton kernels
    cudaMalloc
    cudaMemcpy
    custom CUDA kernels

scoring/
- compute a weighted CUDA lock-in score
example formula:

lockin =
  CUDA_API * 2
+ cudnn * 2
+ nccl * 2
+ triton_kernel * 3
+ custom_kernel * 4

portability_score =
  100 - lockin
  + open_backend_bonus

crawler/
- fetch top AI repositories from GitHub
criteria:
    topic: machine-learning
    stars > 1000
    language: python

dataset/
- store analyzed results
example:

datasets/top_ai_repos.json

report/
- generate a markdown report
called:

AI CUDA Lock-in Report

include:

Top AI repositories by lock-in score
Top AI repositories by portability score

CLI

ai-portability scan <repo>

example output:

AI Portability Index: 34

Lock-in signals:
- torch.cuda
- triton kernels
- nccl

Backend compatibility:
CUDA ✓
ROCm ✗
TPU ✗
CPU ✓

Project structure:

ai-portability
 ├ scanner/
 ├ scoring/
 ├ crawler/
 ├ datasets/
 ├ report/
 ├ cli.py
 ├ README.md

README should start with:

"AI models should run on any hardware.

But today many of them are locked into CUDA.

AI Portability measures this."

Use Python.
Use GitHub API.
Use Typer for CLI.

Generate the full repository code.
```

## Stronger Build Prompt

Use this version when you want the coding model to generate a more complete, runnable repository instead of a loose scaffold.

```text
You are a senior ML infrastructure engineer and open-source Python maintainer.

Build a complete open-source project called:

AI Portability

Core goal:
Measure CUDA lock-in in open-source AI repositories and compute an AI Portability Index.

Primary outcome:
Given a GitHub repository, the tool should analyze source code and project metadata, detect CUDA-specific dependencies and implementation patterns, and output:

1. CUDA Lock-in Score (0-100)
2. Portability Score (0-100)
3. Detected lock-in signals
4. Estimated hardware backend compatibility
5. A machine-readable JSON result

Use Python 3.11+.
Use Typer for the CLI.
Use the GitHub REST API.
Use pytest for tests.

Requirements:

- Generate the full repository code, not pseudocode.
- Do not leave TODOs, placeholders, or stub functions.
- Make the project runnable locally after install.
- Prefer simple, maintainable implementations over overengineering.

Project structure:

ai-portability/
├─ pyproject.toml
├─ README.md
├─ ai_portability/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ models.py
│  ├─ github_api.py
│  ├─ scanner/
│  │  ├─ __init__.py
│  │  └─ detector.py
│  ├─ scoring/
│  │  ├─ __init__.py
│  │  └─ calculator.py
│  ├─ crawler/
│  │  ├─ __init__.py
│  │  └─ github_crawler.py
│  ├─ dataset/
│  │  ├─ __init__.py
│  │  └─ storage.py
│  └─ report/
│     ├─ __init__.py
│     └─ markdown.py
├─ datasets/
├─ reports/
└─ tests/
   ├─ test_scanner.py
   ├─ test_scoring.py
   └─ test_cli.py

Functional requirements:

1. Repository scanner
- Accept either:
  - a GitHub repo slug like `vllm-project/vllm`
  - or a local directory path
- Detect these lock-in signals:
  - `torch.cuda`
  - `cupy`
  - `cudnn`
  - `nccl`
  - `triton`
  - `cudaMalloc`
  - `cudaMemcpy`
  - `nvcc`
  - `.cu` / `.cuh` files
  - custom CUDA kernels
  - CUDA-specific environment variables
  - ROCm support markers
  - TPU / XLA support markers
  - CPU-only compatibility markers
- Scan:
  - Python files
  - C/C++/CUDA files
  - shell scripts
  - `pyproject.toml`
  - `requirements.txt`
  - `setup.py`
  - GitHub Actions workflows
  - README text for backend claims

2. Scoring system
- Implement a weighted scoring model.
- Clamp CUDA Lock-in Score between 0 and 100.
- Compute Portability Score separately, also 0 to 100.
- Make weights easy to tune in one place.
- Example weighting logic:
  - `torch.cuda`: 8
  - `cupy`: 10
  - `cudnn`: 12
  - `nccl`: 10
  - `triton`: 14
  - `cudaMalloc` / `cudaMemcpy`: 18
  - `.cu` files: 16
  - custom CUDA kernels: 20
  - explicit ROCm support: subtract from lock-in
  - explicit TPU/XLA support: subtract from lock-in
  - explicit CPU fallback: subtract from lock-in

3. Hardware compatibility estimation
- Estimate support for:
  - CUDA
  - ROCm
  - TPU
  - CPU
  - Other / Unknown
- Return both:
  - a boolean-like compatibility map
  - a short explanation for each backend

4. GitHub integration
- Use the GitHub API to:
  - fetch repository metadata
  - download or clone repository contents for scanning
  - crawl popular AI repositories
- Support `GITHUB_TOKEN` from environment for authenticated requests.
- If no token is set, still work with unauthenticated requests when possible.
- Handle rate-limit and request errors cleanly.

5. Crawler
- Add a crawler that fetches top AI repositories from GitHub.
- Default query:
  - topic: machine-learning
  - language: Python
  - stars: >1000
- Support a limit flag, default 100.
- For each repo, run the scanner and produce:
  - `datasets/ai_portability_index.json`

6. Report generator
- Generate a markdown report called:
  - `AI CUDA Lock-in Report 2026`
- Write it to:
  - `reports/ai_cuda_lockin_report_2026.md`
- Include:
  - Top 20 repositories by CUDA lock-in
  - Top 20 repositories by portability
  - Summary observations
  - Methodology section

7. CLI
- Implement Typer commands:
  - `ai-portability scan <repo>`
  - `ai-portability crawl`
  - `ai-portability report <dataset_path>`
- Example:
  - `ai-portability scan vllm-project/vllm`
  - `ai-portability crawl --limit 100`
  - `ai-portability report datasets/ai_portability_index.json`
- Print clear terminal output and optionally save JSON with a flag.

8. Data model
- Use dataclasses or Pydantic models for structured results.
- A scan result should include:
  - repository name
  - source URL
  - lock-in score
  - portability score
  - detected signals
  - backend compatibility
  - evidence snippets

9. Testing
- Add unit tests for:
  - scanner detection
  - scoring behavior
  - CLI output
- Keep tests lightweight and offline.
- Mock GitHub network calls where necessary.

10. README
- README must begin with exactly this framing:

  AI models should run on any hardware.

  But today many of them are locked into CUDA.

  AI Portability measures this.

- README should explain:
  - what the project does
  - why CUDA lock-in matters
  - how scoring works
  - installation
  - CLI usage
  - example output
  - roadmap

Implementation guidance:

- Prefer regex- and file-pattern-based detection with simple heuristics.
- Make the scanner deterministic.
- Keep dependencies minimal.
- Use standard library when possible.
- Organize code cleanly so future contributors can tune weights and detection rules.

Deliverables:

- Full repository code
- Ready-to-run `pyproject.toml`
- Working CLI entry point
- Tests
- Example dataset file if useful
- Report generation logic

Now generate the full repository.
```

## Suggested Follow-up Prompt: Crawler

```text
Add a GitHub crawler that fetches the top 100 AI repositories
using the GitHub API.

Analyze each repo with the CUDA scanner and produce a dataset:

datasets/ai_portability_index.json
```

## Suggested Follow-up Prompt: Report

```text
Generate a report called:

AI CUDA Lock-in Report 2026

Include:

Top 20 repositories by CUDA lock-in
Top 20 repositories by portability
Observations
```

## Notes

- The core idea is the **AI Portability Index**, not just the scanner.
- The intended workflow is: create the repo, paste the prompt, generate the project, then push.
