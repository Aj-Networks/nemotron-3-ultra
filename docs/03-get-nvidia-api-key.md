# 3. Get a Free NVIDIA API Key

1. Go to **https://build.nvidia.com** and sign in (create a free account if needed).
2. Search for **nemotron 3 ultra** and open `nvidia/nemotron-3-ultra-550b-a55b`.
3. On the **Build** tab, click **Generate API Key**.
4. Copy the full key, including the `nvapi-` prefix.

You do **not** need the Python, Node, or Shell code shown on that page. OpenCode handles the API calls.

## Save the key as an environment variable

### Windows (PowerShell)

Replace the text inside the quotes with your full key:

```powershell
setx NVIDIA_API_KEY "nvapi-YOUR-REAL-KEY"
$env:NVIDIA_API_KEY = "nvapi-YOUR-REAL-KEY"
```

- `setx` saves it for future windows.
- `$env:` makes it work in the current window.

Verify:

```powershell
$env:NVIDIA_API_KEY.Substring(0,6)    # should print nvapi-
$env:NVIDIA_API_KEY.Length            # should be about 70
```

### macOS / Linux

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export NVIDIA_API_KEY="nvapi-YOUR-REAL-KEY"
```

Then run `source ~/.bashrc` (or open a new terminal).

> Treat this key like a password. Never commit it, post it, or include it in screenshots.
