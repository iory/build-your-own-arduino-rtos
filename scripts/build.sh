#!/usr/bin/env bash
# 日本語(ルート) + 英語(/en/) を _site/ にビルドする
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf _site
uv run sphinx-build -b html docs/ja/source _site
uv run sphinx-build -b html docs/en/source _site/en
# CAD から自動生成した組み立てビューア（静的バンドル）を配置
cp -r docs/assembly _site/assembly
# ブラウザで動く仮想ボード（各章を pio run -e sim でビルドする）
./scripts/build_sim.sh _site/sim

# Sphinx が触らないビューアのページにも Cloudflare Web Analytics の
# ビーコンを入れる。docs/assembly/ は CAD から再生成されるので、原本では
# なくコピー後の _site/ 側に差し込む。トークン未設定なら何もしない。
if [ -n "${CF_BEACON_TOKEN:-}" ]; then
  beacon="<script type=\"module\" src=\"https://static.cloudflareinsights.com/beacon.min.js\" data-cf-beacon='{\"token\":\"${CF_BEACON_TOKEN}\"}'></script>"
  find _site/assembly -name '*.html' -print0 |
    while IFS= read -r -d '' page; do
      uv run python - "$page" "$beacon" <<'EOF'
import pathlib
import sys

path, tag = pathlib.Path(sys.argv[1]), sys.argv[2]
html = path.read_text()
if "cloudflareinsights" not in html:
    path.write_text(html.replace("</head>", tag + "\n</head>", 1))
EOF
    done
fi
touch _site/.nojekyll
echo "built into _site/ (open _site/index.html)"
