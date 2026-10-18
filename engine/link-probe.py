"""Link the developer probe using the engine's exact generated defines."""
from pathlib import Path
import subprocess, json, hashlib, sys, shutil
root=Path('/work');v8=root/'v8';out=root/'out';out.mkdir(exist_ok=True)
data=json.loads(subprocess.check_output(['/work/gn/gn','desc','out/tvos','//:v8_libplatform','defines','--format=json'],cwd=v8))
defines=data['//:v8_libplatform']['defines']
cc=str(root/'saigo/bin/arm-nacl-clang++')
cmd=[cc,'--target=arm-nacl','-std=gnu++20','-O2','-fno-rtti','-fno-exceptions','-pthread','-ffunction-sections','-fdata-sections']
cmd += ['-D'+d for d in defines]
cmd += ['-I/work/include','-I/work/v8/include','-I/work/v8','-I/work/v8/out/tvos/gen','/work/probe.cc','/work/runtime-support.cc','/work/v8/out/tvos/obj/libv8_monolith.a','-L/work','-lppapi','-Wl,--gc-sections','-Wl,-T,/work/nacl-flags.ld','-o','/work/out/probe_arm.nexe']
(out/'link-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
if '--compile-only' in sys.argv:
 prefix=cmd[:cmd.index('/work/probe.cc')]
 for source in ['probe','runtime-support']:
  subprocess.run(prefix+['/work/'+source+'.cc','-c','-o','/work/out/'+source+'.o'],check=True)
 raise SystemExit(0)
subprocess.run(cmd,check=True)
p=out/'probe_arm.nexe';(out/'SHA256SUMS').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  probe_arm.nexe\n')

# Preserve notices with the private test artifact.
licenses=out/'licenses';licenses.mkdir(exist_ok=True)
for base in [v8]+[v8/d for d in json.loads((root/'deps.json').read_text())]:
 for name in ['LICENSE','LICENSE.txt','LICENSE.md','COPYING','NOTICE']:
  src=base/name
  if src.is_file():
   dest=licenses/str(base.relative_to(v8)).replace('/','_')/name
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
