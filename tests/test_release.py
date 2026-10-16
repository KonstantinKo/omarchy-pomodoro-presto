"""Package actual tracked source and executable bytes, without publishing anything."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'presto'
        self.source.mkdir()
        self.out = Path(self.tmp.name) / 'output'
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.source / 'LICENSE.md').write_text('original license')
        (self.source / 'engine.rs').write_text('original engine source')
        self.git('add', '.')
        self.git('commit', '-m', 'fixture source')
        self.revision = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.source / 'private-untracked-file').write_text('must not be distributed')
        self.binary = self.source / 'target/release/presto'
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b'\x7fELF\x02\x01' + bytes(12) + b'\x3e\x00fixture executable')
        self.binary.chmod(0o755)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.source), *args], capture_output=True, text=True, check=True)

    def package(self):
        return subprocess.run(['python3', str(ROOT / 'tools/build_release.py'), '--source', str(self.source), '--output', str(self.out)], capture_output=True, text=True)

    def test_release_contains_matching_binary_license_source_and_checksums(self):
        result = self.package()
        self.assertEqual(result.returncode, 0, result.stderr)
        archives = list(self.out.glob('*.tar.gz'))
        self.assertEqual(len(archives), 2)
        source = next(p for p in archives if p.name.endswith('-source.tar.gz'))
        runtime = next(p for p in archives if 'linux-x86_64' in p.name)
        with tarfile.open(source) as archive:
            self.assertEqual(archive.extractfile('presto-source/engine.rs').read(), b'original engine source')
            self.assertFalse(any('private-untracked-file' in n for n in archive.getnames()))
        with tarfile.open(runtime) as archive:
            self.assertEqual(archive.extractfile('presto').read(), self.binary.read_bytes())
            self.assertEqual(archive.getmember('presto').mode, 0o755)
            self.assertEqual(archive.extractfile('LICENSE.md').read(), b'original license')
            info = json.load(archive.extractfile('BUILD.json'))
            self.assertEqual(info['source_revision'], self.revision)
            self.assertEqual(info['source_archive'], source.name)
        checksums = (self.out / 'SHA256SUMS').read_text().splitlines()
        self.assertEqual(len(checksums), 2)
        for line in checksums:
            digest, name = line.split('  ')
            self.assertEqual(digest, hashlib.sha256((self.out / name).read_bytes()).hexdigest())
        original = {p.name: p.read_bytes() for p in self.out.iterdir()}
        self.assertEqual(self.package().returncode, 0)
        self.assertEqual(original, {p.name: p.read_bytes() for p in self.out.iterdir()})

    def test_dirty_tracked_source_is_refused(self):
        (self.source / 'engine.rs').write_text('uncommitted source')
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('uncommitted', result.stderr.lower())
        self.assertFalse(self.out.exists())

    def test_wrong_architecture_is_refused(self):
        self.binary.write_bytes(b'not a Linux executable')
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('x86_64', result.stderr)
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
