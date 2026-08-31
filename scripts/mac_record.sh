#!/bin/bash
# Terminal.app を開いてデモを走らせ、そのウィンドウだけを連写して GIF の素にする
set -e
SP="$1"; SECS="${2:-30}"
rm -rf "$SP/frames"; mkdir -p "$SP/frames"

osascript >/dev/null <<'OSA'
tell application "Terminal"
    activate
    do script "exec uv run --no-project --with pexpect python3 /tmp/os-demo/mac_type.py"
    delay 0.8
    set bounds of front window to {60, 80, 1000, 560}
    set custom title of front window to "zsh"
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
echo "window id = $WID"
[ -z "$WID" ] && { echo "Terminal のウィンドウが見つからない"; exit 1; }

END=$(( $(date +%s) + SECS ))
i=0
while [ "$(date +%s)" -lt "$END" ]; do
  i=$((i+1))
  screencapture -x -o -l "$WID" "$SP/frames/$(printf '%04d' $i).png" 2>/dev/null || break
done
echo "captured $i frames"
