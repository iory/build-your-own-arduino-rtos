#!/bin/bash
# Terminal.app でデモを走らせ、そのウィンドウだけを連写して GIF の素にする。
#
#   ./scripts/mac_record.sh <出力ディレクトリ> [秒数]
#
# 画面全体ではなくウィンドウ ID を指定して撮るので、前面に別のウィンドウが
# あっても対象だけが写り、画面の他の部分は入らない。
set -e

OUT="${1:?使い方: $0 <出力ディレクトリ> [秒数]}"
SECS="${2:-30}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO="$HERE/mac_type_demo.py"

command -v uv >/dev/null || { echo "uv が見つかりません"; exit 1; }
[ -f "$DEMO" ] || { echo "$DEMO が見つかりません"; exit 1; }

rm -rf "$OUT/frames"; mkdir -p "$OUT/frames"

# pexpect は macOS のシステム python には無いので uv 経由で用意する
osascript >/dev/null <<OSA
tell application "Terminal"
    activate
    do script "exec $(command -v uv) run --no-project --with pexpect python3 $DEMO"
    delay 0.8
    set bounds of front window to {60, 80, 1000, 560}
end tell
OSA

sleep 1
WID=$(uv run --no-project --with pyobjc-framework-Quartz python3 -c "
import Quartz
o = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
ws = [w for w in Quartz.CGWindowListCopyWindowInfo(o, Quartz.kCGNullWindowID)
      if w.get('kCGWindowOwnerName') == 'Terminal']
print(ws[0]['kCGWindowNumber'] if ws else '')
" 2>/dev/null)
[ -n "$WID" ] || { echo "Terminal のウィンドウが見つかりません"; exit 1; }
echo "window id = $WID"

END=$(( $(date +%s) + SECS ))
i=0
while [ "$(date +%s)" -lt "$END" ]; do
  i=$((i+1))
  screencapture -x -o -l "$WID" "$OUT/frames/$(printf '%04d' $i).png" 2>/dev/null || break
done
echo "captured $i frames"

# タイトルバーには実行中プロセスのコマンドラインが出てしまうので、
# GIF にするときは上端を切り落とすこと（crop の y オフセットを 56 前後にする）。
