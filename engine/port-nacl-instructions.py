"""Keep fatal paths and conservative stack scanning within ARM NaCl SFI rules.

The official ARM validator identified the only six invalid instructions in the
linked probe: two bkpt/udf pairs, DebugBreak's bkpt, and saving reserved r9.
Do not disable validation; use the compiler's NaCl fatal trap and avoid r9.
"""
from pathlib import Path
root = Path('/work/v8')
for name, old, new in [
 ('src/execution/isolate.cc',
  '  if (recursive.exchange(true)) IMMEDIATE_CRASH();',
  '''  if (recursive.exchange(true)) {
#if defined(__native_client__)
    __builtin_trap();  // Saigo emits the NaCl-approved fatal UDF encoding.
#else
    IMMEDIATE_CRASH();
#endif
  }'''),
 ('src/base/platform/platform-posix.cc',
  '    case AbortMode::kImmediateCrash:\n      IMMEDIATE_CRASH();',
  '''    case AbortMode::kImmediateCrash:
#if defined(__native_client__)
      __builtin_trap();
#else
      IMMEDIATE_CRASH();
#endif'''),
 ('src/base/platform/platform-posix.cc',
  'void OS::DebugBreak() {\n#if V8_HOST_ARCH_ARM',
  '''void OS::DebugBreak() {
#if defined(__native_client__)
  __builtin_trap();  // Debug break is fatal in the NaCl sandbox.
#elif V8_HOST_ARCH_ARM'''),
 ('src/heap/base/asm/arm/push_registers_asm.cc',
  '    "  push {r3-r11, lr}                                \\n"',
  '''#if defined(__native_client__)
    // r9 is the reserved NaCl thread pointer, never a managed heap root.
    // Save r12 in its place to retain 40-byte size and 8-byte alignment.
    "  push {r3-r8, r10-r12, lr}                         \\n"
#else
    "  push {r3-r11, lr}                                \\n"
#endif''')]:
 p=root/name;s=p.read_text()
 if new not in s:
  assert old in s,name
  p.write_text(s.replace(old,new,1))
