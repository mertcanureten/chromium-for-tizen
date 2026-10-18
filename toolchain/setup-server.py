import hashlib,json,pathlib,tarfile,urllib.request
root=pathlib.Path.cwd(); dest=root/'saigo';dest.mkdir(exist_ok=True)
m=json.loads((root/'saigo-manifest.json').read_text())
for a in m['package_targets']['linux_x86']['archives']:
 if not ('_arm' in a['name'] or a['name'].startswith(('llvm_saigo','binutils_x86_64_linux'))):continue
 p=root/a['name']; print('Downloading',a['name'],flush=True)
 urllib.request.urlretrieve(a['url'],p)
 assert hashlib.sha1(p.read_bytes()).hexdigest()==a['hash'],a['name']
 with tarfile.open(p) as t:t.extractall(dest,filter='data')
 print('Verified/extracted',a['name'],flush=True)
print('SAIGO_READY',flush=True)
