"""Install the official Godot binary after checking the release SHA-512 manifest."""
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path
version = '4.6.3-stable'
name = f'Godot_v{version}_linux.x86_64.zip'
base = f'https://github.com/godotengine/godot/releases/download/{version}/'
with urllib.request.urlopen(base + 'SHA512-SUMS.txt') as response:
    sums = response.read().decode()
expected = next(line.split()[0] for line in sums.splitlines() if line.split()[-1].lstrip('*') == name)
with urllib.request.urlopen(base + name) as response:
    data = response.read()
if hashlib.sha512(data).hexdigest() != expected:
    raise RuntimeError('Godot download checksum mismatch')
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    binary = next(entry for entry in archive.namelist() if entry.endswith('linux.x86_64'))
    target = Path('/usr/local/bin/godot')
    target.write_bytes(archive.read(binary))
    target.chmod(0o755)
