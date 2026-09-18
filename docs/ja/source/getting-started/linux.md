# Linux での開発

Linux でも Windows / macOS と同じコマンドで全章をビルド・書き込みできます。
違うのはポート名が `/dev/ttyACM0` のような形になることと、インストール方法くらいです。

ただし **Linux でしか出ないエラー**がいくつかあり、そこで止まると原因が
分かりにくいので、実際の出力とあわせてまとめます。あわせて、書籍では扱って
いない **Python からボードと通信する方法**もここに置きます。

```{note}
このページの出力例は Arduino UNO R4 WiFi の実機を Ubuntu 24.04 LTS (x86_64) に
つないで取ったものです。他のディストリビューションでの違いは「9. Ubuntu 以外」に
まとめてあります。
```

## 1. 環境をつくる

### 端末（ターミナル）を開く

このページのコマンドは、すべて**端末**に打ち込みます。Ubuntu では
**Ctrl + Alt + T** で開きます。左下のアプリ一覧から「端末」を探しても同じです。

```{figure} ../_static/linux_terminal.gif
:name: fig-linux-terminal
:width: 100%

端末を開いて、次の uv のインストールを打ち込んだところ。入れた直後は
まだ PATH が通っておらず、`source` してから `uv --version` が通ります
```

`ユーザ名@マシン名:~$` のような行（プロンプト）が出れば準備完了です。
`$` の右にコマンドを打って Enter を押すと実行されます。以降、行頭の `$` は
「ここに打つ」という意味なので、`$` 自体は入力しません。

### uv を入れる

