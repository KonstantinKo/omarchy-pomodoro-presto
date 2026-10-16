#!/usr/bin/env python3
"""Build local release assets from an already-tested Presto checkout. No network writes."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def git(source, *args):
    return subprocess.check_output(['git', '-C', str(source), *args])


def compressed(data):
    return gzip.compress(data, mtime=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    source = args.source.resolve()
    for options in [('diff', '--quiet'), ('diff', '--cached', '--quiet')]:
        if subprocess.run(['git', '-C', str(source), *options], check=False).returncode:
            parser.error('Presto has uncommitted tracked source changes; commit them before packaging')
    binary = source / 'target/release/presto'
    if not binary.is_file():
        parser.error('Build and test target/release/presto first')
    header = binary.read_bytes()[:20]
    if len(header) < 20 or header[:6] != b'\x7fELF\x02\x01' or header[18:20] != b'\x3e\x00':
        parser.error('The runtime must be a Linux x86_64 ELF executable')
    version = json.loads((ROOT / 'manifest.json').read_text())['version']
    revision = git(source, 'rev-parse', 'HEAD').decode().strip()
    prefix = f'presto-omarchy-{version}'
    source_name = f'{prefix}-source.tar.gz'
    runtime_name = f'{prefix}-linux-x86_64.tar.gz'
    info = json.dumps({
        'plugin_version': version,
        'platform': 'linux-x86_64',
        'source_revision': revision,
        'source_archive': source_name,
        'source_repository': 'https://github.com/KonstantinKo/presto',
    }, indent=2).encode() + b'\n'
    # Read tracked license bytes, just as the source archive does.
    license_text = git(source, 'show', 'HEAD:LICENSE.md')
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, data, mode in [('presto', binary.read_bytes(), 0o755), ('LICENSE.md', license_text, 0o644), ('BUILD.json', info, 0o644)]:
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            entry.mode = mode
            archive.addfile(entry, io.BytesIO(data))
    assets = {
        runtime_name: compressed(output.getvalue()),
        source_name: compressed(git(source, 'archive', '--format=tar', '--prefix=presto-source/', 'HEAD')),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    sums = []
    for name, data in sorted(assets.items()):
        (args.output / name).write_bytes(data)
        sums.append(f'{hashlib.sha256(data).hexdigest()}  {name}\n')
    (args.output / 'SHA256SUMS').write_text(''.join(sums))
    print(f'Prepared {version} from Presto {revision}: {args.output.resolve()}')


if __name__ == '__main__':
    main()
