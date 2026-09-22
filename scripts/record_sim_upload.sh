#!/usr/bin/env bash
# 付録「自分でビルドした ELF をブラウザで動かす」の GIF を 2 枚録る
#
#   scripts/record_sim_upload.sh     # -> docs/{ja,en}/source/_static/sim_upload_{build,run}.gif
#
# - build: 00_intro のメッセージを書き換えて pio run する端末（本物の bash に打ち込む）
# - run:   公開中のブラウザ版でその firmware.elf をドロップして動かす画面
# 要るもの: uv, pio, agg（AGG で場所を渡せる）, gifsicle, ffmpeg。
# 端末の見た目は cast2gif.sh（既存の端末 GIF）に揃えている。
set -euo pipefail
cd "$(dirname "$0")/.."
AGG=${AGG:-agg}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
# 読者と同じ置き場所を仮の HOME に作る（本物のリポジトリは書き換えない）
home=$work/home
code=$home/learning-os-from-arduino/docs/os-on-arduino/code
mkdir -p "$code"
cp -r code/00_intro "$code/"
rm -rf "$code/00_intro/.pio"
# Ubuntu の bash が最初に出す sudo の案内を出さない（既定の HOME と同じ状態にする）
touch "$home/.sudo_as_admin_successful"
elf=$code/00_intro/.pio/build/uno_r4_wifi/firmware.elf

# 仮の HOME でも、PlatformIO は手元のパッケージを使う
export PLATFORMIO_CORE_DIR=${PLATFORMIO_CORE_DIR:-$HOME/.platformio}
export DEMO_HOME=$home
export DEMO_PATH="$(dirname "$(command -v pio)"):/usr/local/bin:/usr/bin:/bin"

echo ">> build: recording the terminal"
uv tool run --from 'asciinema<3' asciinema rec -q --overwrite --cols 82 --rows 22 \
  -c "uv run --no-project --with pexpect python3 $PWD/scripts/type_sim_upload.py" \
  "$work/build.cast" >/dev/null
[ -f "$elf" ] || { echo "error: $elf was not built" >&2; exit 1; }
"$AGG" --font-size 24 --fps-cap 3 --idle-time-limit 1 --last-frame-duration 3 \
  "$work/build.cast" "$work/build.raw.gif" >/dev/null 2>&1
gifsicle -O3 --colors 8 "$work/build.raw.gif" -o "$work/sim_upload_build.gif"

echo ">> run: recording the browser"
start=$(uv run --no-project --with playwright python scripts/record_sim_upload_browser.py \
  "$elf" "$work/run.webm" | tail -1)
ffmpeg -loglevel error -ss "$start" -i "$work/run.webm" \
  -vf "fps=6,split[a][b];[a]palettegen=max_colors=48[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \
  "$work/run.raw.gif"
gifsicle -O3 --lossy=40 "$work/run.raw.gif" -o "$work/sim_upload_run.gif"

for lang in ja en; do
  cp "$work/sim_upload_build.gif" "$work/sim_upload_run.gif" "docs/$lang/source/_static/"
done
ls -l docs/ja/source/_static/sim_upload_*.gif
