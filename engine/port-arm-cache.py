"""Match ARM cache-flush includes to the existing non-simulator code guard."""
from pathlib import Path
p=Path('/work/v8/src/codegen/arm/cpu-arm.cc');s=p.read_text()
a='#ifdef __arm__\n';b='#if defined(__arm__) && !defined(USE_SIMULATOR)\n'
if b not in s:
 assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
