# Official Nemotron 3 Ultra 550B-A55B Limitations

Source: NVIDIA build.nvidia.com model card (updated 2026-06-04) | [Technical Report](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf) | [API Trial Terms](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf)

## Model Specifications

| Property | Value |
|----------|-------|
| **Total Parameters** | 550B (55B active per token) |
| **Architecture** | LatentMoE: Mamba-2 + MoE + Attention hybrid with Multi-Token Prediction (MTP) |
| **Context Length** | Up to 1,000,000 tokens (1M) |
| **Supported Languages** | English, French, Spanish, Italian, German, Japanese, Korean, Hindi, Brazilian Portuguese, Chinese |
| **Reasoning Mode** | Configurable via chat template (`enable_thinking: true/false`) |
| **License** | OpenMDW 1.1 (commercial + non-commercial) |
| **Data Cutoff** | Pre-training: Sep 2025. Post-training: May 2026 |

## Free API Tier Limits (build.nvidia.com)

| Limit | Value |
|-------|-------|
| **Rate limit** | Not publicly documented by NVIDIA. Community observes ~10-20 req/min before 429. |
| **Daily quota** | Not publicly documented. |
| **Max tokens/request** | 1,000,000 (context) / ~32,768 (output typical) |
| **Concurrent requests** | Limited (single-digit typically) |
| **Session persistence** | None. Stateless per request. |
| **Logging** | NVIDIA logs usage per [API Trial Terms](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf). Don't send confidential code. |

## Local Deployment Requirements (Self-Hosted)

| Config | Minimum Hardware |
|--------|------------------|
| **Single-node (NVFP4)** | 4x B200 / 4x GB200 / 4x GB300 / 4x B300 |
| **Alternative** | 8x H100-80GB |
| **VRAM (model + KV cache)** | ~300 GB weights (NVFP4) + KV cache |
| **OS** | Linux only |
| **Container Runtime** | vLLM 0.22.0+, SGLang 0.5.11+, TRT-LLM 1.3.0rc17+ |
| **Tensor Parallel** | Required (tp=4 minimum) |
| **Expert Parallel** | Required (ep=4) |
| **Context at 1M** | Requires `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` (vLLM) or `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` (SGLang) |

## API Integration Constraints

| Constraint | Detail |
|------------|--------|
| **Base URL** | `https://integrate.api.nvidia.com/v1` (free tier) |
| **Auth** | `nvapi-` prefixed key via `Authorization: Bearer` |
| **OpenAI Compatible** | Yes (`/v1/chat/completions`) |
| **Tool Calling** | Requires `chat_template_kwargs: {enable_thinking: true, force_nonempty_content: true}` |
| **Reasoning Budget** | Use `reasoning_budget` param to cap thinking tokens (default unlimited) |
| **MTP Speculative Decoding** | 5 tokens default. Configurable via backend. |
| **Chunked Prefill** | Required for long context. |
| **Prefix Caching** | Enabled by default on supported backends. |

## Known Behavioral Limits (source: [Hugging Face model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4))

| Area | BF16 | NVFP4 | Notes |
|------|------|-------|-------|
| **Hallucination (OmniScience Non-Hallucination)** | 78.7% | 75.5% | |
| **Math (GPQA, no tools)** | 87.0% | 87.9% | |
| **SWE-Bench Verified** | 70.7% | 69.5% | |
| **Long Context (RULER 1M)** | 94.7% | 94.0% | |
| **Agentic (Terminal Bench 2.1)** | 56.4% | 53.9% | |
| **TauBench V3 (Average)** | 70.9% | 70.3% | Banking only 22.6%/19.2% |
| **BrowseComp** | 44.4% | 41.4% | |
| **SWE-Bench Multilingual** | 67.7% | 69.1% | |
| **Multilingual** | 12 languages | 12 languages | Quality varies by language |
| **Coding (43 languages in pre-training)** | Strong in Python, JS, TS, Rust, Go, C++ | Weaker in niche languages | Pre-training coverage, not guaranteed proficiency |

## Free Tier Practical Limits (Community Observed, Not Official)

| Metric | Typical |
|--------|---------|
| **Requests/minute** | ~10-20 before 429 |
| **Tokens/minute** | ~50k-100k |
| **Session length** | Resets on rate limit or quota |
| **Key rotation** | Manual via build.nvidia.com |
| **No SLA** | Free tier can be throttled or disabled anytime |

> **Note:** NVIDIA does not publish official free tier limits. The above are community observations. Monitor for 429 responses and implement exponential backoff.

## Cost Estimation (If Moving Off Free Tier)

| Deployment | Est. Hourly Cost |
|------------|------------------|
| 4x B200 (NVFP4) | ~$12-16/hr (cloud) |
| 8x H100-80GB | ~$24-32/hr (cloud) |
| API (paid) | Not published. Contact NVIDIA. |

## Recommendations for Production at Scale

1. **Cache aggressively**: Use prefix caching, semantic cache for repeated queries
2. **Queue requests**: Implement token-bucket rate limiter per user/project
3. **Monitor 429s**: Backoff with exponential retry + jitter
4. **Fallback provider**: OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` as backup
5. **Project isolation**: Separate memory/cache per project (see `memory/` and `cache/` folders)
6. **Reasoning budget**: Set `reasoning_budget: 512-1024` for cost/latency control
7. **Stream responses**: Use SSE streaming to reduce perceived latency

## What This Means for Your Repo

- **Free tier only**: Suitable for demos, learning, low-volume personal use
- **Millions of users**: Requires self-hosted deployment or paid NVIDIA enterprise API
- **Memory/cache**: Must be local (this repo provides `memory/` and `cache/` structure)
- **Project folders**: Each project gets isolated `projects/<name>/` with own context
- **UI screenshots**: Place in `website/assets/images/` for documentation site