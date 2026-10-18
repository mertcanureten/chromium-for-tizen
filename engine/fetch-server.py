import pathlib,subprocess,urllib.request,tarfile,json,zipfile,os
root=pathlib.Path.cwd()
rev='94bfc15fbee9b05276068d92bf585ab961c80fd1'
if not (root/'v8').exists():
 urllib.request.urlretrieve(f'https://codeload.github.com/v8/v8/tar.gz/{rev}',root/'v8-source.tar.gz')
 with tarfile.open(root/'v8-source.tar.gz') as t:t.extractall(root,filter='data')
 (root/('v8-'+rev)).rename(root/'v8')
for name,dep in json.loads((root/'deps.json').read_text()).items():
 p=root/'v8'/name
 if (p/'.git').exists():
  current=subprocess.run(['git','-C',str(p),'rev-parse','HEAD'],capture_output=True,text=True)
  if current.returncode==0 and current.stdout.strip()==dep['revision']:continue
 p.mkdir(parents=True,exist_ok=True)
 subprocess.run(['git','init','-q',str(p)],check=True)
 subprocess.run(['git','-C',str(p),'fetch','--depth=1',dep['url'],dep['revision']],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['git','-C',str(p),'checkout','-q','FETCH_HEAD'],check=True)
 print('FETCHED',name,flush=True)
url='https://chrome-infra-packages.appspot.com/dl/gn/gn/linux-amd64/+/git_revision:ca14a831a82342fe28e372a8d25ee4fe31b920e4'
if not (root/'gn/gn').exists():
 urllib.request.urlretrieve(url,root/'gn.zip')
 with zipfile.ZipFile(root/'gn.zip') as z:z.extractall(root/'gn')
 (root/'gn/gn').chmod(0o755)
print('SOURCES_READY',flush=True)
