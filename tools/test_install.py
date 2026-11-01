"""Installer tests in a throwaway HOME: dry-run writes nothing, install copies the skill, existing copies need --force."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

INSTALL = Path(__file__).resolve().parent.parent / 'install.py'


def run(home, *args):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    env.pop('HERMES_HOME', None)
    env.pop('LOCALAPPDATA', None)
    return subprocess.run([sys.executable, '-B', str(INSTALL), *args], capture_output=True, text=True, env=env, timeout=30)


class InstallTests(unittest.TestCase):
    def test_dry_run_install_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            dest = home / '.agents' / 'skills' / 'minimax-h3'
            proc = run(home, '--target', 'agents', '--dry-run')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('plan', proc.stdout)
            self.assertFalse(dest.exists())

            proc = run(home, '--target', 'agents', '--target', 'claude-code')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((dest / 'SKILL.md').is_file())
            self.assertTrue((dest / 'scripts' / 'freevideo.py').is_file())
            self.assertTrue((home / '.claude' / 'skills' / 'minimax-h3' / 'SKILL.md').is_file())

            marker = dest / 'local-note.txt'
            marker.write_text('user file', encoding='utf-8')
            proc = run(home, '--target', 'agents')
            self.assertIn('skip', proc.stdout)
            self.assertTrue(marker.exists())
            proc = run(home, '--target', 'agents', '--force')
            self.assertIn('ok', proc.stdout)
            self.assertFalse(marker.exists())

    def test_all_covers_default_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            proc = run(home, '--all')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for root in ('.agents/skills', '.claude/skills', '.hermes/skills', '.gemini/config/skills', '.cline/skills'):
                self.assertTrue((home / root / 'minimax-h3' / 'SKILL.md').is_file(), root)

    def test_list_and_no_args(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(run(Path(directory), '--list').returncode, 0)
            self.assertEqual(run(Path(directory)).returncode, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
