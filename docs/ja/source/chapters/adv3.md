# 応用編 第3章: ヒープ自作 — malloc / free を書く

malloc / free を自分で書き、断片化と戦います。

## サンプルコード

- ディレクトリ: `code/adv3_heap`
- ビルドと書き込み:

```bash
pio run -d adv3_heap -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv3_heap](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv3_heap)


## ソースコード

この章のスケッチです。ファイル名をクリックすると開きます。コードは原稿リポジトリから自動で同期されているので、ここに出ているものが常に最新です。

:::{dropdown} `src/main.cpp` — 75 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv3_heap/src/main.cpp)

```{literalinclude} ../../../../code/adv3_heap/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_heap.h` — 22 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv3_heap/include/os_heap.h)

```{literalinclude} ../../../../code/adv3_heap/include/os_heap.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_heap.cpp` — 128 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv3_heap/src/os_heap.cpp)

```{literalinclude} ../../../../code/adv3_heap/src/os_heap.cpp
:language: cpp
:linenos:
```
:::


## 実機での出力

Arduino UNO R4 WiFi の実機で実際に取得した出力です（macOS / Windows の
両方で同じ結果を確認しています）。手元の出力と見比べてください。

ヒープの状態を段階ごとにダンプしています。

```{figure} ../_static/adv3_heap.gif
:name: fig-adv3-heap
:width: 100%

`S` を送ると、ここまでのダンプが一気に出ます。最後は「空きの合計は
足りていても連続領域が無ければ取れない」ところと、二重 `free` の検出です
```

```text
=== Advanced 3: my_malloc / my_free ===

### heap_init()
---- heap dump ----
[00] +0000 size= 4080 FREE
total free=4080 used=0

### a = my_malloc(100)
---- heap dump ----
[00] +0000 size=  104 USED
[01] +0120 size= 3960 FREE
total free=3960 used=104

### b = my_malloc(100)
---- heap dump ----
[00] +0000 size=  104 USED
[01] +0120 size=  104 USED
[02] +0240 size= 3840 FREE
total free=3840 used=208
...
```

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