[uv](https://docs.astral.sh/uv/) は Python の環境とパッケージをまとめて
面倒みてくれる道具です。PlatformIO をこれで動かします。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール先は `~/.local/bin` です。**入れた直後のシェルはまだ PATH を
知らない**ので、そのまま `uv` を打つと `command not found` になります。
シェルを開き直すか、次を実行して PATH に反映してください。

```bash
source ~/.bashrc          # zsh なら ~/.zshrc
uv --version
```

`source ~/.local/bin/env` でも PATH だけ通せます（上の GIF はこちらです）。

このとき Ubuntu は `sudo snap install astral-uv` を勧めてきますが、**従わないで
ください**。uv は入っていて、PATH がまだ通っていないだけです。

`git` が入っていない場合は先に入れてください。

```bash
sudo apt install -y git   # Ubuntu / Debian
```

### サンプルコードを取ってくる

```bash
git clone https://github.com/iory/learning-os-from-arduino.git
cd learning-os-from-arduino/docs/os-on-arduino/code
uv sync
```

`uv sync` で PlatformIO と pyserial が入ります。**コンパイラは入れなくて
かまいません。** PlatformIO が `~/.platformio` へ自前で取ってきます
（初回のビルドで数百 MB ぶん、数分かかります）。

## 2. ボードをつなぐ前に — udev ルールを入れる

**先にこれをやってください。** あとで説明する 2 つの問題（権限と
ModemManager）が、これ 1 つでまとめて解決します。

```bash
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/develop/platformio/assets/system/99-platformio-udev.rules \
  | sudo tee /etc/udev/rules.d/99-platformio-udev.rules >/dev/null
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**入れたあとは USB を一度抜き挿ししてください。** 既につないでいるデバイスには
自動で反映されません。

これは PlatformIO 公式の udev ルールです
（[公式の説明](https://docs.platformio.org/en/latest/core/installation/udev-rules.html)）。

## 3. ボードを見つける

```bash
uv run pio device list
```

```text
/dev/ttyACM0
------------
Hardware ID: USB VID:PID=2341:1002 SER=B43A45B9F1CC LOCATION=1-1:1.1
Description: UNO WiFi R4 CMSIS-DAP - TinyUSB CDC
```

`2341:1002` が Arduino UNO R4 WiFi です。`2341` が Arduino のベンダ ID で、
あとで Python からポートを自動検出するときに使います。

`/dev/ttyS*` がたくさん出ることがありますが、これはマザーボード上の
シリアルポートで、ボードとは関係ありません。**`ttyACM`** の行を見てください。

```{admonition} 番号は固定ではありません
:class: warning

`/dev/ttyACM0` の **0 は「何番目に挿されたか」でしかありません**。
抜き挿ししたり、ほかの USB シリアル機器を先につないだりすると、
同じボードが `/dev/ttyACM1` になります。書き込みが急に
`No such file or directory` で失敗したら、まずこれを疑ってください。

いま何番かは、こう調べます。

    uv run pio device list          # Hardware ID に 2341:1002 と出る行
    ls /dev/ttyACM*                 # 手早く見るだけなら

どれが今挿したボードなのか確実に知りたいときは、カーネルのログを
**流しっぱなしにしておいて、その場で挿す**のがいちばん早いです。

    sudo dmesg --follow          # 止めるときは Ctrl-C

この状態でボードを挿すと、その瞬間にこの行が出ます。

    cdc_acm 1-1:1.1: ttyACM0: USB ACM device

`ttyACM0` の部分が、いま挿したボードの名前です。抜くと `USB disconnect` が
出るので、抜き挿しすれば番号の対応が確実に分かります。

`sudo` を付けるのは、Ubuntu では `dmesg` が root 専用（`kernel.dmesg_restrict=1`）
だからです。付けずに実行すると
`read kernel buffer failed: Operation not permitted` になります。

**Windows でも同じことが起きます**（`COM3` が `COM5` になる）。
番号に依存しない書き方は「7. Python からボードと通信する」にあります。
```

## 4. ビルドして書き込む

```bash
uv run pio run -d 01_boot -t upload
```

```{figure} ../_static/linux_upload.gif
:name: fig-linux-upload
:width: 100%

ポートを確認して書き込むところ。実機の Ubuntu 24.04 で流したものです
```

`Auto-detected: /dev/ttyACM0` のとおり、ふつうはポートを指定しなくても
見つかります。ほかに USB シリアル機器がつながっていて誤検出されるときだけ
`--upload-port /dev/ttyACM0` を足してください。

## 5. シリアルモニタで見る

```bash
uv run pio device monitor -b 115200
```

第1章は **`S` を 1 文字送ると出力が始まります**。モニタが開いたら `S` を
打ってください。

```{admonition} なぜ `S` を待たせているのか
:class: note

ボードは電源が入った瞬間から全速力で走り出します。一方こちらは、書き込みが
終わってからシリアルモニタを開くまでに数秒かかります。第1章のスケッチは
`setup()` の中で一度だけ印字して終わるので、**普通に書くとモニタが開く前に
出力が終わってしまい、何も見えません**。しかも UNO R4 WiFi は、**シリアル
ポートを開いてもリセットされません**（USB 通信はボード上の ESP32-S3 が
受け持っていて、プログラムが動く RA4M1 とは独立しているためです）。
つまりモニタを開き直しても、最初からやり直してはくれません。

そこで「PC 側の準備ができた」ことをボードに伝える必要があります。
`S` はその合図です。スケッチは

    while (Serial.read() != 'S') { delay(1); }

で足踏みし、`S` が届いてから印字を始めます。だからモニタを開くのが何秒
遅れても、出力を最初から見られます。

Linux ではもう一つ理由があります。**ModemManager** が書き込み直後にポートを
開きにくるため、`while (!Serial)` だけでは「ホストが繋がった」と誤って
判定されてしまいます（「6. Linux でつまずくところ」を参照）。

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

モニタを終了するには `Ctrl-C` を押します。

## 6. Linux でつまずくところ

### `Permission denied: /dev/ttyACM0`

udev ルールを入れずにボードをつなぐと、こうなります。

```text
$ cat /dev/ttyACM0
cat: /dev/ttyACM0: Permission denied
```

Python からだと、こう出ます。

```text
PermissionError: [Errno 13] Permission denied: '/dev/ttyACM0'
```

原因はデバイスファイルの所有グループです。

```bash
$ ls -l /dev/ttyACM0
crw-rw---- 1 root dialout 166, 0 Aug 31 01:51 /dev/ttyACM0
#                  ^^^^^^^ このグループに入っていないと開けない
```

**「2. udev ルール」を入れていれば、この問題は起きません。**
PlatformIO のルールが `MODE="0666"` を設定するので、誰でも開けるように
なります。

```bash
$ ls -l /dev/ttyACM0
crw-rw-rw- 1 root dialout 166, 0 Aug 31 02:12 /dev/ttyACM0
```

udev ルールを使わない場合（Arduino IDE だけを使う場合など）は、
自分を `dialout` グループに入れてください。

```bash
sudo usermod -aG dialout $USER
```

**このあと一度ログアウトして入り直す必要があります。** グループの変更は
ログインし直すまで効きません。いま開いているターミナルだけで先に有効に
したいときは `newgrp dialout` が使えます。

### ModemManager がボードを掴む

Ubuntu には **ModemManager** という常駐サービスがいて、USB シリアル機器が
現れると「モバイル回線のモデムかもしれない」と考えて調べにいきます。
Arduino はモデムではないのですが、**つないだ直後にポートを開かれる**ため、
`setup()` の中でしか出力しないスケッチだと、こちらがモニタを開くより前に
出力が終わってしまいます。

書籍の第1章が `S` を待つ仕組みになっているのは、これが理由です。

いま自分の環境がどうなっているかは、こう調べます。

```bash
$ udevadm info -q property -n /dev/ttyACM0 | grep ID_MM
ID_MM_CANDIDATE=1
```

`ID_MM_CANDIDATE=1` だけが出る場合、ModemManager の対象になっています。
**「2. udev ルール」を入れると、こうなります。**

```bash
$ udevadm info -q property -n /dev/ttyACM0 | grep ID_MM
ID_MM_CANDIDATE=1
ID_MM_DEVICE_IGNORE=1
ID_MM_PORT_IGNORE=1
```

`ID_MM_DEVICE_IGNORE=1` が付けば、ModemManager はこのデバイスに触りません。

```{admonition} なぜ PlatformIO のルールで効くのか
:class: note

公式ルールの Arduino 向けの行は `idProduct` を `[08][023]*` に限っていて、
UNO R4 WiFi の PID `1002` は**この条件に一致しません**。
効いているのは、その下にある別の行です。

    ATTRS{product}=="*CMSIS-DAP*", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1", ENV{ID_MM_PORT_IGNORE}="1"

UNO R4 WiFi は USB の製品名が `UNO WiFi R4 CMSIS-DAP` なので、
**PID ではなく製品名でマッチ**しています。
```

ModemManager をまったく使っていない（モバイル回線を使わない）機械なら、
止めてしまう手もあります。ただし udev ルールで足りるので、ふつうは不要です。

```bash
sudo systemctl disable --now ModemManager
```

### モニタを開いたままだと書き込めない

シリアルポートを開けるのは同時に 1 つだけです。モニタを開いたまま `upload`
すると失敗します。Windows の `PermissionError` にあたるもので、Linux では
`Device or resource busy` と出ます。**モニタを `Ctrl-C` で閉じてから**
書き込み直してください。

Arduino IDE のシリアルモニタや、自分で書いた Python スクリプトが掴んで
いるときも同じです。

### そのほか

- **`brltty`**。点字ディスプレイ用の常駐で、Ubuntu には既定で入っています。
  一部の USB シリアル機器を横取りするため、`/dev/ttyACM0` が現れてすぐ
  消えるようなら疑ってください（`systemctl status brltty` で確認できます）。
  UNO R4 WiFi では確認されていませんが、USB-シリアル変換器を使う場合は
  起こりえます
- **USB ハブ経由**だと書き込みに失敗することがあります。PC 本体に直挿しを
  試してください
- ボードが応答しなくなったら **RESET ボタンを素早く 2 回押す**と
  ブートローダに入ります

## 7. Python からボードと通信する

書籍ではシリアルモニタで見るところまでしか扱いませんが、実際に何か作るときは
PC 側のプログラムからボードと話したくなります。`uv sync` で入る
**pyserial** を使います。

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
time.sleep(1.6)          # 挿した直後は取りこぼすことがあるので少し待つ
ser.reset_input_buffer()

ser.write(b"ps\n")
time.sleep(1.0)
print(ser.read(4096).decode("utf-8", errors="replace"))
ser.close()
```

```bash
uv run python hello_serial.py
```

```{figure} ../_static/linux_pyserial.gif
:name: fig-linux-pyserial
:width: 100%

`hello_serial.py` を実行したところ
```

```text
見つかったポート: /dev/ttyACM0
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

### 打ちながら試す

送るコマンドを決め打ちにせず、その場で打ちたいときは、読む側を別スレッドに
するだけの短いコンソールが書けます。

```python
"""ボードのシェルと対話する、最小のシリアルコンソール。Ctrl-D で終了。"""
import sys
import time
import threading
import serial
import serial.tools.list_ports

port = next(p.device for p in serial.tools.list_ports.comports() if p.vid == 0x2341)
print(f"connected: {port}  (Ctrl-D で終了)")

ser = serial.Serial(port, 115200, timeout=0.2)
time.sleep(1.6)                      # 挿した直後は取りこぼすことがあるので少し待つ
ser.reset_input_buffer()

def reader():                        # ボードからの出力を流し続ける
    while True:
        data = ser.read(4096)
        if data:
            sys.stdout.write(data.decode("utf-8", errors="replace"))
            sys.stdout.flush()

threading.Thread(target=reader, daemon=True).start()

# for line in sys.stdin: は読み溜めするので、対話では readline を使う
for line in iter(sys.stdin.readline, ""):   # 打った行をボードへ送る
    ser.write(line.encode())
    ser.flush()
```

```bash
uv run python serial_console.py
```

```{figure} ../_static/linux_console.gif
:name: fig-linux-console
:width: 100%

`ps` でタスク表を見て、`kill 1` で LED1 を止め（`SUSPEND` に変わります）、
`exec 1` で戻すところ。実機の Ubuntu 24.04 で打ったものです
```

`kill 1` を打つと基板の L LED の点滅が止まり、`exec 1` で再開します。
画面の `STATE` と手元の LED が一致していることを確かめてください。

### 覚えておくと詰まらない 3 つ

**ポート名を書かない。** 上の `p.vid == 0x2341` で探す書き方なら、
**Linux / macOS / Windows のどれでも同じコードが動きます**
（`/dev/ttyACM0` / `/dev/cu.usbmodem...` / `COM3` のどれが返るかの違いだけです）。

**開いたら 1.5 秒待つ。** UNO R4 はポートを開くとスケッチが再起動します。
待たずに書き込むと、最初の出力を取り逃したり、コマンドが届かなかったりします。

**ポートは 1 つのプロセスしか開けません。** PlatformIO のモニタや
Arduino IDE を閉じてから実行してください。

## 8. 四脚ロボットを PC から動かす

第13章の四脚ロボットは、組み立てと校正を PC 側からやるほうが早いです
（値が全部画面に出て、直すたびに焼き直さなくて済みます）。

```bash
cd docs/os-on-arduino/code/13_quadruped/host
uv run python quad_host.py scan        # バスに何個サーボがいるか
uv run python quad_host.py calibrate   # zero と sign を測る -> calib.json
uv run python quad_host.py stand       # home 姿勢を保持
uv run python quad_host.py teleop      # w/s/a/d で歩かせる
```

ポートを明示したいときは `--port /dev/ttyACM0` を足してください。

組み立てと学習の全体像は {doc}`../hardware/walk` にあります。

## 9. Ubuntu 以外

このページは Ubuntu 24.04 で確認したものです。他のディストリビューションでも
手順はほぼ同じで、**違うのはパッケージの入れ方とグループ名だけ**です。

| | Ubuntu / Debian | Fedora | Arch |
|---|---|---|---|
| git を入れる | `sudo apt install git` | `sudo dnf install git` | `sudo pacman -S git` |
| シリアルのグループ | `dialout` | `dialout` | **`uucp`** |

**`uv` の導入と PlatformIO のツールチェインは、どのディストリビューションでも
同じです。** コンパイラを自前で用意する必要はありません。

自分の環境でどのグループが要るかは、これで分かります。

```bash
$ ls -l /dev/ttyACM0
crw-rw---- 1 root dialout 166, 0 Aug 31 01:51 /dev/ttyACM0
#                  ^^^^^^^ ここに出るのが、入るべきグループ
```

udev ルールを入れれば、そもそもグループを気にしなくてよくなります。

## 10. 全章をまとめて確認する

同梱のスクリプトで、全章をビルドして実機に書き込み、出力が書籍の記載どおりかを
自動で突き合わせられます。

```bash
uv run python scripts/verify_chapters.py
```

詳しくは {doc}`../chapters/verify` を見てください。
