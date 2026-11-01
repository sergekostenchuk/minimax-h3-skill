#!/usr/bin/env python3
"""Validate the minimax-h3 skill package: Agent Skills frontmatter, referenced files, JSON assets, no private data.
Stdlib only. Usage: python tools/validate_skill.py [skill_dir]"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'skill' / 'minimax-h3'
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
PRIVATE = [
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), 'IPv4 address'),
    (re.compile(r'[A-Za-z]:\\Users\\', re.I), 'Windows user path'),
    (re.compile(r'/Users/[A-Za-z0-9._-]+/'), 'macOS user path'),
    (re.compile(r'/home/[A-Za-z0-9._-]+/'), 'Linux user path'),
    (re.compile(r'\b(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,})'), 'API key'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._-]{24,}'), 'bearer token'),
    (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}'), 'e-mail address'),
]
ALLOWED_IPS = {'127.0.0.1'}
errors = []


def fail(msg):
    errors.append(msg)


def frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        fail('SKILL.md: missing YAML frontmatter')
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(':')
        if sep and not line.startswith(' '):
            fields[k.strip()] = v.strip().strip('"')
    return fields


skill_md = SKILL / 'SKILL.md'
if not skill_md.is_file():
    sys.exit(f'FAIL: {skill_md} not found')
text = skill_md.read_text(encoding='utf-8')
meta = frontmatter(text)
name, desc = meta.get('name', ''), meta.get('description', '')
if not NAME_RE.fullmatch(name) or len(name) > 64:
    fail(f'SKILL.md: name {name!r} must be lowercase-hyphen, at most 64 chars')
if name != SKILL.name:
    fail(f'SKILL.md: name {name!r} must match folder {SKILL.name!r}')
if not desc or len(desc) > 1024:
    fail(f'SKILL.md: description must be 1..1024 chars (got {len(desc)})')
if len(text.splitlines()) > 500:
    fail('SKILL.md: keep the body under 500 lines; move detail to references/')

# every referenced bundled file exists
for doc in [skill_md, *SKILL.glob('references/*.md')]:
    body = doc.read_text(encoding='utf-8')
    for ref in sorted(set(re.findall(r'`((?:references|assets|scripts)/[\w./-]+\.(?:md|json|py))`', body))):
        if not (SKILL / ref).is_file():
            fail(f'{doc.relative_to(SKILL)}: referenced file {ref} does not exist')
    if doc != skill_md:
        continue  # references may name upstream files (e.g. shot-table-spec.md); bare names are links only in SKILL.md
    for ref in sorted(set(re.findall(r'`([\w-]+\.md)`', body))):
        if not (SKILL / 'references' / ref).is_file() and not (SKILL / ref).is_file():
            fail(f'{doc.relative_to(SKILL)}: referenced file {ref} does not exist')

# JSON assets parse; job examples follow the FreeVideo contract
for path in SKILL.glob('assets/*.json'):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        fail(f'{path.name}: invalid JSON ({exc})')
        continue
    if path.name.startswith('job-'):
        if data.get('kind') != 'generate' or 'duration' in data or 'task' in data:
            fail(f'{path.name}: job must use kind=generate and seconds, never duration/task')
        if not isinstance(data.get('seconds'), (int, float)) or not isinstance(data.get('prompt'), str):
            fail(f'{path.name}: job needs numeric seconds and a prompt')
    if path.name == 'evals.json':
        ids = [e.get('id') for e in data.get('evals', [])]
        if len(ids) != len(set(ids)) or not ids:
            fail('evals.json: eval ids must be present and unique')

# no private data anywhere in the repository text files
for path in sorted(set(ROOT.rglob('*')) | set(SKILL.rglob('*'))):
    if not path.is_file() or '.git' in path.parts or path.suffix not in {'.md', '.py', '.json', '.yml', '.yaml', '.txt', ''}:
        continue
    if path.name == 'LICENSE' or path == Path(__file__).resolve():
        continue
    content = path.read_text(encoding='utf-8', errors='replace')
    for rx, label in PRIVATE:
        for m in rx.finditer(content):
            if label == 'IPv4 address' and m.group(0) in ALLOWED_IPS:
                continue
            if label == 'e-mail address' and m.group(0).endswith(('@anthropic.com', '@users.noreply.github.com')):
                continue
            if label == 'bearer token' and re.search(r'test-only|fixture|not-a-real', m.group(0)):
                continue  # deliberate fake credential in offline test fixtures
            where = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            fail(f'{where}: possible {label}: {m.group(0)[:40]}')

if errors:
    print('\n'.join('FAIL: ' + e for e in errors))
    sys.exit(1)
print(f'OK: {name} — frontmatter, {len(list(SKILL.rglob("*.md")))} markdown files, assets and privacy checks passed')
