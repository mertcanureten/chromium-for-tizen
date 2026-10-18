#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${TIZEN_CLI:?Set TIZEN_CLI to your tizen executable}"
: "${TIZEN_SECURITY_PROFILE:?Set your own Samsung signing profile}"
stage="$PWD/stage"
artifact="$PWD/artifact"
mkdir -p "$stage" "$PWD/dist"
(cd "$artifact" && shasum -a 256 -c SHA256SUMS)
cp engine/index.html engine/config.xml "$stage/"
cp "$artifact/probe_arm.nexe" "$stage/"
cp -R "$artifact/licenses" "$stage/"
printf '%s\n' '{"program":{"arm":{"url":"probe_arm.nexe"}}}' > "$stage/probe.nmf"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:--Xmx256m}"
"$TIZEN_CLI" build-web -- "$stage"
"$TIZEN_CLI" package -t wgt -s "$TIZEN_SECURITY_PROFILE" -o "$PWD/dist" -- "$stage/.buildResult"
