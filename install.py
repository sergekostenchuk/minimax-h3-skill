#!/usr/bin/env python3
"""Install the minimax-h3 Agent Skill into one or more agent harnesses (user level). Stdlib only.

  python install.py --list
  python install.py --target agents            # the shared ~/.agents/skills (Codex, Gemini CLI, Qwen Code, Kimi, pi, ...)
  python install.py --target claude-code --target hermes
  python install.py --all --dry-run

Copies skill/minimax-h3 into <root>/minimax-h3. An existing copy is replaced only with --force.
Paths follow each harness's official documentation (see docs/harnesses.md)."""
import argparse
import os
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent / 'skill' / 'minimax-h3'
HOME = Path.home()


def hermes_root():
    # Hermes keeps its home in %LOCALAPPDATA%\hermes on Windows installs, ~/.hermes elsewhere; HERMES_HOME wins.
    if os.environ.get('HERMES_HOME'):
        return Path(os.environ['HERMES_HOME']) / 'skills'
    local = os.environ.get('LOCALAPPDATA')
    if os.name == 'nt' and local and (Path(local) / 'hermes').is_dir():
        return Path(local) / 'hermes' / 'skills'
    return HOME / '.hermes' / 'skills'


TARGETS = {
    'agents': (lambda: HOME / '.agents' / 'skills',
               'shared root: Codex, Gemini CLI, Qwen Code, Kimi Code, pi, OpenCode, Cursor, Roo Code, Goose, '
               'GitHub Copilot, Devin/Windsurf, Grok Build'),
    'claude-code': (lambda: HOME / '.claude' / 'skills', 'Claude Code'),
    'hermes': (hermes_root, 'Hermes Agent'),
    'antigravity': (lambda: HOME / '.gemini' / 'config' / 'skills', 'Google Antigravity'),
    'cline': (lambda: HOME / '.cline' / 'skills', 'Cline'),
    'gemini': (lambda: HOME / '.gemini' / 'skills', 'Gemini CLI (own root; also reads ~/.agents/skills)'),
    'qwen': (lambda: HOME / '.qwen' / 'skills', 'Qwen Code (own root; also reads ~/.agents/skills)'),
    'kimi': (lambda: HOME / '.config' / 'agents' / 'skills', 'Kimi Code CLI (recommended root)'),
    'opencode': (lambda: HOME / '.config' / 'opencode' / 'skills', 'OpenCode (own root)'),
    'cursor': (lambda: HOME / '.cursor' / 'skills', 'Cursor (own root)'),
    'roo': (lambda: HOME / '.roo' / 'skills', 'Roo Code (own root)'),
    'copilot': (lambda: HOME / '.copilot' / 'skills', 'GitHub Copilot (own root)'),
    'devin': (lambda: HOME / '.config' / 'devin' / 'skills', 'Devin Desktop / Windsurf (own root)'),
    'grok': (lambda: HOME / '.grok' / 'skills', 'xAI Grok Build CLI (own root)'),
}
DEFAULT_ALL = ['agents', 'claude-code', 'hermes', 'antigravity', 'cline']


def install(name, force, dry_run):
    root = TARGETS[name][0]()
    dest = root / SKILL.name
    if dest.exists() and not force:
        return f'skip   {name:12} {dest} (exists; use --force to replace)'
    if dry_run:
        return f'plan   {name:12} {dest}'
    root.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return f'ok     {name:12} {dest}'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--target', action='append', choices=sorted(TARGETS), default=[])
    ap.add_argument('--all', action='store_true', help='agents + claude-code + hermes + antigravity + cline')
    ap.add_argument('--force', action='store_true', help='replace an existing minimax-h3 folder')
    ap.add_argument('--dry-run', action='store_true', help='show planned writes, change nothing')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args(argv)
    if a.list or not (a.target or a.all):
        for k, (root, who) in TARGETS.items():
            print(f'{k:12} {root()}  — {who}')
        return 0 if a.list else 2
    if not (SKILL / 'SKILL.md').is_file():
        print(f'skill folder not found: {SKILL}', file=sys.stderr)
        return 1
    for name in dict.fromkeys((DEFAULT_ALL if a.all else []) + a.target):
        print(install(name, a.force, a.dry_run))
    return 0


if __name__ == '__main__':
    sys.exit(main())
