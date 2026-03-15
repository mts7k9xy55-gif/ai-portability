# AI CUDA Lock-in Report 2026

## 1. Top 20 Most Locked Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| vllm-project/vllm | 73198 | 98 | 2 |
| sgl-project/sglang | 24532 | 97 | 3 |
| NVIDIA/TensorRT-LLM | 13102 | 94 | 6 |
| deepspeedai/DeepSpeed | 41815 | 79 | 21 |
| pytorch/ao | 2731 | 75 | 25 |
| hpcaitech/ColossalAI | 41363 | 74 | 26 |
| huggingface/text-generation-inference | 10803 | 68 | 32 |
| triton-inference-server/server | 10431 | 67 | 33 |
| AutoGPTQ/AutoGPTQ | 5033 | 64 | 36 |
| xorbitsai/inference | 9134 | 61 | 39 |
| NVIDIA-AI-IOT/torch2trt | 4858 | 46 | 54 |
| LMCache/LMCache | 7691 | 45 | 55 |
| meta-pytorch/torchtune | 5703 | 43 | 57 |
| vllm-project/vllm-omni | 3183 | 41 | 59 |
| huggingface/diffusers | 33051 | 38 | 62 |
| ggml-org/llama.cpp | 98052 | 36 | 64 |
| Lightning-AI/litgpt | 13226 | 35 | 65 |
| unslothai/unsloth | 54026 | 35 | 65 |
| casper-hansen/AutoAWQ | 2317 | 25 | 75 |
| mlc-ai/mlc-llm | 22207 | 22 | 78 |

## 2. Top 20 Most Portable Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| neuralmagic/deepsparse | 3163 | 6 | 94 |
| deepspeedai/DeepSpeed-MII | 2101 | 12 | 88 |
| dstackai/dstack | 2063 | 12 | 88 |
| lm-sys/FastChat | 39424 | 14 | 86 |
| hiyouga/LlamaFactory | 68460 | 19 | 81 |
| mlc-ai/mlc-llm | 22207 | 22 | 78 |
| casper-hansen/AutoAWQ | 2317 | 25 | 75 |
| Lightning-AI/litgpt | 13226 | 35 | 65 |
| unslothai/unsloth | 54026 | 35 | 65 |
| ggml-org/llama.cpp | 98052 | 36 | 64 |
| huggingface/diffusers | 33051 | 38 | 62 |
| vllm-project/vllm-omni | 3183 | 41 | 59 |
| meta-pytorch/torchtune | 5703 | 43 | 57 |
| LMCache/LMCache | 7691 | 45 | 55 |
| NVIDIA-AI-IOT/torch2trt | 4858 | 46 | 54 |
| xorbitsai/inference | 9134 | 61 | 39 |
| AutoGPTQ/AutoGPTQ | 5033 | 64 | 36 |
| triton-inference-server/server | 10431 | 67 | 33 |
| huggingface/text-generation-inference | 10803 | 68 | 32 |
| hpcaitech/ColossalAI | 41363 | 74 | 26 |

## 3. Summary Stats

- Snapshot year: 2026
- Query: `curated:ai-infra-benchmark-2026`
- Requested limit: 25
- Scan mode: `clone`
- Generated at: 2026-03-15T23:05:02+00:00
- Repositories analyzed: 25
- Average Lock-in Score: 48.24
- Median Lock-in Score: 43.00
- Average Portability Score: 51.76
- Median Portability Score: 57.00

## 4. Lock-in Distribution

- 0-19: 5
- 20-39: 6
- 40-59: 4
- 60-79: 7
- 80-100: 3

## 5. Key Observations

- We analyzed 25 repositories with scan mode `clone`.
- The average CUDA lock-in score is 48.24.
- Triton appears in 20 repositories and tends to correlate with higher lock-in.
- However, portability varies significantly across the benchmark set.
- The most locked repository in this snapshot is vllm-project/vllm with a score of 98.
- The most portable repository in this snapshot is neuralmagic/deepsparse with a score of 94.
