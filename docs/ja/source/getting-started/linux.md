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

### uv を入れる

[uv](https://docs.astral.sh/uv/) は Python の環境とパッケージをまとめて
面倒みてくれる道具です。PlatformIO をこれで動かします。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール先は `~/.local/bin` です。シェルを開き直すか、次を実行して
PATH に反映してください。

```bash
source ~/.bashrc          # zsh なら ~/.zshrc
uv --version
```

`git` が入っていない場合は先に入れてください。

```bash
sudo apt install -y git   # Ubuntu / Debian
```

### サンプルコードを取ってくる

```bash
git clone https://github.com/iory/build-your-own-arduino-rtos.git
cd build-your-own-arduino-rtos/code
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

第5章（`05_shell`）を書き込んだ状態で試してください。シェルが動いているので、
`ps` を送るとタスク表が返ってきます。

```python
import time
import serial
import serial.tools.list_ports

# Arduino の USB ベンダ ID。ポート名を書かずに済む
port = next(p.device for p in serial.tools.list_ports.comports() if p.vid == 0x2341)
print("見つかったポート:", port)

ser = serial.Serial(port, 115200, timeout=0.2)
time.sleep(1.6)          # 開くとボードがリセットされるので待つ
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

`hello_serial.py` を実行して、ボードのシェルに応答させたところ
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
cd code/13_quadruped/host
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
