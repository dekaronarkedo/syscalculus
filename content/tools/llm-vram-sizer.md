---
title: "LLM VRAM & Quantization Sizer (FP16 / INT8 / INT4)"
slug: "llm-vram-sizer"
category: "AI / MLOps"
subtitle: "Calculate GPU VRAM memory requirements for LLaMA 3, DeepSeek, and Mistral models. Accurately compute weights, KV-cache, and CUDA runtime overhead before renting cloud GPU clusters."
meta_description: "Accurately compute GPU VRAM memory requirements for LLaMA 3, DeepSeek, and Mistral models. Calculates weights, KV-cache, and CUDA overhead."
article_headline: "The Mathematics of LLM GPU Memory: Calculating KV-Cache, Context Length, and Quantization Perplexity"
date_published: "2026-09-05"
date_modified: "2026-09-05"
faqs:
  - question: "Why do LLMs crash with 'CUDA Out of Memory' during inference even when weights fit in VRAM?"
    answer: "During autoregressive inference, the model must store Key-Value (KV) tensors for every preceding token in the conversation to compute attention. As the context length grows (e.g. 8k to 32k or 128k tokens) or concurrent user requests increase, the dynamic KV-cache memory frequently exceeds the static weight memory, triggering an out-of-memory crash."
  - question: "What is Grouped-Query Attention (GQA) and how does it reduce VRAM consumption?"
    answer: "Traditional Multi-Head Attention (MHA) allocates separate Key and Value heads for every Query head. GQA (implemented in LLaMA 3 and Mistral) shares single Key and Value heads across groups of Query heads (e.g. 8:1 ratio), reducing the KV-cache footprint by up to 87.5% without degrading reasoning accuracy."
  - question: "What are the tradeoffs between AWQ, GPTQ, and GGUF quantization formats?"
    answer: "AWQ (Activation-aware Weight Quantization) protects critical outlier weights and provides the highest inference speed and perplexity retention on NVIDIA TensorRT-LLM and vLLM servers. GGUF is optimized for CPU/hybrid inference in llama.cpp, while GPTQ provides fast one-shot offline quantization."
---

## Executive MLOps Analysis: The GPU Sizing Estimation Failure

In modern AI application development, renting GPU cloud instances without calculating the exact mathematical memory footprint leads to two costly failure states:

1. **Over-provisioning:** Renting an 8x NVIDIA H100 80GB cluster ($28.00/hr, ~$20,000/month) to serve a model that could comfortably execute on a single dual-L40S node ($4.50/hr).
2. **Under-provisioning (OOM Outages):** Deploying a 70B parameter model at 4-bit quantization on a single 48GB GPU (NVIDIA A6000 / RTX 6000 Ada). The service boots successfully and passes smoke tests with 500-token prompts. However, when user requests reach 16,000-token context windows under batch concurrency, dynamic KV-cache allocation exceeds the remaining 13GB of free VRAM, triggering fatal `CUDA out of memory` panics and service restarts.

```
+-----------------------------------------------------------------------------------+
|                        TOTAL GPU VRAM ALLOCATION BUDGET                           |
+-----------------------------------------------------------------------------------+
|  [ Model Weights ]      [ Dynamic KV-Cache ]      [ CUDA & Activation Overhead ]   |
|   (Static Footprint)     (Scales with Context)     (PyTorch Memory Pool Reserve)   |
|                                                                                   |
|  * 70B Model (4-bit):    * 8k Context Window:      * CUDA Context: ~1.2 GB        |
|    ~35.0 GB               ~2.7 GB                   * FlashAttention scratch: ~1.5GB|
|                                                                                   |
|  TOTAL VRAM REQUIRED:    35.0 GB + 2.7 GB + 2.7 GB = 40.4 GB (Requires 48GB GPU)  |
+-----------------------------------------------------------------------------------+
```

---

## The Mathematical Formulas for LLM VRAM

Calculating the memory footprint of an autoregressive Transformer model requires breaking memory down into three distinct hardware allocations:

$$\text{Total VRAM} = M_{\text{weights}} + M_{\text{kv\_cache}} + M_{\text{overhead}}$$

---

### 1. Static Model Weights Memory ($M_{\text{weights}}$)

The memory required to load model weights into high-bandwidth memory (HBM) is determined strictly by parameter count ($P$) and quantization bit precision ($B$):

$$M_{\text{weights}} = \frac{P \times B}{8} \times 1.15 \text{ (Conversion & Metadata Factor)}$$

