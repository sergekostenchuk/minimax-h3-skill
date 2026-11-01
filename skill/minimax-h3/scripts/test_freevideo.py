"""Offline integration fixtures only: never call the real GPU server."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CLIENT = Path(__file__).with_name('freevideo.py')
SCRATCH = Path(tempfile.gettempdir()) / 'minimax-h3-skill-tests'
SCRATCH.mkdir(parents=True, exist_ok=True)

class ClientTests(unittest.TestCase):
    def test_plan_is_non_generating_and_uses_seconds(self):
        self.assertTrue(CLIENT.is_file(), 'The executable FreeVideo client is not implemented')
        received = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append((self.path, body, self.headers.get('Authorization')))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'spec': body, 'warnings': [], 'fixture': True}).encode())
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            token_path = root / 'token.txt'
            token_path.write_text('test-only-not-a-real-secret', encoding='utf-8')
            spec = {'kind': 'generate', 'prompt': 'A robot waters a plant.', 'seconds': 5,
                    'width': 1344, 'height': 768, 'quality': 'light', 'release_gpu_after': True}
            job = root / 'job.json'
            job.write_text(json.dumps(spec), encoding='utf-8')
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1'
                for quality in ('light', 'medium', 'high', 'max'):
                    spec['quality'] = quality
                    job.write_text(json.dumps(spec), encoding='utf-8')
                    proc = subprocess.run([sys.executable, '-B', str(CLIENT), '--base', url,
                                           '--token-file', str(token_path), 'post', '/plan',
                                           '--json', str(job)], capture_output=True, text=True, timeout=10)
                    self.assertEqual(proc.returncode, 0, proc.stderr)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(len(received), 4)
            self.assertEqual(received[0][0], '/freevideo/agent/v1/plan')
            self.assertEqual(received[0][1]['seconds'], 5)
            self.assertNotIn('duration', received[0][1])
            self.assertEqual(received[0][2], 'Bearer test-only-not-a-real-secret')
            self.assertNotIn('test-only-not-a-real-secret', proc.stdout + proc.stderr)
            self.assertTrue(json.loads(proc.stdout)['fixture'])

    def test_permission_boundary_blocks_before_reading_credentials(self):
        bad_cases = [
            (['--base', 'https://example.com/freevideo/agent/v1', 'get', '/schema'], 'security_blocked'),
            (['get', '/../../config'], 'security_blocked'),
            (['get', '//example.com/schema'], 'security_blocked'),
            (['post', '/jobs'], 'permission_blocked'),
            (['post', '/gpu/release'], 'permission_blocked'),
            (['get', '/connect'], 'security_blocked'),
        ]
        for arguments, category in bad_cases:
            with self.subTest(arguments=arguments):
                proc = subprocess.run([sys.executable, '-B', str(CLIENT),
                    '--token-file', str(CLIENT.parent / 'nonexistent-token'), *arguments],
                    capture_output=True, text=True, timeout=5)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(category, proc.stderr)
                self.assertNotIn('nonexistent-token', proc.stderr)

    def test_job_write_requires_apply_plans_once_and_reads_back(self):
        self.assertTrue(CLIENT.is_file())
        received = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def respond(self, data):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append(('POST', self.path, data))
                if self.path.endswith('/plan'):
                    self.respond({'spec': data, 'warnings': [], 'fixture': True})
                else:
                    self.respond({'job': {'id': 'j0123456789ab', 'status': 'waiting'}, 'fixture': True})
            def do_GET(self):
                received.append(('GET', self.path, None))
                self.respond({'job': {'id': 'j0123456789ab', 'status': 'waiting'}, 'fixture': True})
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root=Path(directory)
            secret=root/'token.txt'; secret.write_text('fixture-value', encoding='utf-8')
            job=root/'job.json'
            job.write_text(json.dumps({'kind':'generate','prompt':'Robot waters plant.',
                'seconds':5,'width':1344,'height':768,'quality':'light','release_gpu_after':True}),encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                args=[sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1',
                    '--token-file',str(secret),'post','/jobs','--json',str(job),'--apply']
                proc=subprocess.run(args,capture_output=True,text=True,timeout=10)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual([(m,p.rsplit('/',1)[-1]) for m,p,_ in received],
                             [('POST','plan'),('POST','jobs'),('GET','j0123456789ab')])
            self.assertEqual(json.loads(proc.stdout)['job']['id'],'j0123456789ab')

    def test_bad_generation_fields_fail_before_io(self):
        good={'kind':'generate','prompt':'Robot waters plant.','seconds':5,'width':1344,
              'height':768,'quality':'light','release_gpu_after':True}
        bad_specs=[dict(good, duration=20), dict(good, task='i2va'), dict(good, width=1000),
                   dict(good, seconds=0), dict(good, prompt=' '), dict(good, width=1008),
                   dict(good, height=240), dict(good, seconds=1), dict(good, quality='balanced')]
        missing=dict(good); del missing['seconds']; bad_specs.append(missing)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root=Path(directory); spec=root/'job.json'
            for body in bad_specs:
                with self.subTest(body=body):
                    spec.write_text(json.dumps(body),encoding='utf-8')
                    proc=subprocess.run([sys.executable,'-B',str(CLIENT),'--token-file',str(root/'missing'),
                        'post','/plan','--json',str(spec)],capture_output=True,text=True,timeout=5)
                    self.assertNotEqual(proc.returncode,0)
                    self.assertIn('schema_mismatch',proc.stderr)
                    self.assertNotIn('No such file',proc.stderr)

    def test_last_frame_and_binary_download_are_verified(self):
        received=[]; blob=b'fixture-not-a-real-image'
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append(('POST',self.path,body)); self.send_response(200)
                self.send_header('Content-Type','application/json');self.end_headers()
                result={'file':'fixture.png','url':'/freevideo/agent/v1/media/input/fixture.png'} if self.path.endswith('/frame') else {'type':'image','width':1,'height':1,'fixture':True}
                self.wfile.write(json.dumps(result).encode())
            def do_GET(self):
                received.append(('GET',self.path,None));self.send_response(200)
                self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(blob)))
                self.end_headers();self.wfile.write(blob)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root=Path(directory);token=root/'token';token.write_text('fixture-value',encoding='utf-8')
            payload=root/'frame.json'; payload.write_text(json.dumps({'source':{'library':'2026-01-01/'+'a'*32,'frame':'last'}}),encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            common=[sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1','--token-file',str(token)]
            try:
                frame=subprocess.run(common+['post','/media/frame','--json',str(payload),'--apply'],capture_output=True,text=True,timeout=10)
                self.assertEqual(frame.returncode,0,frame.stderr)
                self.assertEqual([(m,p.rsplit('/',1)[-1]) for m,p,_ in received],[('POST','frame'),('POST','inspect')])
                self.assertEqual(received[0][2]['source']['frame'],'last')
                target=root/'frame.png'
                download=subprocess.run(common+['get','/media/input/fixture.png','--save',str(target)],capture_output=True,text=True,timeout=10)
                self.assertEqual(download.returncode,0,download.stderr)
                self.assertEqual(target.read_bytes(),blob)
                self.assertEqual(json.loads(download.stdout)['bytes'],len(blob))
                overwrite=subprocess.run(common+['get','/media/input/fixture.png','--save',str(target)],capture_output=True,text=True,timeout=10)
                self.assertNotEqual(overwrite.returncode,0)
                self.assertEqual(target.read_bytes(),blob)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)

    def test_warning_blocks_jobs_until_exactly_accepted(self):
        warning='Reference generation is experimental'
        def serve(received):
            class Handler(BaseHTTPRequestHandler):
                def log_message(self,*args):pass
                def do_POST(self):
                    body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                    received.append(self.path.rsplit('/',1)[-1])
                    self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
                    if self.path.endswith('/plan'):
                        payload={'spec':body,'warnings':[warning]}
                    else:
                        payload={'job':{'id':'j0123456789ab','status':'waiting'}}
                    self.wfile.write(json.dumps(payload).encode())
                def do_GET(self):
                    received.append(self.path.rsplit('/',1)[-1])
                    self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
                    self.wfile.write(json.dumps({'job':{'id':'j0123456789ab','status':'waiting'}}).encode())
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            return server,thread
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root=Path(directory);token=root/'token';token.write_text('fixture-value',encoding='utf-8')
            job=root/'job.json'
            job.write_text(json.dumps({'kind':'generate','prompt':'Robot waters plant.','seconds':10,
                'width':1344,'height':768,'quality':'light','release_gpu_after':True,
                'media':{'references':['freevideo/agent/assets/a.png']}}),encoding='utf-8')
            for accepted,expect_submit in (([],False),([warning],True),(['Reference generation is experiment'],False)):
                received=[]
                server,thread=serve(received)
                try:
                    args=[sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1',
                          '--token-file',str(token),'post','/jobs','--json',str(job),'--apply']
                    for text in accepted: args+=['--accept-warning',text]
                    proc=subprocess.run(args,capture_output=True,text=True,timeout=10)
                finally:
                    server.shutdown();server.server_close();thread.join(timeout=2)
                with self.subTest(accepted=accepted):
                    self.assertIn('plan',received)
                    if expect_submit:
                        self.assertEqual(proc.returncode,0,proc.stderr)
                        self.assertIn('jobs',received)
                        self.assertEqual(json.loads(proc.stdout)['accepted_warnings'],[warning])
                    else:
                        self.assertNotEqual(proc.returncode,0)
                        self.assertNotIn('jobs',received)

    def test_root_status_does_not_append_a_slash(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200 if self.path=='/freevideo/agent/v1' else 404)
                self.end_headers();self.wfile.write(b'{"ready":true}')
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            token=Path(directory)/'token';token.write_text('fixture-value',encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                proc=subprocess.run([sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1',
                    '--token-file',str(token),'get','/'],capture_output=True,text=True,timeout=5)
                self.assertEqual(proc.returncode,0,proc.stderr)
                self.assertTrue(json.loads(proc.stdout)['ready'])
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)

    def _serve_plan(self, received, reply=None):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers()
                self.wfile.write(json.dumps(reply or {},ensure_ascii=False).encode('utf-8'))
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append((self.path,body));self.send_response(200)
                self.send_header('Content-Type','application/json');self.end_headers()
                self.wfile.write(json.dumps({'spec':body,'warnings':[]}).encode())
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        return server,thread

    def test_non_ascii_reply_on_legacy_console(self):
        reply={'note':'Сетка кадров 17n+5 — 字幕','ready':True}
        server,thread=self._serve_plan([],reply)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            token=Path(directory)/'token';token.write_text('fixture-value',encoding='utf-8')
            env=dict(os.environ,PYTHONIOENCODING='cp1252')
            try:
                proc=subprocess.run([sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1',
                    '--token-file',str(token),'get','/guide'],capture_output=True,timeout=10,env=env)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)
            self.assertEqual(proc.returncode,0,proc.stderr.decode('utf-8','replace'))
            self.assertEqual(json.loads(proc.stdout.decode('utf-8'))['note'],reply['note'])

    def test_aspect_and_continuation_fields_pass_through(self):
        received=[]
        server,thread=self._serve_plan(received)
        base={'kind':'generate','prompt':'The camera keeps rising.','seconds':20,'quality':'light','release_gpu_after':True}
        good=[dict(base,aspect='9:16'),
              dict(base,width=1344,height=768,continue_from={'from_job':'j0123456789ab'},
                   part_prompts=['Part one.','Part two.'],first_frame_reference=True,seed=101,
                   loras=[{'name':'style.safetensors','strength':0.8}],
                   media={'first':{'from_job':'j0123456789ab','frame':'last'}})]
        bad=dict(base,aspect='9:16',width=768)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root=Path(directory);token=root/'token';token.write_text('fixture-value',encoding='utf-8');spec=root/'job.json'
            common=[sys.executable,'-B',str(CLIENT),'--base',f'http://127.0.0.1:{server.server_port}/freevideo/agent/v1','--token-file',str(token)]
            try:
                for body in good:
                    spec.write_text(json.dumps(body),encoding='utf-8')
                    proc=subprocess.run(common+['post','/plan','--json',str(spec)],capture_output=True,text=True,timeout=10)
                    self.assertEqual(proc.returncode,0,proc.stderr)
                spec.write_text(json.dumps(bad),encoding='utf-8')
                proc=subprocess.run(common+['post','/plan','--json',str(spec)],capture_output=True,text=True,timeout=10)
                self.assertNotEqual(proc.returncode,0)
                self.assertIn('schema_mismatch',proc.stderr)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)
        self.assertEqual(len(received),2)
        self.assertEqual(received[0][1]['aspect'],'9:16')
        self.assertEqual(received[1][1]['continue_from'],{'from_job':'j0123456789ab'})
        self.assertEqual(received[1][1]['media']['first']['frame'],'last')
        self.assertEqual(received[1][1]['part_prompts'],['Part one.','Part two.'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
