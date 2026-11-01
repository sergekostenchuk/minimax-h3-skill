# Changelog

## 1.0.0 — 2026-11-01

- First public release of the `minimax-h3` Agent Skill.
- Prompt guide for all five H3 modes (T2VA, I2VA, FL2VA, L2VA, Ref2VA) with exact keyframe-alignment lines, six-section Ref2VA template, camera vocabulary, dialogue `<d>[Language] …</d>` with stable speaker IDs, subtitles and music rules.
- Long videos: choice between a new shot, last frame → first frame, `continue_from` and multi-part jobs; seam-speed guidance for chained clips.
- FreeVideo Agent API reference: quality tiers and `sampling`, LoRA, 24 fps / 17n+5 frame grid, `/capabilities` time estimates, idempotent submissions.
- Stdlib-only helper `freevideo.py`: loopback-only, never prints the token, no automatic retries, UTF-8 output on Windows consoles, exact `--accept-warning` for the experimental Ref2VA warning.
- Offline test suite (9 tests) and package validator in CI on Linux, Windows and macOS.
