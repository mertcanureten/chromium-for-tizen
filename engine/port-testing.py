"""Only include sandbox-testing sanitizer APIs when that code is enabled.

Trap-mode UBSan does not ship sanitizer callback headers in the NaCl SDK.
All users of these interfaces in this translation unit are inside the existing
V8_ENABLE_SANDBOX guard. Keep compiler instrumentation unchanged.
"""
from pathlib import Path
p=Path('/work/v8/src/sandbox/testing.cc');s=p.read_text()
marker='// Sanitizer callbacks below are used only by sandbox testing.'
if marker not in s:
 start=s.index('#if defined(V8_USE_ADDRESS_SANITIZER)\n#include <sanitizer/asan_interface.h>')
 end=s.index('\n#if defined(V8_ENABLE_SANDBOX) && defined(V8_ENABLE_MEMORY_CORRUPTION_API)',start)
 s=s[:start]+marker+'\n#ifdef V8_ENABLE_SANDBOX\n'+s[start:end]+'#endif  // V8_ENABLE_SANDBOX\n'+s[end:]
 p.write_text(s)
