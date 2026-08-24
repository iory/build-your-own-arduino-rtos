# アドバンス章1: ロックと同期 — 食事する哲学者を解く

ロック・セマフォを実装し、食事する哲学者問題を自分の OS で解きます。

## サンプルコード

- ディレクトリ: `code/adv1_sync`
- ビルドと書き込み:

```bash
pio run -d adv1_sync -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv1_sync](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv1_sync)

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
