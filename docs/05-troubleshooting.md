# 5. Troubleshooting

## Common errors

| Error | Likely cause | Fix |
|-------|--------------|-----|
| `opencode` is not recognized | Terminal opened before install finished updating PATH | Close and reopen the terminal |
| `401 Unauthorized` / authorization header missing | API key not loaded in the current terminal | Set `$env:NVIDIA_API_KEY` in this window (see [03](03-get-nvidia-api-key.md)), then relaunch `opencode` |
| `403 Forbidden` / authorization failed | Key is invalid, incomplete, or revoked | Generate a new key on build.nvidia.com and set it again |
| `404 Not Found` | Model ID changed on NVIDIA's side | Check the current model ID on build.nvidia.com and update it in `opencode.json` |
| `429 Too Many Requests` | Free tier rate limit reached | Wait a few minutes and retry |

## Quick checks (PowerShell)

```powershell
echo $env:NVIDIA_API_KEY            # empty means the key is not set in this window
$env:NVIDIA_API_KEY.Length          # should be about 70
Get-Content "$env:USERPROFILE\.config\opencode\opencode.json"
```

## Note on setx

`setx` only applies to **new** terminal windows. After running it, open a new terminal or also set `$env:NVIDIA_API_KEY` in the current one.
