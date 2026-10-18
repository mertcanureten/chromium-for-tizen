# Chromium for Tizen

Experimental work toward an on-device Chromium engine for older Samsung Tizen TVs.
**The working milestone is V8 JavaScript execution, not a complete Chromium browser.**

V8 **15.8.18** runs inside an ARM Native Client module on a **Samsung UE49MU7400,
Tizen 3.0**. The final signed developer package passed 14 individual feature tests
and 5 combined execution/recovery tests on the physical television on
2026-10-18 UTC (2026-10-19 local time). See [test evidence](evidence/).

This repository is independent of any TV launcher or phone remote application.
It contains source adapters, build scripts and a controlled developer probe.
No signing keys, Samsung SDK libraries, private deployment configuration or
signed device package are distributed here. This is an independent experiment,
not an official Samsung, Google, Chromium or Apple product.

## What runs on the TV

Saigo Clang 21 compiles V8's C++ runtime into ARM Native Client code. V8's ARM
simulator interprets generated ARM builtins **on the TV**, because those raw
builtins do not satisfy Native Client's native-code validation rules. JavaScript
runs in jitless/lite mode. A server was used only to build the binaries; it does
not execute pages, JavaScript or user sessions at runtime.

Verified features include BigInt, optional chaining, Unicode, arrays, closures,
regular expressions, JSON, typed arrays, floating-point math, UTC dates, Map and
Set. Tests also cover syntax/runtime exceptions, recovery, 10,000 object
allocations, and fresh-isolate separation. The tests are smoke tests, not Test262
conformance, a performance benchmark or a security audit. Inspector round-trip
times include a one-second polling interval and must not be read as execution
latency.

## Status and limits

- No Blink, DOM, CSS layout, browser networking, compositor or browser UI yet.
- WebAssembly, ICU/Intl, Temporal, JIT and asynchronous CPU profiling are disabled
  or unavailable in this experimental configuration.
- The NaCl outer sandbox and validator remain enabled. V8's separate 64-bit
  sandbox and pointer compression are not enabled on this 32-bit target.
- Math uses the SDK libm; selected values were verified, full rounding and edge
  case conformance still needs work.
- The probe accepts controlled developer scripts only. It does not provide a
  deadline for arbitrary JavaScript and is not a production browser API.
- Device support is established only for the tested TV. Newer Tizen models may
  not expose the same legacy Native Client development capabilities.
- The published scripts capture the successful source adaptations. The verified
  artifact was produced through incremental rebuilds; a new clean build from
  this standalone repository has not yet been verified.

## Build

Use an x86-64 Linux builder with Python 3.12, build-essential, ninja-build, git,
curl, ca-certificates, pkg-config and g++-multilib. A workspace mounted at `/work`
is currently required. Keep enough disk for sources and build outputs (100 GB
or more is recommended). The verified builder was capped at 4 CPUs and 7 GiB RAM;
`run-build.sh` defaults to three jobs. Do not place this build on an unrestricted
production host.

1. Obtain the Samsung TV Native Client SDK using your own authorized installation.
   Supply its `include` directory and the ARM library directory containing
   `libppapi.a` and `libppapi_stub.a` to the staging helper:

   ```sh
   python3 prepare-builder.py --include /path/to/sdk/include \
     --arm-lib /path/to/sdk/arm-nacl/lib --work /path/to/build-workspace
   ```

2. Mount that staged workspace as `/work` in the Linux builder. Then run:

   ```sh
   cd /work
   python3 setup-server.py
   python3 fetch-server.py
   sh run-build.sh
   python3 link-probe.py
   ```

   Sources and the Saigo manifest are pinned. The bootstrap validates the
   vendor-published archive hashes. The build preserves sources and artifacts.
   The output is `/work/out/probe_arm.nexe` with `SHA256SUMS` and dependency notices.
   `nacl-flags.ld` is required when linking; it isolates immutable V8 flag storage
   on complete 64 KiB pages.

3. Copy the contents of `/work/out` into `artifact/` on your Tizen development
   machine. Configure your own Samsung signing profile, then package:

   ```sh
   export TIZEN_CLI=/path/to/tizen/tools/ide/bin/tizen
   export TIZEN_SECURITY_PROFILE=YourProfile
   sh engine/package.sh
   "$TIZEN_CLI" install -n V8Probe.wgt -- "$PWD/dist"
   ```

   `engine/config.xml` uses the test application ID `Cpp20TVXXX.Main` for parity
   with the device-tested probe. It is not intended to replace a browser app.

4. Launch that test app in developer debug mode and forward its reported port:

   ```sh
   sdb shell 0 debug Cpp20TVXXX.Main 0
   sdb forward tcp:PORT tcp:PORT
   npm install
   TV_DEBUG_PORT=PORT node engine/verify-tv.mjs report.json
   ```

   `engine/verify-features.mjs` provides finer-grained diagnosis. The browser shell
   uses ES5-compatible code; modern syntax is passed as text to the native V8
   module, so the old TV web engine does not execute the tested JavaScript.

## Porting changes

The `engine/port-*.py` adapters are guarded, repeatable source transformations
against pinned revisions. They cover NaCl platform identification, unavailable
POSIX interfaces, host snapshot generation, safe builtin storage, and:

- NaCl-approved fatal traps and stack scanning without reserved register r9.
- Dedicated, read-protected 64 KiB flag storage, preserving the FlagValues ABI.
- Separate 64 KiB mappings backing logical 16 KiB dispatch-table segments, with
  matching deallocation sizes.
- Portable switch dispatch for the RegExp interpreter, avoiding a real-device
  hang observed with computed-label dispatch.
- ARM-on-ARM simulator floating-point marshaling matching the hard-float ABI.
- A secure random stack canary, SDK fstream template instantiations, and an ARM
  ABI hook in `runtime-support.cc`.

## Next milestones

1. Verify a clean independent rebuild and widen JavaScript conformance coverage.
2. Measure startup, memory use and sustained execution on the physical TV.
3. Design a bounded execution/termination API for the application.
4. Investigate Blink, networking, rendering/compositing, input and media integration.

A working V8 component does not establish that full Chromium can be packaged or
run acceptably on this television. Those integrations remain research work.

## Attribution

V8, Chromium and Native Client remain subject to their upstream licenses.
See [NOTICE](NOTICE). This repository does not redistribute the Samsung SDK.
