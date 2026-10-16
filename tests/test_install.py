"""Exercise installer filesystem effects in an isolated home; never touch the desktop."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.commands = self.home / 'commands'
        self.commands.mkdir()
        self.log = self.home / 'calls'
        self.env = dict(os.environ, HOME=str(self.home), PATH=f'{self.commands}:/usr/bin:/bin', CALL_LOG=str(self.log))
        for command in ['systemctl', 'hyprctl']:
            script = self.commands / command
            script.write_text('''#!/bin/bash
printf '%s %s\\n' "$(basename "$0")" "$*" >> "$CALL_LOG"
if [[ "$*" == *is-active* ]]; then exit 3; fi
if [[ "$*" == configerrors ]]; then printf 'ok\\n'; fi
''')
            script.chmod(0o755)
        self.hypr = self.home / '.config/hypr/hyprland.lua'
        self.hypr.parent.mkdir(parents=True)
        self.hypr.write_text('-- user configuration\n')
        self.binary = self.home / 'release-presto'
        self.binary.write_text('#!/bin/bash\nprintf \'{"ready":true,"isRunning":false,"isPaused":false}\\n\'\n')
        self.binary.chmod(0o755)
        self.plugin = self.home / '.config/omarchy/plugins/konko.presto'
        self.plugin.mkdir(parents=True)
        (self.plugin / 'manifest.json').write_text('git-managed-plugin-must-not-change')
        self.data = self.home / '.local/share/com.presto.app/session.json'
        self.data.parent.mkdir(parents=True)
        self.data.write_text('existing session history')

    def install(self, binary=None):
        return subprocess.run(['bash', str(ROOT / 'install-runtime.sh'), str(binary or self.binary)], env=self.env, capture_output=True, text=True)

    def test_fresh_install_starts_original_runtime_without_overwriting_plugin_or_history(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / '.local/bin/presto').read_bytes(), self.binary.read_bytes())
        self.assertEqual((self.home / '.config/systemd/user/presto-omarchy.service').read_bytes(), (ROOT / 'presto-omarchy.service').read_bytes())
        self.assertEqual((self.plugin / 'manifest.json').read_text(), 'git-managed-plugin-must-not-change')
        self.assertEqual(self.data.read_text(), 'existing session history')
        self.assertIn('enable --now presto-omarchy.service', self.log.read_text())
        self.assertNotIn('restart shell', self.log.read_text())

    def test_reinstall_keeps_one_hyprland_include_and_backs_up_previous_files(self):
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.hypr.read_text().count('require("hypr.presto")'), 1)
        backups = list((self.home / '.local/state/presto-omarchy/backups').glob('*/presto'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), self.binary.read_bytes())

    def test_active_session_is_not_interrupted(self):
        target = self.home / '.local/bin/presto'
        target.parent.mkdir(parents=True)
        target.write_text('#!/bin/bash\nprintf \'{"ready":true,"isRunning":true,"isPaused":false}\\n\'\n')
        target.chmod(0o755)
        original = target.read_bytes()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('active', result.stderr.lower())
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(self.hypr.read_text(), '-- user configuration\n')
        self.assertFalse(self.log.exists())

    def test_missing_binary_fails_before_changing_configuration(self):
        result = self.install(self.home / 'missing')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.hypr.read_text(), '-- user configuration\n')
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
