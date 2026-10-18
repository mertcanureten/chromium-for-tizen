// Missing NaCl embedding runtime facilities; no disabled stack checks.
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <nacl/nacl_random.h>
#include "src/base/platform/platform.h"

// Saigo's libc++ headers declare these extern templates, but its archive does
// not supply the char specializations. Instantiate the actual implementations.
template class std::basic_filebuf<char>;
template class std::basic_ifstream<char>;
template class std::basic_ofstream<char>;

extern "C" {
uintptr_t __stack_chk_guard = 0;
__attribute__((noreturn)) void __stack_chk_fail() { std::abort(); }
// Runs before ordinary C++ constructors. Fail closed if entropy is unavailable.
__attribute__((constructor(101), no_stack_protector))
static void initialize_stack_guard() {
  size_t written = 0;
  if (nacl_secure_random(&__stack_chk_guard, sizeof(__stack_chk_guard), &written)
      != 0 || written != sizeof(__stack_chk_guard) || __stack_chk_guard == 0) {
    std::abort();
  }
}
}
namespace v8::base {
bool OS::ArmUsingHardFloat() {
#if defined(__ARM_PCS_VFP)
  return true;
#elif defined(__ARM_PCS) || defined(__SOFTFP__)
  return false;
#else
#error "Unknown ARM floating point calling convention"
#endif
}
}
