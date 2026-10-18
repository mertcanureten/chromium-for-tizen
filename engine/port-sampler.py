"""Disable unsupported asynchronous CPU stack sampling on Native Client.

NaCl has no POSIX signal context / pthread_kill interface. JavaScript execution
is unaffected; CPU profiling deliberately produces no asynchronous samples.
"""
from pathlib import Path
root=Path('/work/v8/src/libsampler')
p=root/'sampler.h';s=p.read_text()
a='#if V8_OS_POSIX && !V8_OS_CYGWIN && !V8_OS_FUCHSIA'
b=a+' && !V8_OS_NACL'
if b not in s:
 assert s.count(a)==1
 s=s.replace(a,b);p.write_text(s)
p=root/'sampler.cc';s=p.read_text()
if '// NaCl does not expose asynchronous thread register sampling.' not in s:
 a='#endif  // USE_SIGNALS\n\n#if defined(USE_SIGNALS)\nclass SignalHandler'
 b='''#elif V8_OS_NACL
// NaCl does not expose asynchronous thread register sampling.
class Sampler::PlatformData {};
#endif  // USE_SIGNALS

#if defined(USE_SIGNALS)
class SignalHandler'''
 assert s.count(a)==1;s=s.replace(a,b)
 a='\n#endif  // USE_SIGNALS\n\n}  // namespace sampler'
 b='''
#elif V8_OS_NACL
void Sampler::DoSample() {
  // Unsupported: do not invent register states or count synthetic samples.
}
#endif  // USE_SIGNALS

}  // namespace sampler'''
 assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
