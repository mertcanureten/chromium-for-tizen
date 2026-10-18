"""Match the ARM-on-ARM simulator FP marshaling to the NaCl ARM ABI.

GN sets USE_EABI_HARDFLOAT only for non-ARM host CPUs. The on-device ARM
simulator therefore defaulted to soft-float, unlike the snapshot generator
and ARM assembler. Consult the same OS ABI helper used by the assembler.
"""
from pathlib import Path
p=Path('/work/v8/src/execution/arm/simulator-arm.cc');s=p.read_text()
old='  if (use_eabi_hardfloat()) {'
new='''#if defined(__native_client__)
  if (base::OS::ArmUsingHardFloat()) {
#else
  if (use_eabi_hardfloat()) {
#endif'''
if new not in s:
 assert s.count(old)==3
 p.write_text(s.replace(old,new))
