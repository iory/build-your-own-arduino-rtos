# 応用編 第1章: ロックと同期 — 食事する哲学者を解く

ロック・セマフォを実装し、食事する哲学者問題を自分の OS で解きます。

## サンプルコード

- ディレクトリ: `docs/os-on-arduino/code/adv1_sync`
- ビルドと書き込み:

```bash
pio run -d adv1_sync -t upload
pio device monitor -b 115200
```

コードを見る: [docs/os-on-arduino/code/adv1_sync](https://github.com/iory/learning-os-from-arduino/tree/main/docs/os-on-arduino/code/adv1_sync)


## ソースコード

この章のスケッチです。ファイル名をクリックすると開きます。コードは原稿リポジトリから自動で同期されているので、ここに出ているものが常に最新です。

:::{dropdown} `src/main.cpp` — 140 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/main.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/main.cpp
:language: cpp
:linenos:
```

:::

:::{dropdown} `include/os_atomic.h` — 28 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_atomic.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_atomic.h
:language: cpp
:linenos:
```

:::

:::{dropdown} `include/os_fault.h` — 46 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_fault.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_fault.h
:language: cpp
:linenos:
```

:::

:::{dropdown} `include/os_kernel.h` — 76 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_kernel.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_kernel.h
:language: cpp
:linenos:
```

:::

:::{dropdown} `include/os_sync.h` — 53 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_sync.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_sync.h
:language: cpp
:linenos:
```

:::

:::{dropdown} `src/os_fault.cpp` — 170 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_fault.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_fault.cpp
:language: cpp
:linenos:
```

:::

:::{dropdown} `src/os_kernel.cpp` — 231 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_kernel.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_kernel.cpp
:language: cpp
:linenos:
```

:::

:::{dropdown} `src/os_sync.cpp` — 150 行
:icon: code

[GitHub で開く](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_sync.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_sync.cpp
:language: cpp
:linenos:
```

:::


## 実機での出力

Arduino UNO R4 WiFi の実機で実際に取得した出力です（macOS / Windows の
両方で同じ結果を確認しています）。手元の出力と見比べてください。

5 人の哲学者の食事回数です。全員が増え続けていれば、誰も飢えていない（デッドロックしていない）ことになります。

```{figure} ../_static/adv1_philosophers.gif
:name: fig-adv1-philosophers
:width: 100%

5 人の回数が横並びのまま伸びていくところ。特定の番号だけ取り残されない
ことが、止めずに見ていると分かります
```

```text
meals: P0=31 P1=31 P2=31 P3=30 P4=31
meals: P0=47 P1=46 P2=46 P3=46 P4=46
meals: P0=62 P1=61 P2=62 P3=61 P4=61
meals: P0=77 P1=77 P2=77 P3=76 P4=77
meals: P0=93 P1=92 P2=92 P3=92 P4=92
meals: P0=108 P1=107 P2=108 P3=107 P4=108
```

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
