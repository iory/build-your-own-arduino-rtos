# アドバンス章2: ユーザー／カーネルモードと SVC

特権レベルを分離し、SVC でシステムコールを生やします。

## サンプルコード

- ディレクトリ: `code/adv2_syscall`
- ビルドと書き込み:

```bash
pio run -d adv2_syscall -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv2_syscall](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv2_syscall)

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
