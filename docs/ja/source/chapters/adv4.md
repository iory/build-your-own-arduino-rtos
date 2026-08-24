# アドバンス章4: 最小ファイルシステム — LittleFS

Flash 上に LittleFS を載せ、ファイルという抽象を手に入れます。

## サンプルコード

- ディレクトリ: `code/adv4_fs`
- ビルドと書き込み:

```bash
pio run -d adv4_fs -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv4_fs](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv4_fs)

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
