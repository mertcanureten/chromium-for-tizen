"""Make standard library dependencies explicit for the Linux libstdc++ host."""
from pathlib import Path
p=Path('/work/v8/include/cppgc/allocation.h');s=p.read_text()
if '#include <limits>' not in s:
 s=s.replace('#include <cstddef>', '#include <cstddef>\n#include <limits>')
 assert '#include <limits>' in s
 p.write_text(s)
p=Path('/work/v8/build/config/compiler/BUILD.gn');s=p.read_text()
s=s.replace('(is_linux && !is_clang)', '(is_linux && (!is_clang || !use_lld))')
p.write_text(s)
