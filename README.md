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
scripts/build.sh  # 両言語を _site/ にビルド
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
