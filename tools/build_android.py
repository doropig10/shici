from pathlib import Path
import subprocess, json, secrets, zipfile, hashlib, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
JAVA=Path(r'D:\app\PyCharm 2025.2\jbr\bin')
SDK=ROOT/'.tooling/android'
BT=SDK/'build-tools/android-15'
JAR=SDK/'platform/android-35/android.jar'
BUILD=ROOT/'build'
OUT=ROOT/'output'
for d in [BUILD,OUT,BUILD/'classes',BUILD/'dex']: d.mkdir(parents=True,exist_ok=True)
def run(args,cwd=ROOT):
    subprocess.run([str(x) for x in args],check=True,cwd=cwd)

src=ROOT/'app/src/main'
run([BT/'aapt2.exe','compile','--dir',src/'res','-o',BUILD/'resources.zip'])
run([BT/'aapt2.exe','link','-o',BUILD/'base.apk','-I',JAR,'--manifest',src/'AndroidManifest.xml',BUILD/'resources.zip','-A',src/'assets','--min-sdk-version','26','--target-sdk-version','35'])
run([JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',JAR,'-d',BUILD/'classes',*src.glob('java/**/*.java')])
run([JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',JAR,'--min-api','26','--output',BUILD/'dex',*(BUILD/'classes').rglob('*.class')])
run([BT/'aapt.exe','add',BUILD/'base.apk',*[p.name for p in (BUILD/'dex').glob('*.dex')]],cwd=BUILD/'dex')
# Force ordinary streaming reads for image assets. Keep resources.arsc and all
# non-image entry compression unchanged, then align before signing as usual.
with zipfile.ZipFile(BUILD/'base.apk') as source, zipfile.ZipFile(BUILD/'image-streams.apk','w') as target:
    for entry in source.infolist():
        payload=source.read(entry)
        if entry.filename.startswith('assets/') and entry.filename.endswith('.webp'):
            entry.compress_type=zipfile.ZIP_DEFLATED
        target.writestr(entry,payload)
run([BT/'zipalign.exe','-f','-p','4',BUILD/'image-streams.apk',BUILD/'aligned.apk'])
key=ROOT/'.tooling/shici-release.jks'
config=ROOT/'.tooling/signing.json'
if not key.exists():
    password=secrets.token_urlsafe(24)
    config.write_text(json.dumps({'password':password}),encoding='utf-8')
    run([JAVA/'keytool.exe','-genkeypair','-keystore',key,'-storepass',password,'-keypass',password,'-alias','shici','-keyalg','RSA','-keysize','2048','-validity','10950','-dname','CN=Shici Personal Wordbook, O=Personal, C=CN'])
password=json.loads(config.read_text(encoding='utf-8'))['password']
version=ET.parse(src/'AndroidManifest.xml').getroot().get('{http://schemas.android.com/apk/res/android}versionName')
apk=OUT/f'shici-{version}.apk'
run([JAVA/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--ks',key,'--ks-key-alias','shici','--ks-pass','pass:'+password,'--key-pass','pass:'+password,'--out',apk,BUILD/'aligned.apk'])
run([JAVA/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--verbose',apk])
with zipfile.ZipFile(apk) as archive:
    assert archive.testzip() is None, 'APK archive integrity failed'
    for entry in archive.infolist():
        if entry.filename.startswith('assets/') and entry.filename.endswith('.webp'):
            assert entry.compress_type==zipfile.ZIP_DEFLATED
            assert archive.read(entry)==(src/entry.filename).read_bytes(), entry.filename
print('Verified all packaged image bytes and streaming compression.')
sha=hashlib.sha256(apk.read_bytes()).hexdigest()
(OUT/f'shici-{version}.sha256.txt').write_text(sha+'  '+apk.name+'\n',encoding='utf-8')
print('APK:',apk,'MB:',round(apk.stat().st_size/1024/1024,1),'SHA256:',sha)
