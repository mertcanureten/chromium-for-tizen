"""Give flag freezing dedicated 64 KiB pages without changing FlagValues ABI."""
from pathlib import Path
p=Path('/work/v8/src/flags/flags.cc');s=p.read_text()
old='FlagValues v8_flags PERMISSION_MUTABLE_SECTION;'
new='''#if defined(__native_client__)
// The linker reserves whole NaCl pages; no neighboring mutable data is frozen.
FlagValues v8_flags __attribute__((section(".data.nacl_v8_flags"), aligned(65536)));
extern "C" char __nacl_v8_flags_start[], __nacl_v8_flags_end[];
#else
FlagValues v8_flags PERMISSION_MUTABLE_SECTION;
#endif'''
if new not in s:
 assert old in s;s=s.replace(old,new,1)
old='  base::OS::SetDataReadOnly(&v8_flags, sizeof(v8_flags));'
new='''#if defined(__native_client__)
  base::OS::SetDataReadOnly(__nacl_v8_flags_start,
      static_cast<size_t>(__nacl_v8_flags_end - __nacl_v8_flags_start));
#else
  base::OS::SetDataReadOnly(&v8_flags, sizeof(v8_flags));
#endif'''
if new not in s:
 assert old in s;s=s.replace(old,new,1)
p.write_text(s)
