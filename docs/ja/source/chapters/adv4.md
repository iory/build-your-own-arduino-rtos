# 応用編 第4章: 最小ファイルシステム — LittleFS

Flash 上に LittleFS を載せ、ファイルという抽象を手に入れます。

## サンプルコード

- ディレクトリ: `code/adv4_fs`
- ビルドと書き込み:

```bash
pio run -d adv4_fs -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv4_fs](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv4_fs)


## ソースコード

この章のスケッチです。ファイル名をクリックすると開きます。コードは原稿リポジトリから自動で同期されているので、ここに出ているものが常に最新です。

:::{dropdown} `src/main.cpp` — 97 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/main.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/fs.h` — 18 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/include/fs.h)

```{literalinclude} ../../../../code/adv4_fs/include/fs.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/fs_flash_hal.h` — 19 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/include/fs_flash_hal.h)

```{literalinclude} ../../../../code/adv4_fs/include/fs_flash_hal.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/fs.cpp` — 70 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/fs.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/fs.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/fs_flash_hal.cpp` — 53 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/fs_flash_hal.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/fs_flash_hal.cpp
:language: cpp
:linenos:
```
:::


## 実機での出力

Arduino UNO R4 WiFi の実機で実際に取得した出力です（macOS / Windows の
両方で同じ結果を確認しています）。手元の出力と見比べてください。

リセットするたびに `boot count` が増えます。Data Flash に残っている証拠です。

```{figure} ../_static/adv4_bootcount.gif
:name: fig-adv4-bootcount
:width: 100%

RESET を 6 回押しながら録ったところ。押すたびに `boot count` が
9, 10, 11 … と増えていきます。電源が切れても Data Flash に残っている証拠です
```

```text
=== Advanced 4: LittleFS on Data Flash ===
data flash: 8192 B / sector 1024 B
mounted.
boot count = 5
--- / ---
  [DIR ] .
  [DIR ] ..
  [FILE] boot_count  4 B
done. リセットすると boot count が増えます
```

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
