"""Stage source scripts and required PPAPI headers from a user-supplied SDK."""
from pathlib import Path
import argparse,re,shutil
p=argparse.ArgumentParser()
p.add_argument('--include',type=Path,required=True)
p.add_argument('--arm-lib',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parent;a.work.mkdir(parents=True,exist_ok=True)
queue=re.findall(r'#include "(ppapi/[^\"]+)"',(root/'engine/probe.cc').read_text());seen=set()
while queue:
 name=queue.pop()
 if name in seen:continue
 seen.add(name);source=a.include/name;dest=a.work/'include'/name
 if not source.is_file():raise FileNotFoundError(source)
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 queue.extend(re.findall(r'#include "(ppapi/[^\"]+)"',source.read_text()))
for name in ['libppapi.a','libppapi_stub.a']:shutil.copy2(a.arm_lib/name,a.work/name)
for directory in ['engine','toolchain']:
 for source in (root/directory).iterdir():
  if source.is_file():shutil.copy2(source,a.work/source.name)
print('Staged build workspace. Preserve SDK notices and use your own signing profile.')
