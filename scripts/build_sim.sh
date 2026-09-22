#!/usr/bin/env bash
# ブラウザで動く仮想 UNO R4 WiFi（docs/sim）を組み立てる
#
#   scripts/build_sim.sh [出力先]          # 既定は _site/sim
#
# - 章の一覧は docs/sim/sim.js の CHAPTERS から取る（ここに二重に書かない）
# - 各章は `pio run -e sim` でビルドする（実機向けとの差は -D NO_USB だけ）。
#   PlatformIO は code/ の uv 環境のもの（simulator.yml と同じ）
# - QEMU の WebAssembly 版は qemu-arduino-uno-r4 のリリースから取る。
#   手元でビルドしたものを使うときは QEMU_WASM_DIR に
#   qemu-system-arm.{js,wasm} のあるディレクトリを渡す
set -euo pipefail
cd "$(dirname "$0")/.."

out=${1:-_site/sim}
# 付録・simulator.yml と同じリリースを使う。上げるときは一緒に直す
QEMU_UNOR4_VERSION=${QEMU_UNOR4_VERSION:-v11.1.1-unor4.5}

chapters=$(sed -n "s/^ *{ dir: '\([^']*\)'.*/\1/p" docs/sim/sim.js)
[ -n "$chapters" ] || { echo "error: docs/sim/sim.js から章の一覧を読めません" >&2; exit 1; }

rm -rf "$out"
mkdir -p "$out/chapters" "$out/qemu"
cp docs/sim/index.html docs/sim/sim.js docs/sim/coi-serviceworker.js "$out/"
cp code/sim/board_off.jpg code/sim/matrix_cells.json "$out/"

if [ -n "${QEMU_WASM_DIR:-}" ]; then
  cp "$QEMU_WASM_DIR/qemu-system-arm.js" "$QEMU_WASM_DIR/qemu-system-arm.wasm" "$out/qemu/"
else
  base="https://github.com/iory/qemu-arduino-uno-r4/releases/download/$QEMU_UNOR4_VERSION"
  name="qemu-arduino-uno-r4-$QEMU_UNOR4_VERSION-wasm"
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  (cd "$tmp" && curl -fsSL -O "$base/SHA256SUMS" -O "$base/$name.tar.gz" &&
     shasum -a 256 -c --ignore-missing SHA256SUMS >/dev/null)
  tar xzf "$tmp/$name.tar.gz" -C "$tmp"
  cp "$tmp/$name/qemu-system-arm.js" "$tmp/$name/qemu-system-arm.wasm" \
     "$tmp/$name/LICENSE" "$out/qemu/"
fi

for ch in $chapters; do
  uv run --frozen --project code pio run -d "code/$ch" -e sim >/dev/null
  cp "code/$ch/.pio/build/sim/firmware.elf" "$out/chapters/$ch.elf"
done
echo "built into $out/ ($(echo "$chapters" | wc -l | tr -d ' ') chapters)"
