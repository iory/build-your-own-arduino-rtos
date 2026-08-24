#!/usr/bin/env bash
# 日本語(ルート) + 英語(/en/) を _site/ にビルドする
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf _site
uv run sphinx-build -b html docs/ja/source _site
uv run sphinx-build -b html docs/en/source _site/en
touch _site/.nojekyll
echo "built into _site/ (open _site/index.html)"
