# build-your-own-arduino-rtos

書籍**『つくりながら学ぶ！リアルタイムOS自作入門』**（Arduino UNO R4
WiFi でプリエンプティブなリアルタイム OS を一から自作する本）の
サポートページです。

- サイト: https://iory.github.io/build-your-own-arduino-rtos/ （日本語）
  / [English](https://iory.github.io/build-your-own-arduino-rtos/en/)
- 内容: 開発環境のセットアップ、章ごとのサンプルコード案内、
  四脚ロボットの組み立て、FAQ・正誤表

## 構成

XLeRobot のドキュメント（Sphinx + pydata-sphinx-theme + MyST +
sphinx-design）を参考に、言語ごとに独立したツリーを持つ:

```
docs/ja/source/   # 日本語（サイトのルートに配信）
docs/en/source/   # English（/en/ に配信）
docs/assembly/    # CAD から自動生成した組み立てビューア（静的バンドル、/assembly/ に配信）
scripts/build.sh  # 両言語を _site/ にビルドし docs/assembly をコピー
```

言語切替はナビバーの Language ドロップダウン
（`BASE_URL` 環境変数でリンク先のベースパスを指定。
GitHub Pages では workflow が `/build-your-own-arduino-rtos/` を渡す）。

## ローカルビルド

```bash
uv sync
./scripts/build.sh
python3 -m http.server -d _site 8000   # http://localhost:8000/
```

main へ push すると GitHub Actions が GitHub Pages へ自動デプロイする
（リポジトリ設定の Pages で Source: GitHub Actions を選んでおくこと）。

## 組み立てビューアの再生成

`docs/assembly/quadruped/`（three.js ビューア・GLB・PDF）と
`docs/ja/source/hardware/assembly_img/`（手順 PNG）は
[create-assembly-view](https://github.com/iory/create-assembly-view) で
CAD の graph.json から自動生成したもの。モデルを更新したら:

```bash
cd ~/src/github.com/iory/create-assembly-view
uv run create-assembly-view models/sts3215_quadruped/graph.json -o output/quadruped_site
PYOPENGL_PLATFORM=egl uv run create-assembly-view-render \
    models/sts3215_quadruped/graph.json output/quadruped_site/plan.yaml -o output/quadruped_site
uv run create-assembly-view-viewer \
    models/sts3215_quadruped/graph.json output/quadruped_site/plan.yaml -o output/quadruped_site
uv run create-assembly-view-pdf output/quadruped_site/plan.yaml -o output/quadruped_site
# → index.html/glb/vendor/instructions.pdf を docs/assembly/quadruped/ に、
#   steps/*.png と units/ を docs/ja/source/hardware/assembly_img/ にコピー
#
# docs/assembly/quadruped/stl/ の配布物は create-assembly-view リポジトリの
# cad/ からコピーしたもの:
#   body.stl / bracket_outline.stl / leg_link1.stl ← cad/*.STL（SolidWorks 直接出力、mm）
#   body.3mf / leg_parts.3mf ← cad/*.3mf（Bambu Studio プロジェクト、設定・配置込み）
# docs/ja/source/hardware/print_img/ のプレート画像も cad/bambulab-*.png から
```
