"""Store simulator bytecode as data, never as native NaCl executable text."""
from pathlib import Path
p=Path('/work/v8/src/snapshot/embedded/platform-embedded-file-writer-generic.cc')
s=p.read_text()
old='''void PlatformEmbeddedFileWriterGeneric::SectionText() {
  if (target_os_ == EmbeddedTargetOs::kChromeOS) {'''
new='''void PlatformEmbeddedFileWriterGeneric::SectionText() {
#if defined(V8_TARGET_OS_NACL)
  // These ARM instructions are interpreted by the V8 simulator on the TV.
  // Raw builtin bytes are not NaCl SFI native code and must not be executable.
  fprintf(fp_, ".section .rodata.v8_simulator_builtins,\\\"a\\\",%%progbits\\n");
#else
  if (target_os_ == EmbeddedTargetOs::kChromeOS) {'''
if new not in s:
 assert old in s
 s=s.replace(old,new)
 end='''}

void PlatformEmbeddedFileWriterGeneric::SectionRoData()'''
 assert end in s;s=s.replace(end,'''#endif
}

void PlatformEmbeddedFileWriterGeneric::SectionRoData()''',1)
 p.write_text(s)
