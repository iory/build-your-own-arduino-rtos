# アドバンス章3: ヒープ自作 — malloc / free を書く

malloc / free を自分で書き、断片化と戦います。

## サンプルコード

- ディレクトリ: `code/adv3_heap`
- ビルドと書き込み:

```bash
pio run -d adv3_heap -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv3_heap](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv3_heap)

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
