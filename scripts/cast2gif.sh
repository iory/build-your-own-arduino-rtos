#!/bin/bash
# cast2gif.sh <in.cast> <out.gif> [max_seconds]
# 既存のサポートページ GIF と体裁を揃える（幅 1228px 相当）。
set -e
IN=$1; OUT=$2; MAX=${3:-0}
TRIM=$IN
if [ "$MAX" != "0" ]; then
  TRIM="${IN%.cast}.trim.cast"
  python3 - "$IN" "$TRIM" "$MAX" <<'PY'
import json, sys, io
src, dst, mx = sys.argv[1], sys.argv[2], float(sys.argv[3])
lines = io.open(src, encoding="utf-8").read().split("\n")
out = [lines[0]]
for l in lines[1:]:
    if not l.strip():
        continue
    ev = json.loads(l)
    if ev[0] > mx:
        break
    out.append(l)
io.open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
fi
agg --font-size 24 --fps-cap 3 --idle-time-limit 1 --last-frame-duration 3 \
    "$TRIM" "$OUT.raw.gif" >/dev/null 2>&1
magick "$OUT.raw.gif" -layers Optimize -colors 8 "$OUT"
rm -f "$OUT.raw.gif"
magick identify -format "%wx%h  %n frames  %B bytes\n" "$OUT" | head -1
