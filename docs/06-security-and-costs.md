# 6. Security, Costs, and Limits

## Is it free?

Yes. The build.nvidia.com endpoint is a free tier with rate limits. No credit card is required.

## "$0.50 spent" in OpenCode?

That is **OpenCode's local estimate** based on the model's list price. It is not a bill from NVIDIA. To confirm, check your build.nvidia.com profile for any billing or payment method. If none is on file, nothing can be charged.

## Why are so many tokens used?

OpenCode sends its own instructions and tool definitions with every session (often 90k+ tokens). Free tier limits get used faster than your message length suggests.

## Privacy

NVIDIA logs free endpoint usage for security and product improvement per [API Trial Terms](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf). Do **not** send:

- Confidential work or client data
- Passwords, keys, or personal data
- Proprietary source code you are not allowed to share

## API key safety

- Store it only in an environment variable.
- Never commit it to Git. The config uses `{env:NVIDIA_API_KEY}` so the key is never written in the file.
- If a key leaks, delete it on build.nvidia.com and generate a new one.

## Alternative free provider

OpenRouter offers `nvidia/nemotron-3-ultra-550b-a55b:free` (rate limited). Always pick the `:free` variant to avoid charges.
