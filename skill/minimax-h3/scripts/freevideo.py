"""Small stdlib-only local FreeVideo client; no automatic retry or installs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import re
import hashlib
from urllib.parse import urlsplit, unquote
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

DEFAULT_BASE = 'http://127.0.0.1:8188/freevideo/agent/v1'

# Windows consoles default to a legacy code page; server replies contain non-ASCII text.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default=DEFAULT_BASE)
    parser.add_argument('--token-file', type=Path, default=Path.home() / 'FreeVideo/FreeVideo-engine/agent/token')
    parser.add_argument('method', choices=['get', 'post'])
    parser.add_argument('endpoint')
    parser.add_argument('--json', dest='json_file', type=Path)
    parser.add_argument('--save', type=Path, help='Download a media URL to a new local file')
    parser.add_argument('--apply', action='store_true', help='Authorize the explicitly requested state-changing POST')
    parser.add_argument('--accept-warning', action='append', default=[], metavar='TEXT',
                        help='Allow one exact /plan warning to pass the submission guard; repeatable. '
                             'Without it, any warning blocks POST /jobs.')
    args = parser.parse_args(argv)
    secret = ''
    try:
        parsed = urlsplit(args.base)
        if (parsed.scheme not in {'http', 'https'} or parsed.hostname not in {'127.0.0.1', '::1'}
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.path.rstrip('/') != '/freevideo/agent/v1'):
            raise ValueError('security_blocked: only literal loopback FreeVideo URLs are permitted')
        endpoint = unquote(args.endpoint)
        if endpoint == '/':
            endpoint = ''
        if ('..' in endpoint or '\\' in endpoint or endpoint.startswith('//')
                or '#' in endpoint or '://' in endpoint):
            raise ValueError('security_blocked: invalid endpoint')
        get_allowed = re.fullmatch(r'(?:|/|/(?:schema|openapi\.json|guide|queue|jobs|library)|/capabilities(?:\?[a-zA-Z0-9_=&.-]+)?|/jobs/j[0-9a-f]{12}(?:\?wait=(?:[0-9]|1[0-9]|2[0-5]))?|/library/\d{4}-\d{2}-\d{2}/[0-9a-f]{32}(?:/(?:file|thumbnail))?|/media/input/[a-zA-Z0-9_./-]+)', endpoint)
        if args.method == 'get' and not get_allowed:
            raise ValueError('security_blocked: GET endpoint is not allowlisted')
        body = json.loads(args.json_file.read_text(encoding='utf-8-sig')) if args.json_file else None
        if args.method == 'post':
            if endpoint not in {'/plan', '/jobs', '/media', '/media/frame', '/media/inspect'} or (endpoint not in {'/plan', '/media/inspect'} and not args.apply):
                raise ValueError('permission_blocked: POST not allowed or --apply missing')
            if not isinstance(body, dict):
                raise ValueError('schema_mismatch: POST requires a JSON object')
        if args.method == 'post' and endpoint in {'/plan', '/jobs'}:
            if body.get('kind') != 'generate' or 'duration' in body or 'task' in body:
                raise ValueError('schema_mismatch: helper supports kind=generate; use seconds, never duration/task')
            seconds = body.get('seconds')
            if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not 1.625 <= seconds <= 60:
                raise ValueError('schema_mismatch: seconds must be explicit and in [1.625, 60]; /plan applies actual model limits')
            if not isinstance(body.get('prompt'), str) or not body['prompt'].strip():
                raise ValueError('schema_mismatch: non-empty prompt is required')
            if 'aspect' in body:
                if 'width' in body or 'height' in body or not isinstance(body['aspect'], str) or not body['aspect'].strip():
                    raise ValueError('schema_mismatch: use either aspect (+ optional megapixels) or width/height, not both')
            else:
                for dimension in ('width', 'height'):
                    value = body.get(dimension)
                    if isinstance(value, bool) or not isinstance(value, int) or not 256 <= value <= 4096 or value % 32:
                        raise ValueError('schema_mismatch: explicit dimensions in [256,4096] divisible by 32 (or aspect) are required')
            if body.get('quality') not in {'light', 'medium', 'high', 'max'} or not isinstance(body.get('release_gpu_after'), bool):
                raise ValueError('schema_mismatch: explicit quality and boolean release_gpu_after are required')
        if args.save:
            if args.method != 'get' or not re.fullmatch(r'(?:/media/input/[a-zA-Z0-9_./-]+|/library/\d{4}-\d{2}-\d{2}/[0-9a-f]{32}/(?:file|thumbnail))', endpoint):
                raise ValueError('security_blocked: --save is only supported for allowlisted media GETs')
            if args.save.exists():
                raise ValueError('permission_blocked: destination exists; refusing to overwrite')
        secret = args.token_file.read_text(encoding='utf-8').strip()
        if not secret:
            raise ValueError('permission_blocked: token file is empty')
        opener = build_opener(ProxyHandler({}), NoRedirect())
        def call(method, path, payload=None):
            data = None if payload is None else json.dumps(payload, ensure_ascii=False, allow_nan=False).encode('utf-8')
            request = Request(args.base.rstrip('/') + path, data=data, method=method,
                              headers={'Authorization': 'Bearer ' + secret, 'Content-Type': 'application/json'})
            with opener.open(request, timeout=40) as response:
                return json.load(response)
        if args.save:
            request = Request(args.base.rstrip('/') + endpoint, headers={'Authorization': 'Bearer ' + secret})
            count = 0
            digest = hashlib.sha256()
            created = False
            try:
                with opener.open(request, timeout=40) as response:
                    media_type = response.headers.get('Content-Type', '').split(';', 1)[0]
                    if not (media_type.startswith(('image/', 'video/', 'audio/')) or media_type == 'application/octet-stream'):
                        raise ValueError('partial_output: expected media, not an error or HTML page')
                    with args.save.open('xb') as destination:
                        created = True
                        while chunk := response.read(1024 * 1024):
                            destination.write(chunk); digest.update(chunk); count += len(chunk)
                    declared = response.headers.get('Content-Length')
                    if not count or (declared and int(declared) != count):
                        raise ValueError('partial_output: empty or truncated download')
            except (OSError, ValueError):
                if created:
                    args.save.unlink(missing_ok=True)
                raise
            print(json.dumps({'file': str(args.save.resolve()), 'bytes': count, 'sha256': digest.hexdigest()}, ensure_ascii=False))
            return 0
        if args.method == 'post' and endpoint == '/jobs':
            plan = call('POST', '/plan', body)
            warnings = plan.get('warnings') or []
            unaccepted = [w for w in warnings if w not in args.accept_warning]
            if unaccepted:
                raise ValueError('schema_mismatch: plan has warnings; inspect /plan before submitting '
                                 '(pass --accept-warning with the exact warning text to allow one): '
                                 + ' | '.join(unaccepted))
        result = call(args.method.upper(), endpoint, body)
        if args.method == 'post' and endpoint == '/jobs':
            job_id = result.get('job', {}).get('id')
            if not isinstance(job_id, str) or not re.fullmatch(r'j[0-9a-f]{12}', job_id):
                raise ValueError('partial_output: submit returned no valid job ID; inspect /jobs, do not resubmit')
            try:
                result = call('GET', '/jobs/' + job_id)
            except (OSError, ValueError) as exc:
                raise ValueError('partial_output: job ' + job_id + ' submitted, readback failed; poll this ID, do not resubmit') from exc
            result['accepted_warnings'] = warnings
        if args.method == 'post' and endpoint in {'/media', '/media/frame'}:
            uploaded_file = result.get('file')
            if not isinstance(uploaded_file, str) or not uploaded_file:
                raise ValueError('partial_output: media write returned no file; inspect result, do not repeat blindly')
            result['inspection'] = call('POST', '/media/inspect', {'source': uploaded_file})
        print(json.dumps(result, ensure_ascii=False).replace(secret, '[REDACTED]'))
        return 0
    except (OSError, ValueError) as exc:
        detail = str(exc).replace(secret, '[REDACTED]') if secret else str(exc)
        print(json.dumps({'ok': False, 'error': detail}, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
