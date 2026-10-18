"""Use newlib timezone globals instead of nonportable struct tm extensions."""
from pathlib import Path
p=Path('/work/v8/src/base/platform/platform-posix-time.cc')
s=p.read_text()
if "newlib records seconds west" in s: raise SystemExit(0)
s=s.replace('  if (!t || !t->tm_zone) return "";\n  return t->tm_zone;', '''#if defined(V8_OS_NACL)
  if (!t) return "";
  const char* name = _tzname[t->tm_isdst > 0 ? 1 : 0];
  return name ? name : "";
#else
  if (!t || !t->tm_zone) return "";
  return t->tm_zone;
#endif''')
s=s.replace('  return static_cast<double>(t->tm_gmtoff', '''#if defined(V8_OS_NACL)
  // newlib records seconds west of UTC, excluding daylight saving.
  return -static_cast<double>(_timezone) * msPerSecond;
#else
  return static_cast<double>(t->tm_gmtoff''')
s=s.replace('(t->tm_isdst > 0 ? 3600 * msPerSecond : 0));','(t->tm_isdst > 0 ? 3600 * msPerSecond : 0));\n#endif')
p.write_text(s)
