"""Experimental full V8 on ARM NaCl. Run inside the disposable /work builder."""
from pathlib import Path
import subprocess
root=Path('/work/v8')
def replace(path,old,new):
 p=root/path;s=p.read_text()
 if new in s:return
 assert old in s,(path,old)
 p.write_text(s.replace(old,new))
replace('build/config/BUILDCONFIG.gn','} else if (target_os == "emscripten") {','} else if (target_os == "nacl") {\n  _default_toolchain = "//tvos:nacl_arm"\n} else if (target_os == "emscripten") {')
replace('build/config/clang/BUILD.gn','if (!defined(invoker.libname) || is_wasm) {','if (!defined(invoker.libname) || is_wasm || target_os == "nacl") {')
(root/'build/config/gclient_args.gni').write_text('checkout_src_internal = false\nandroid_ndk_version = "2@30.0.16248370"\n')
py=root/'third_party/cpython3/host/bin/python3';py.parent.mkdir(parents=True,exist_ok=True)
if not py.exists(): py.symlink_to('/usr/bin/python3')
(root/'tvos').mkdir(exist_ok=True)
(root/'tvos/BUILD.gn').write_text('''import("//build/toolchain/gcc_toolchain.gni")
gcc_toolchain("nacl_arm") {
 cc = "/work/saigo/bin/arm-nacl-clang"
 cxx = "/work/saigo/bin/arm-nacl-clang++"
 ar = "/work/saigo/bin/arm-nacl-ar"
 ld = cxx
 extra_cppflags = "--target=arm-nacl -DV8_OS_NACL=1 -DV8_OS_POSIX=1 -marm"
 extra_cxxflags = "-std=gnu++20"
 toolchain_args = {
  current_cpu = "arm"
  current_os = "nacl"
  v8_current_cpu = "arm"
  is_clang = true
 }
}
gcc_toolchain("host_x86") {
 cc = "/work/saigo/bin/clang"
 cxx = "/work/saigo/bin/clang++"
 ar = "ar"
 ld = cxx
 extra_cppflags = "--target=i686-linux-gnu"
 extra_ldflags = "--target=i686-linux-gnu"
 toolchain_args = {
  current_cpu = "x86"
  current_os = "linux"
  v8_current_cpu = "arm"
  is_clang = true
 }
}
''')
out=root/'out/tvos';out.mkdir(parents=True,exist_ok=True)
(out/'args.gn').write_text('''target_os = "nacl"
target_cpu = "arm"
v8_target_cpu = "arm"
custom_toolchain = "//tvos:nacl_arm"
host_toolchain = "//tvos:host_x86"
v8_snapshot_toolchain = "//tvos:host_x86"
is_debug = false
symbol_level = 0
is_component_build = false
v8_monolithic = true
v8_use_external_startup_data = false
v8_enable_i18n_support = false
v8_enable_webassembly = false
v8_enable_sandbox = false
v8_enable_pointer_compression = false
v8_enable_temporal_support = false
v8_enable_lite_mode = true
v8_target_is_simulator = true
v8_use_metagen = false
use_custom_libcxx = false
use_custom_libcxx_for_host = false
use_sysroot = false
treat_warnings_as_errors = false
clang_base_path = "/work/saigo"
clang_use_chrome_plugins = false
use_lld = false
use_remoteexec = false
enable_rust = false
v8_use_zlib = false
v8_enable_snapshot_compression = false
v8_enable_fuzztest = false
v8_enable_test_features = false
use_glib = false
use_siso = false
''')
# Use the experimentally tested POSIX adapter, unchanged.
if 'pthread_get_stack_end_np' not in (root/'src/base/platform/platform-posix.cc').read_text():
 script=Path('/work/port-platform.py').read_text().replace("root=Path('v8-94bfc15fbee9b05276068d92bf585ab961c80fd1')","root=Path('/work/v8')")
 Path('/work/out').mkdir(exist_ok=True)
 exec(compile(script,'port-platform.py','exec'))
# Current Chromium emits flags newer than the official NaCl Clang 21.
for p in (root/'build/config').rglob('*.gn*'):
 s=p.read_text();n=s
 for flag in ['-fdiagnostics-show-inlining-chain','-fno-lifetime-dse','-fsanitize-ignore-for-ubsan-feature=${invoker.sanitizer}','-fsanitize-ignore-for-ubsan-feature=return','-fsanitize-ignore-for-ubsan-feature=unreachable']:
  n=n.replace('"'+flag+'",','').replace('[ "'+flag+'" ]','[]')
 if n!=s:p.write_text(n)
subprocess.run(['/work/gn/gn','gen','out/tvos'],cwd=root,check=True)
