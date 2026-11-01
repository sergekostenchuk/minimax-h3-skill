# Security

- The helper `skill/minimax-h3/scripts/freevideo.py` talks only to a literal loopback FreeVideo address (`127.0.0.1` / `::1`), refuses redirects and proxies, never prints the bearer token and never retries writes on its own.
- State-changing calls (`POST /jobs`, `/media`, `/media/frame`) require an explicit `--apply`. Cancelling, resuming, releasing the GPU and settings are deliberately not exposed.
- The skill installs nothing and downloads no models.

Report a vulnerability through a private GitHub security advisory on this repository.
