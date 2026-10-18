/* Isolate immutable V8 flags on whole 64 KiB Native Client pages. */
SECTIONS {
  .nacl_v8_flags ALIGN(0x10000) : {
    __nacl_v8_flags_start = .;
    KEEP(*(.data.nacl_v8_flags))
    . = ALIGN(0x10000);
    __nacl_v8_flags_end = .;
  }
}
INSERT BEFORE .data;
