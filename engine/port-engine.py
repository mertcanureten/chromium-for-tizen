"""NaCl target identity and missing POSIX platform hooks for V8 experiment."""
from pathlib import Path
root=Path('/work/v8')
def replace(path,old,new):
 p=root/path;s=p.read_text()
 if new in s:return
 assert old in s,path
 p.write_text(s.replace(old,new))
replace('include/v8config.h','#elif defined(__linux__)','#elif defined(__native_client__)\n# define V8_OS_NACL 1\n# define V8_OS_POSIX 1\n# define V8_OS_STRING "nacl"\n\n#elif defined(__linux__)')
replace('include/v8config.h','&& !defined(V8_TARGET_OS_CHROMEOS)','&& !defined(V8_TARGET_OS_NACL) \\\n  && !defined(V8_TARGET_OS_CHROMEOS)')
replace('include/v8config.h','|| defined(V8_TARGET_OS_CHROMEOS)','|| defined(V8_TARGET_OS_NACL) \\\n  || defined(V8_TARGET_OS_CHROMEOS)')
replace('include/v8config.h','// Fall back to the detected host OS.','// Fall back to the detected host OS.\n#ifdef V8_OS_NACL\n# define V8_TARGET_OS_NACL\n#endif')
replace('include/v8config.h','#elif defined(V8_TARGET_OS_LINUX)','#elif defined(V8_TARGET_OS_NACL)\n# define V8_TARGET_OS_STRING "nacl"\n#elif defined(V8_TARGET_OS_LINUX)')
replace('BUILD.gn','  "V8_TARGET_OS_LINUX",','  "V8_TARGET_OS_LINUX",\n  "V8_TARGET_OS_NACL",')
replace('BUILD.gn','if (target_os == "android") {\n  enabled_external_v8_defines','if (target_os == "nacl") {\n  enabled_external_v8_defines += [ "V8_HAVE_TARGET_OS", "V8_TARGET_OS_NACL" ]\n} else if (target_os == "android") {\n  enabled_external_v8_defines')
replace('BUILD.gn','  if (is_linux || is_chromeos) {\n    sources += [\n      "src/base/debug/stack_trace_posix.cc",','  if (current_os == "nacl") {\n    sources += [ "tvos/platform-nacl.cc" ]\n  } else if (is_linux || is_chromeos) {\n    sources += [\n      "src/base/debug/stack_trace_posix.cc",')
(root/'tvos/platform-nacl.cc').write_text('''// Experimental TV Native Client hooks. Unsupported facilities fail explicitly.
#include <cstdio>
#include <ostream>
#include "src/base/debug/stack_trace.h"
#include "src/base/platform/platform.h"
#include "src/base/platform/platform-posix-time.h"
namespace v8::base {
TimezoneCache* OS::CreateTimezoneCache() { return new PosixDefaultTimezoneCache(); }
void OS::SignalCodeMovingGC() {} // No host profiler mmap channel in NaCl.
void OS::AdjustSchedulingParams() {} // Scheduling belongs to the TV runtime.
std::vector<OS::SharedLibraryAddress> OS::GetSharedLibraryAddresses() { return {}; }
void* OS::RemapShared(void*, void*, size_t) { return nullptr; }
std::optional<OS::MemoryRange> OS::GetFirstFreeMemoryRangeWithin(Address, Address, size_t, size_t) { return std::nullopt; }
bool OS::RemapPages(const void*, size_t, void*, MemoryPermission) { return false; }
namespace debug {
bool EnableInProcessStackDumping() { return false; }
void DisableSignalStackDump() {}
StackTrace::StackTrace() = default;
void StackTrace::Print() const { fputs("Native stack trace unavailable in NaCl", stderr); }
void StackTrace::OutputToStream(std::ostream* os) const { *os << "Native stack trace unavailable in NaCl"; }
}
}
''')
