# macOS での開発

macOS は本書の標準的な開発環境です。ドライバの導入は要らず、つないだ時点で
ポートが現れます。Windows / Linux と同じコマンドで全章をビルド・書き込みできます。

違うのは **ポート名が `/dev/cu.usbmodem…` になること**と、
**同じボードに `/dev/cu.` と `/dev/tty.` の 2 つの名前ができること**くらいです。

```{note}
このページの出力例は Arduino UNO R4 WiFi の実機を macOS 26.5.1（Apple Silicon /
arm64）につないで取ったものです。
```

## 1. 環境をつくる

### ターミナルを開く

このページのコマンドは、すべて**ターミナル**に打ち込みます。
**Command + Space** で Spotlight を開き、`ターミナル`（または `Terminal`）と
打って Enter が一番早いです。アプリケーション › ユーティリティ › ターミナル
からも開けます。

```{figure} ../_static/macos_terminal.gif
:name: fig-macos-terminal
:width: 100%

ターミナルでボードを探しているところ。`%` の右にコマンドを打って Enter します
```

`ユーザ名@マシン名 ~ %` のような行（プロンプト）が出れば準備完了です。
以降、行頭の `%` は「ここに打つ」という意味なので、`%` 自体は入力しません。

```{note}
プロンプトの記号はシェルによって変わります。macOS の既定は zsh なので `%` ですが、
bash なら `$` です。どちらでも打つ内容は同じです。
```

### uv を入れる

