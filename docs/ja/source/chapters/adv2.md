# 応用編 第2章: ユーザー／カーネルモードと SVC

特権レベルを分離し、SVC でシステムコールを生やします。

## サンプルコード

- ディレクトリ: `code/adv2_syscall`
- ビルドと書き込み:

```bash
pio run -d adv2_syscall -t upload
pio device monitor -b 115200
```

コードを見る: [code/adv2_syscall](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/adv2_syscall)


## ソースコード

この章のスケッチです。ファイル名をクリックすると開きます。コードは原稿リポジトリから自動で同期されているので、ここに出ているものが常に最新です。

:::{dropdown} `src/main.cpp` — 94 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/main.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_kernel.h` — 74 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_kernel.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_kernel.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_syscall.h` — 33 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_syscall.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_syscall.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_syscall_user.h` — 38 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_syscall_user.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_syscall_user.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_kernel.cpp` — 231 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/os_kernel.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/os_kernel.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_svc.cpp` — 95 行
:icon: code

[GitHub で開く](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/os_svc.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/os_svc.cpp
:language: cpp
:linenos:
```
:::


## 実機での出力

Arduino UNO R4 WiFi の実機で実際に取得した出力です（macOS / Windows の
両方で同じ結果を確認しています）。手元の出力と見比べてください。

出力はすべて `svc` 経由（`sys_putchar`）で出ています。

```text
[probe] svc #99 -> -1  (-1 なら ENOSYS 相当が返っている)
[A] pid=1
[B] count=2
[A] pid=1
[B] count=3
[A] pid=1
[A] pid=1
[B] count=4
[A] pid=1
[B] count=5
...
```

## つまずきやすいポイント

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
