# AI CUDA Lock-in Report 2026

## 1. Top 20 Most Locked Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| vllm-project/vllm | 73198 | 19 | 81 |
| sgl-project/sglang | 24532 | 19 | 81 |
| triton-inference-server/server | 10431 | 19 | 81 |
| huggingface/text-generation-inference | 10803 | 17 | 83 |
| deepspeedai/DeepSpeed | 41815 | 17 | 83 |
| NVIDIA/TensorRT-LLM | 13102 | 17 | 83 |
| AutoGPTQ/AutoGPTQ | 5033 | 15 | 85 |
| pytorch/ao | 2731 | 15 | 85 |
| xorbitsai/inference | 9134 | 15 | 85 |
| hpcaitech/ColossalAI | 41363 | 13 | 87 |
| NVIDIA-AI-IOT/torch2trt | 4858 | 12 | 88 |
| ggml-org/llama.cpp | 98052 | 11 | 89 |
| LMCache/LMCache | 7691 | 10 | 90 |
| huggingface/diffusers | 33051 | 9 | 91 |
| vllm-project/vllm-omni | 3183 | 9 | 91 |
| meta-pytorch/torchtune | 5703 | 9 | 91 |
| Lightning-AI/litgpt | 13226 | 7 | 93 |
| hiyouga/LlamaFactory | 68460 | 7 | 93 |
| unslothai/unsloth | 54026 | 7 | 93 |
| mlc-ai/mlc-llm | 22207 | 5 | 95 |

## 2. Top 20 Most Portable Repositories

| Repo | Stars | Lock-in | Portability |
| --- | ---: | ---: | ---: |
| neuralmagic/deepsparse | 3163 | 2 | 98 |
| deepspeedai/DeepSpeed-MII | 2101 | 4 | 96 |
| dstackai/dstack | 2063 | 4 | 96 |
| mlc-ai/mlc-llm | 22207 | 5 | 95 |
| casper-hansen/AutoAWQ | 2317 | 5 | 95 |
| lm-sys/FastChat | 39424 | 5 | 95 |
| Lightning-AI/litgpt | 13226 | 7 | 93 |
| hiyouga/LlamaFactory | 68460 | 7 | 93 |
| unslothai/unsloth | 54026 | 7 | 93 |
| huggingface/diffusers | 33051 | 9 | 91 |
| vllm-project/vllm-omni | 3183 | 9 | 91 |
| meta-pytorch/torchtune | 5703 | 9 | 91 |
| LMCache/LMCache | 7691 | 10 | 90 |
| ggml-org/llama.cpp | 98052 | 11 | 89 |
| NVIDIA-AI-IOT/torch2trt | 4858 | 12 | 88 |
| hpcaitech/ColossalAI | 41363 | 13 | 87 |
| AutoGPTQ/AutoGPTQ | 5033 | 15 | 85 |
| pytorch/ao | 2731 | 15 | 85 |
| xorbitsai/inference | 9134 | 15 | 85 |
| huggingface/text-generation-inference | 10803 | 17 | 83 |

## 3. Summary Stats

- Snapshot year: 2026
- Query: `curated:ai-infra-benchmark-2026`
- Requested limit: 25
- Scan mode: `clone`
- Generated at: 2026-03-15T23:05:02+00:00
- Repositories analyzed: 25
- Average Lock-in Score: 10.88
- Median Lock-in Score: 10.00
- Average Portability Score: 89.12
- Median Portability Score: 90.00

## 4. Lock-in Distribution

- 0-19: 25
- 20-39: 0
- 40-59: 0
- 60-79: 0
- 80-100: 0

## 5. Key Observations

- We analyzed 25 repositories with scan mode `clone`.
- The average CUDA lock-in score is 10.88.
- Triton appears in 20 repositories and tends to correlate with higher lock-in.
- However, portability varies significantly across the benchmark set.
- The most locked repository in this snapshot is vllm-project/vllm with a score of 19.
- The most portable repository in this snapshot is neuralmagic/deepsparse with a score of 98.
