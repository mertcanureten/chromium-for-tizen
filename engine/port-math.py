"""Use Saigo's shipped libm on NaCl; LLVM shared math needs unavailable fenv API.
This changes transcendental rounding and needs conformance testing before release.
"""
from pathlib import Path
p=Path('/work/v8/src/base/ieee754.cc');s=p.read_text()
if 'TVOS_V8_MATH' not in s:
 s=s.replace('#include "third_party/llvm-libc/src/shared/math.h"','''#if defined(V8_OS_NACL)
#define TVOS_V8_MATH std
#else
#include "third_party/llvm-libc/src/shared/math.h"
#define TVOS_V8_MATH LIBC_NAMESPACE::shared
#endif''')
 s=s.replace('return LIBC_NAMESPACE::shared::','return TVOS_V8_MATH::')
 p.write_text(s)
