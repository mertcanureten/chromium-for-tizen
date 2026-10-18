"""Handle NaCl's pointer pthread_t without truncation on the ARM32 target."""
from pathlib import Path
p=Path('/work/v8/third_party/abseil-cpp/absl/base/internal/sysinfo.cc')
s=p.read_text()
if 'static_assert(sizeof(pthread_t)' not in s:
 s=s.replace('  return static_cast<pid_t>(pthread_self());', '''#if defined(__native_client__)
  static_assert(sizeof(pthread_t) == sizeof(pid_t));
  return static_cast<pid_t>(reinterpret_cast<uintptr_t>(pthread_self()));
#else
  return static_cast<pid_t>(pthread_self());
#endif''')
p.write_text(s)
p=Path('/work/v8/third_party/abseil-cpp/absl/debugging/failure_signal_handler.cc')
s=p.read_text().replace('#if !defined(_WIN32) && !defined(__wasi__)', '#if !defined(_WIN32) && !defined(__wasi__) && !defined(__native_client__)')
p.write_text(s)
p=Path('/work/v8/third_party/abseil-cpp/absl/debugging/internal/elf_mem_image.h')
s=p.read_text().replace('    !defined(__XTENSA__)\n','    !defined(__XTENSA__) && !defined(__native_client__)\n')
p.write_text(s)