[uv](https://docs.astral.sh/uv/) は Python の環境とパッケージをまとめて
面倒みてくれる道具です。PlatformIO をこれで動かします。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール先は `~/.local/bin` です。**入れた直後のシェルはまだ PATH を
知らない**ので、そのまま `uv` を打つと `command not found` になります。
ターミナルを開き直すか、次を実行してください。

```bash
source ~/.zshrc           # bash なら ~/.bash_profile
uv --version
```

`source ~/.local/bin/env` でも PATH だけ通せます。

### サンプルコードを取ってくる

```bash
git clone https://github.com/iory/build-your-own-arduino-rtos.git
cd build-your-own-arduino-rtos/code
uv sync
```

`git` が入っていなければ、初回に Xcode のコマンドラインツールの導入を促す
ダイアログが出ます。指示に従って入れてください。

## 2. ボードを見つける

USB でつなぐだけです。**ドライバの導入は要りません。**

```bash
uv run pio device list
```

ただし macOS は Bluetooth 機器なども `/dev/cu.*` として並べるので、
そのままだと目的のボードが埋もれます。`grep` で絞ると見つけやすいです。

```bash
uv run pio device list | grep -A 3 usbmodem
```

```text
/dev/cu.usbmodemB43A45B9F1CC2
-----------------------------
Hardware ID: USB VID:PID=2341:1002 SER=B43A45B9F1CC LOCATION=2-1
Description: UNO WiFi R4 CMSIS-DAP
```

```{admonition} grep は「その行だけ取り出す」道具
:class: note

`|`（パイプ）は左のコマンドの出力を右のコマンドに渡す記号です。
`grep usbmodem` は、受け取った出力のうち **`usbmodem` を含む行だけ**を通します。

`-A 3` は「見つかった行の**後ろ 3 行**も一緒に出す」という意味です
（`A` は after）。ポート名の下に `Hardware ID` と `Description` が続くので、
これを付けないとポート名しか見えません。

`Hardware ID` が `2341:1002` になっていれば、それが Arduino UNO R4 WiFi です。
```

```{admonition} `cu.` と `tty.` の 2 つが現れます
:class: warning

同じボードに対して、macOS は次の 2 つを作ります。

    /dev/cu.usbmodemB43A45B9F1CC2      ← こちらを使う
    /dev/tty.usbmodemB43A45B9F1CC2

`cu`（call-out）はこちらから話しかけるための名前、`tty`（call-in）は
かかってくるのを待つための名前です。**書き込みもモニタも `cu.` のほう**を
使ってください。`uv run pio device list` に出るのも `cu.` だけです。

末尾の英数字はボードごとに違うシリアル番号なので、**手元では別の文字列**に
なります。番号ではなくシリアルなので、抜き挿ししても変わりません
（Linux の `ttyACM0` / `ttyACM1` のように入れ替わることはありません）。
```

## 3. ビルドして書き込む

```bash
uv run pio run -d 01_boot -t upload
```

```text
Uploading .pio/build/uno_r4_wifi/firmware.bin
Erase flash

Done in 0.001 seconds
Write 35356 bytes to flash (9 pages)

[==============================] 100% (9/9 pages)
Done in 2.229 seconds
========================= [SUCCESS] Took 5.24 seconds =========================
```

ふつうはポートを指定しなくても見つかります。ほかに USB シリアル機器が
つながっていて誤検出されるときだけ、`--upload-port` を足してください。

```bash
uv run pio run -d 01_boot -t upload --upload-port /dev/cu.usbmodemB43A45B9F1CC2
```

## 4. シリアルモニタで見る

```bash
uv run pio device monitor -b 115200
```

抜けるときは `Ctrl-C` です。

第1章は **`S` を 1 文字送ると出力が始まります**。モニタが開いたら `S` を
打ってください。

```{admonition} なぜ `S` を待たせているのか
:class: note

ボードは電源が入った瞬間から全速力で走り出しますが、こちらは書き込みが
終わってからモニタを開くまでに数秒かかります。`setup()` の中で一度だけ
印字して終わる章では、**普通に書くとモニタが開く前に出力が終わってしまい、
何も見えません**。しかも UNO R4 WiFi は、**シリアルポートを開いても
リセットされません**（USB 通信はボード上の ESP32-S3 が受け持っていて、
プログラムが動く RA4M1 とは独立しているためです）。つまりモニタを開き直しても、
最初からやり直してはくれません。

そこで「PC 側の準備ができた」ことをボードに伝えます。`S` はその合図です。

    while (Serial.read() != 'S') { delay(1); }

書籍では `01_boot` / `01_boot_vector_dump` / 応用編の `adv3_heap` と
`adv4_fs` がこの形です。ずっと印字し続ける章（第2章など）には要りません。
```

```text
=== Boot Sequence Check ===

bss_var (should be 0): 0
data_var (should be 12345): 12345

=== Memory Addresses ===
&bss_var:  0x200000C4
&data_var: 0x20000000
VTOR:      0x20007F00
MSP:       0x20007EC8

If you see this, boot sequence completed!
```

## 5. macOS でつまずくところ

### モニタを開いたままだと書き込めない

ポートを開けるのは一度に 1 つだけです。シリアルモニタ、Arduino IDE、
自分の Python スクリプトのうち、**動かしていいのは 1 つ**です。
書き込む前に `Ctrl-C` でモニタを閉じてください。

### ボードが見つからない

- **USB ハブ経由だと失敗することがあります。** Mac 本体に直挿ししてください
- ケーブルが充電専用だと、電源は入っても通信できません。データ線のあるものを
  使ってください
- それでも見つからないときは、**RESET を素早く 2 回**押してブートローダに
  入れてから、もう一度書き込んでください

### `/dev/cu.` の名前が長い

シリアル番号が入るので長くなりますが、**打つ必要はほとんどありません**。
`pio` は自動で見つけますし、Python からはベンダ ID で探せます（下記）。

## 6. Python からボードと通信する

書き込みができるようになったら、PC 側のプログラムからボードと話したくなります。
`uv sync` の時点で `pyserial` が入っているので、すぐ書けます。

### 最小の例

{doc}`第5章（05_shell）<../chapters/ch05>` を書き込んだ状態で試してください。
シェルが動いているので、`ps` を送るとタスク表が返ってきます。

```python
import time
import serial
import serial.tools.list_ports

# Arduino の USB ベンダ ID。ポート名を書かずに済む
port = next(p.device for p in serial.tools.list_ports.comports() if p.vid == 0x2341)
print("見つかったポート:", port)

ser = serial.Serial(port, 115200, timeout=0.2)
time.sleep(1.0)                      # 挿した直後は取りこぼすことがあるので少し待つ
ser.reset_input_buffer()

ser.write(b"ps\n")
time.sleep(0.8)
print(ser.read(4096).decode("utf-8", errors="replace").replace("\r\n", "\n"))
ser.close()
```

```bash
uv run python hello_serial.py
```

```text
見つかったポート: /dev/cu.usbmodemB43A45B9F1CC2
ps

ID  NAME           STATE      CPU%
--  ----           -----      ----
0   idle           READY     100%
1   LED1           BLOCKED   0%
2   LED2           BLOCKED   0%
3   Heartbeat      BLOCKED   0%
4   Shell          RUNNING   0%

>
```

### 覚えておくと詰まらない 3 つ

**ポート名を書かない。** 上の `p.vid == 0x2341` で探す書き方なら、
**同じコードが macOS / Windows / Linux のどれでも動きます**。
`/dev/cu.usbmodem…` を直書きすると、別の Mac では動きません。

**開いたらすこし待つ。** つないだ直後は取りこぼすことがあります。
1 秒ほど待ってから `reset_input_buffer()` すると安定します。

**ポートは 1 つのプログラムだけ。** モニタを開いたままスクリプトを走らせると、
どちらかが失敗します。

## 7. 全章をまとめて確認する

全章を順に書き込んで出力を照合する手順は
{doc}`../chapters/verify` にまとめてあります。macOS でもそのまま使えます。

```bash
uv run python scripts/verify_chapters.py
```
