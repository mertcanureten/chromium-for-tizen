"""Back each logical 16 KiB segment with a separate 64 KiB NaCl mapping.

Keep segment indexing and snapshot ABI unchanged. The remaining bytes are
unused padding; the entire mapping is freed with the matching physical size.
Only the non-contiguous 32-bit NaCl path uses this extra backing memory.
"""
from pathlib import Path
p=Path('/work/v8/src/sandbox/segmented-table.cc');s=p.read_text()
for old,new in [
('  vas_->FreePages(segment_start, kSegmentSize);','''#if defined(__native_client__)
  static_assert(!kUseContiguousMemory);
  vas_->FreePages(segment_start,
      RoundUp(kSegmentSize, vas_->allocation_granularity()));
#else
  vas_->FreePages(segment_start, kSegmentSize);
#endif'''),
('''  const Address start =
      vas_->AllocatePages(VirtualAddressSpace::kNoHint, kSegmentSize,
                          kSegmentSize, PagePermissions::kReadWrite);''','''#if defined(__native_client__)
  static_assert(!kUseContiguousMemory);
  const size_t mapping_size =
      RoundUp(kSegmentSize, vas_->allocation_granularity());
  const Address start = vas_->AllocatePages(VirtualAddressSpace::kNoHint,
      mapping_size, mapping_size, PagePermissions::kReadWrite);
#else
  const Address start =
      vas_->AllocatePages(VirtualAddressSpace::kNoHint, kSegmentSize,
                          kSegmentSize, PagePermissions::kReadWrite);
#endif''')]:
 if new not in s:
  assert old in s;s=s.replace(old,new,1)
p.write_text(s)
