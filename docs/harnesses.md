# Harness support

`minimax-h3` is a standard [Agent Skills](https://agentskills.io/specification) folder (`SKILL.md` with `name` + `description`, plus `references/`, `scripts/`, `assets/`). Any harness that loads Agent Skills can use it; the model inside the harness does not matter (Claude, GPT, Gemini, Qwen, Kimi, DeepSeek, GLM, Grok, Llama via Ollama, …).

Checked against official documentation on 2026-11-01. `install.py` target in brackets.

| Harness | User-level folder | Project-level folder | Official docs |
|---|---|---|---|
| Claude Code `[claude-code]` | `~/.claude/skills/` | `.claude/skills/` | https://code.claude.com/docs/en/skills |
| OpenAI Codex (CLI and app) `[agents]` | `~/.agents/skills/` | `.agents/skills/` | https://learn.chatgpt.com/docs/build-skills |
| Gemini CLI `[agents]` / `[gemini]` | `~/.agents/skills/` or `~/.gemini/skills/` | `.agents/skills/` or `.gemini/skills/` | https://geminicli.com/docs/cli/skills/ |
| Google Antigravity `[antigravity]` | `~/.gemini/config/skills/` | `.agents/skills/` | https://antigravity.google/docs/skills |
| Qwen Code `[agents]` / `[qwen]` | `~/.agents/skills/` or `~/.qwen/skills/` | `.agents/skills/` or `.qwen/skills/` | https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/ |
| Kimi Code CLI `[kimi]` / `[agents]` | `~/.config/agents/skills/` (recommended) or `~/.agents/skills/` | `.agents/skills/` or `.kimi/skills/` | https://moonshotai.github.io/kimi-cli/en/customization/skills.html |
| Hermes Agent `[hermes]` | `~/.hermes/skills/` (Windows app: `%LOCALAPPDATA%\hermes\skills\`) | `.hermes/skills/` (after `hermes skills trust`) | https://hermes-agent.nousresearch.com/docs/user-guide/features/skills |
| pi coding agent `[agents]` | `~/.agents/skills/` | `.agents/skills/` | https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md |
| OpenCode `[agents]` / `[opencode]` | `~/.agents/skills/` or `~/.config/opencode/skills/` | `.agents/skills/` or `.opencode/skills/` | https://opencode.ai/docs/skills/ |
| Cursor `[agents]` / `[cursor]` | `~/.agents/skills/` or `~/.cursor/skills/` | `.agents/skills/` or `.cursor/skills/` | https://cursor.com/docs/context/skills |
| Cline `[cline]` | `~/.cline/skills/` | `.cline/skills/` | https://docs.cline.bot/customization/skills |
| Roo Code `[agents]` / `[roo]` | `~/.agents/skills/` or `~/.roo/skills/` | `.agents/skills/` or `.roo/skills/` | https://roocodeinc.github.io/Roo-Code/features/skills |
| Goose `[agents]` | `~/.agents/skills/` | `.agents/skills/` | https://goose-docs.ai/docs/guides/context-engineering/using-skills |
| GitHub Copilot (CLI, VS Code agent, cloud agent) `[agents]` / `[copilot]` | `~/.agents/skills/` or `~/.copilot/skills/` | `.github/skills/` or `.agents/skills/` | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills |
| Devin Desktop / Windsurf `[agents]` / `[devin]` | `~/.agents/skills/` or `~/.config/devin/skills/` | `.agents/skills/` or `.devin/skills/` | https://docs.devin.ai/desktop/cascade/skills |
| xAI Grok Build CLI (beta) `[agents]` / `[grok]` | `~/.agents/skills/` or `~/.grok/skills/` | `.grok/skills/` | https://docs.x.ai/build/features/skills-plugins-marketplaces |

Native install commands, where a harness has one:

```bash
gemini skills install https://github.com/sergekostenchuk/minimax-h3-skill --scope user   # Gemini CLI (repository install)
gh skill install sergekostenchuk/minimax-h3-skill minimax-h3                             # GitHub Copilot (gh >= 2.90, preview)
hermes skills install <SKILL.md URL>                                                     # Hermes Agent
```

Check the exact syntax in your harness's docs before using these; `install.py` (a plain folder copy) works everywhere.

## Not verified / no native skills

- **DeepSeek Harness (`dsh`)**: third-party sources mention `~/.agents/skills/`; not confirmed in official docs. Try the `agents` target, or the fallback below.
- **Ollama, LM Studio** are model runners, not harnesses. Use a harness on top of them (for example `ollama launch` starts Claude Code, OpenCode, Hermes and others) and install the skill there.
- **Chat UIs without skills** (web chats of DeepSeek, Qwen, Grok, Kimi, …): paste `SKILL.md` and the needed `references/*.md` into the system prompt or project instructions (`AGENTS.md`). The helper script still needs a shell on the FreeVideo machine.