Where:
* $P$ = Total parameter count (e.g. 8 Billion, 70 Billion, 405 Billion)
* $B$ = Bits per parameter:
  * **FP16 / BF16:** 16 bits (2 bytes per parameter)
  * **INT8 / Q8:** 8 bits (1 byte per parameter)
  * **INT4 / AWQ / GPTQ:** 4 bits (0.5 bytes per parameter)

#### Sizing Example: LLaMA-3-70B
* **At FP16 (16-bit):** $\frac{70 \times 10^9 \times 16}{8 \times 1024^3} \times 1.15 \approx \mathbf{154.2 \text{ GB}}$ (Requires 2x 80GB A100/H100)
* **At INT4 (4-bit):** $\frac{70 \times 10^9 \times 4}{8 \times 1024^3} \times 1.15 \approx \mathbf{38.5 \text{ GB}}$ (Fits on 1x 48GB GPU or 2x 24GB RTX 3090/4090)

---

### 2. Dynamic KV-Cache Memory ($M_{\text{kv\_cache}}$)

During token generation, the model caches key and value projections for all previous tokens in the sequence across all transformer layers. The memory consumed per concurrent user request is:

$$M_{\text{kv}} = 2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times L_{\text{context}} \times B_{\text{precision}}$$

Where:
* $n_{\text{layers}}$: Number of Transformer decoder layers (e.g. 80 layers in LLaMA-3-70B)
* $n_{\text{kv\_heads}}$: Number of Key-Value attention heads (e.g. 8 in Grouped-Query Attention)
* $d_{\text{head}}$: Head dimension size (typically 128)
* $L_{\text{context}}$: Sequence length in tokens (e.g. 8,192 or 32,768)
* $B_{\text{precision}}$: 2 bytes for FP16 cache, 1 byte for FP8 quantized cache

#### FlashAttention-2 & PagedAttention Optimization
Modern inference engines like **vLLM** utilize **PagedAttention** (inspired by virtual memory paging in operating systems). PagedAttention reduces memory fragmentation from 60% down to under 4%, allowing servers to dynamically pack up to 3x more concurrent requests into available VRAM.

---

### 3. Runtime Activation & CUDA Context Overhead ($M_{\text{overhead}}$)

When PyTorch or TensorRT-LLM initializes a GPU context, several gigabytes are reserved immediately:
1. **CUDA Driver & Context:** Consumes between **800 MB and 1.4 GB** of VRAM on process startup.
2. **Intermediate Activation Tensors:** Peak activation memory during the forward pass of large input prompts.
3. **vLLM Memory Pool:** By default, vLLM configures `gpu_memory_utilization = 0.90`, reserving 90% of total physical VRAM for weights and KV-cache blocks.

---

## Hardware Selection Matrix: Cloud GPU Tiers

| Model Architecture | Quantization | Context Window | Minimum VRAM | Recommended Production Cloud GPU |
| :--- | :--- | :--- | :--- | :--- |
| **Mistral / LLaMA 3 8B** | FP16 (16-bit) | 8,192 | 18.2 GB | 1x NVIDIA RTX 4090 (24GB) or 1x A10G |
| **Mistral / LLaMA 3 8B** | INT4 (4-bit) | 8,192 | 6.8 GB | 1x Consumer RTX 3070 / Apple M2 (16GB) |
| **LLaMA 3 70B** | INT4 (AWQ) | 8,192 | 41.2 GB | 1x NVIDIA A6000 (48GB) or 2x RTX 3090 |
| **LLaMA 3 70B** | FP16 (16-bit) | 8,192 | 158.4 GB | 2x NVIDIA A100 / H100 (80GB SXM) |
| **LLaMA 3 70B** | INT4 (AWQ) | 32,768 (Long) | 52.8 GB | 1x NVIDIA A100 (80GB) |
| **DeepSeek V2.5 / 405B** | INT4 (AWQ) | 16,384 | 248.0 GB | 4x NVIDIA H100 (80GB) Cluster |

---

## Production vLLM Deployment Configuration

To maximize throughput and prevent out-of-memory crashes on production servers, launch vLLM with tuned KV-cache parameters:

```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model casperhansen/llama-3-70b-instruct-awq \
    --quantization awq \
    --dtype float16 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.92 \
    --max-num-seqs 64 \
    --enforce-eager false \
    --trust-remote-code
```

### Critical Tuning Flags:
* `--max-model-len 8192`: Clamps the maximum context window to prevent unexpected 32k prompts from blowing out memory.
* `--gpu-memory-utilization 0.92`: Gives PyTorch 8% headroom for transient activations and temporary tensor allocations.
* `--max-num-seqs 64`: Throttles maximum concurrent generation streams to guarantee deterministic P99 latency.
