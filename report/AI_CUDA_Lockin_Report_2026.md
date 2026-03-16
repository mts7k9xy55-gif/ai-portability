# AI CUDA Lock-in Report 2026

## 1. Top 20 Most Locked Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| vllm-project/vllm | 73257 | 100 | 0 |
| sgl-project/sglang | 24617 | 100 | 0 |
| NVIDIA/TensorRT-LLM | 13110 | 100 | 0 |
| deepspeedai/DeepSpeed | 41819 | 86 | 14 |
| huggingface/text-generation-inference | 10803 | 78 | 22 |
| pytorch/ao | 2732 | 76 | 24 |
| hpcaitech/ColossalAI | 41362 | 74 | 26 |
| AutoGPTQ/AutoGPTQ | 5033 | 64 | 36 |
| xorbitsai/inference | 9134 | 59 | 41 |
| triton-inference-server/server | 10431 | 54 | 46 |
| NVIDIA-AI-IOT/torch2trt | 4859 | 54 | 46 |
| LMCache/LMCache | 7694 | 52 | 48 |
| meta-pytorch/torchtune | 5703 | 44 | 56 |
| ggml-org/llama.cpp | 98119 | 40 | 60 |
| unslothai/unsloth | 54046 | 35 | 65 |
| vllm-project/vllm-omni | 3190 | 33 | 67 |
| huggingface/diffusers | 33050 | 32 | 68 |
| Lightning-AI/litgpt | 13227 | 31 | 69 |
| casper-hansen/AutoAWQ | 2317 | 21 | 79 |
| dstackai/dstack | 2064 | 20 | 80 |

## 2. Top 20 Most Portable Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| neuralmagic/deepsparse | 3163 | 5 | 95 |
| lm-sys/FastChat | 39424 | 11 | 89 |
| deepspeedai/DeepSpeed-MII | 2101 | 12 | 88 |
| mlc-ai/mlc-llm | 22211 | 12 | 88 |
| hiyouga/LlamaFactory | 68501 | 13 | 87 |
| dstackai/dstack | 2064 | 20 | 80 |
| casper-hansen/AutoAWQ | 2317 | 21 | 79 |
| Lightning-AI/litgpt | 13227 | 31 | 69 |
| huggingface/diffusers | 33050 | 32 | 68 |
| vllm-project/vllm-omni | 3190 | 33 | 67 |
| unslothai/unsloth | 54046 | 35 | 65 |
| ggml-org/llama.cpp | 98119 | 40 | 60 |
| meta-pytorch/torchtune | 5703 | 44 | 56 |
| LMCache/LMCache | 7694 | 52 | 48 |
| triton-inference-server/server | 10431 | 54 | 46 |
| NVIDIA-AI-IOT/torch2trt | 4859 | 54 | 46 |
| xorbitsai/inference | 9134 | 59 | 41 |
| AutoGPTQ/AutoGPTQ | 5033 | 64 | 36 |
| hpcaitech/ColossalAI | 41362 | 74 | 26 |
| pytorch/ao | 2732 | 76 | 24 |

## 3. Summary Stats

- Snapshot year: 2026
- Query: `curated:ai-infra-benchmark-2026`
- Requested limit: 25
- Scan mode: `clone`
- Generated at: 2026-03-16T08:16:09+00:00
- Repositories analyzed: 25
- Average Lock-in Score: 48.24
- Median Lock-in Score: 44.00
- Average Portability Score: 51.76
- Median Portability Score: 56.00

## 4. Lock-in Distribution

- 0-19: 5
- 20-39: 6
- 40-59: 6
- 60-79: 4
- 80-100: 4

## 5. Key Observations

- We analyzed 25 repositories with scan mode `clone`.
- The average CUDA lock-in score is 48.24.
- Triton appears in 14 repositories, NCCL appears in 18, and custom CUDA kernels appear in 13.
- Alternate backend signals appear in 19 ROCm repos, 17 Metal repos, 17 oneAPI repos, and 14 CPU-oriented repos.
- The highest lock-in cluster in this snapshot is vllm-project/vllm, sgl-project/sglang, NVIDIA/TensorRT-LLM.
- However, portability varies significantly across the benchmark set, with neuralmagic/deepsparse, lm-sys/FastChat, deepspeedai/DeepSpeed-MII landing at the portable end.
- The most locked repository in this snapshot is vllm-project/vllm with a score of 100.
- The most portable repository in this snapshot is neuralmagic/deepsparse with a score of 95.
