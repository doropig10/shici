from pathlib import Path
import urllib.request, hashlib, zipfile, concurrent.futures, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / '.tooling' / 'android'
SDK.mkdir(parents=True, exist_ok=True)
repo = ET.parse(ROOT / 'tmp' / 'android-repository.xml').getroot()
targets = {'platform-35_r02.zip': 'platform', 'build-tools_r35_windows.zip': 'build-tools', 'platform-tools_r37.0.1-win.zip': 'platform-tools'}
tasks = []
for package in repo.findall('remotePackage'):
    for archive in package.findall('./archives/archive/complete'):
        url = archive.findtext('url')
        if url in targets:
            tasks.append((url, archive.findtext('checksum')))

def download(task):
    name, checksum = task
    dest = SDK / name
    if not dest.exists() or hashlib.sha1(dest.read_bytes()).hexdigest() != checksum:
        print('Downloading', name, flush=True)
        with urllib.request.urlopen('https://dl.google.com/android/repository/' + name, timeout=90) as response, dest.open('wb') as out:
            while data := response.read(1024 * 1024):
                out.write(data)
    assert hashlib.sha1(dest.read_bytes()).hexdigest() == checksum, 'Checksum mismatch: ' + name
    with zipfile.ZipFile(dest) as z:
        base = (SDK / targets[name]).resolve()
        for item in z.namelist():
            assert (base / item).resolve().is_relative_to(base)
        z.extractall(base)
    print('Verified and extracted', name, flush=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(download, tasks))
