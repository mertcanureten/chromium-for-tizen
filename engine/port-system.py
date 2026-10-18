"""Report unavailable NaCl resource information without inventing TV hardware."""
from pathlib import Path
root=Path('/work/v8')
p=root/'src/base/sys-info.cc';s=p.read_text()
s=s.replace('int64_t SysInfo::AmountOfPhysicalMemory() {\n#if V8_OS_DARWIN','int64_t SysInfo::AmountOfPhysicalMemory() {\n#if defined(V8_OS_NACL)\n  return 0;  // Unknown; embedder must supply explicit heap limits.\n#elif V8_OS_DARWIN')
s=s.replace('#if V8_OS_WIN || V8_OS_FUCHSIA','#if V8_OS_WIN || V8_OS_FUCHSIA || defined(V8_OS_NACL)')
p.write_text(s)
