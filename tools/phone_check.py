"""Scoped diagnostics for the connected Shici app; never clear application data."""
from pathlib import Path
import os,subprocess,sys,xml.etree.ElementTree as ET,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
ADB=ROOT/'.tooling/android/platform-tools/platform-tools/adb.exe'
ENV=os.environ.copy();ENV['ANDROID_USER_HOME']=str(ROOT/'.tooling/android-user')
DEVICE='10AE4J2TQ0000KL'
def adb(*args):return subprocess.check_output([str(ADB),'-s',DEVICE,*args],env=ENV)
def ui():
    adb('shell','uiautomator','dump','/sdcard/shici-ui.xml')
    data=adb('shell','cat','/sdcard/shici-ui.xml')
    (ROOT/'tmp/phone-ui.xml').write_bytes(data)
    return ET.fromstring(data)
def inspect():
    for n in ui().iter('node'):
        if n.get('package')!='cn.shici.wordbook':continue
        label=n.get('text') or n.get('content-desc')
        if label and n.get('bounds')!='[0,0][0,0]':print(label,n.get('bounds'))
command=sys.argv[1]
if command=='inspect':inspect()
elif command=='tap':
    label=sys.argv[2].strip();nodes=[n for n in ui().iter('node') if n.get('package')=='cn.shici.wordbook' and label in [(n.get('text') or '').strip(),(n.get('content-desc') or '').strip()] and n.get('bounds')!='[0,0][0,0]']
    if not nodes:raise ValueError('No visible app control: '+label)
    coords=list(map(int,re.findall(r'\d+',nodes[0].get('bounds'))));adb('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2))
    inspect()
elif command=='logs':
    pid=adb('shell','pidof','cn.shici.wordbook').decode().strip().split()[0]
    data=adb('logcat','-d','--pid='+pid,'-t','250').decode('utf-8',errors='replace')
    (ROOT/'tmp/phone-shici-log.txt').write_text(data,encoding='utf-8');print(data)
elif command=='shot':
    name=Path(sys.argv[2]).name
    dest=ROOT/'output/screenshots'/name
    dest.write_bytes(adb('exec-out','screencap','-p'));print(dest)
elif command=='install':
    apk=ROOT/'output'/Path(sys.argv[2]).name
    if apk.suffix!='.apk':raise ValueError('APK required')
    print(adb('install','-r',str(apk)).decode());print(adb('shell','am','start','-n','cn.shici.wordbook/.MainActivity').decode())
elif command=='hash':
    for name in ['tmp/phone-base-1.0.4.apk','output/shici-1.0.4.apk']:
        print(name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
else:raise ValueError('Unknown diagnostic command')
