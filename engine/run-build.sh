#!/bin/sh
set -eu
cd /work
python3 configure-server.py
python3 port-engine.py
python3 port-math.py
python3 port-sync.py
python3 port-system.py
python3 port-time.py
python3 port-abseil.py
python3 port-snapshot.py
python3 port-host.py
python3 port-sampler.py
python3 port-testing.py
python3 port-arm-cache.py
python3 port-nacl-instructions.py
python3 port-flags-pages.py
python3 port-segment-pages.py
python3 port-regexp-dispatch.py
python3 port-simulator-float.py
cd v8
/work/gn/gn gen out/tvos
ninja -C out/tvos -j3 v8_libbase
ninja -C out/tvos -j3 v8_monolith
