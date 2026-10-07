# 1. Requirements

## Can I run Nemotron 3 Ultra locally?

**No, not on a normal PC.** NVIDIA's minimum hardware for self-hosting:

- 4x GB200, 4x B200, 4x GB300, 4x B300, or 8x H100 GPUs
- Linux only
- Roughly 300 GB of weights even in the smallest (NVFP4) version

That is datacenter hardware. This guide uses the **hosted free API** instead.

## What you actually need

| Item | Notes |
|------|-------|
| PC | Windows, macOS, or Linux. Any modern machine works. |
| Internet | Required. The model runs remotely. |
| Node.js LTS | Needed to install OpenCode via npm. Get it from nodejs.org. |
| NVIDIA account | Free. Used to generate the API key. |
| No credit card | The free endpoint does not require payment. |

## Model at a glance

- 550B total parameters, 55B active per token (Mixture of Experts)
- Up to 1M token context
- Strong at coding, reasoning, tool use, long documents
- Top tier among open models; not clearly ahead of the best paid closed models
