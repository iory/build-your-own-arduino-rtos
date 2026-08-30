# Windows での開発

Windows でも Linux / macOS と同じコマンドで全章をビルド・書き込みできます。
違うのはポート名が `COM3` のような形になることと、インストール方法くらいです。

ただし **Windows でしか出ないエラー**がいくつかあり、そこで止まると原因が
分かりにくいので、実際の出力とあわせてまとめます。あわせて、書籍では扱って
いない **Python からボードと通信する方法**もここに置きます。

```{note}
このページの出力例は Arduino UNO R4 WiFi の実機を Windows 11 + PowerShell 7 に
つないで取ったものです。
```

## 1. 環境をつくる

### PowerShell を開く

**スタートボタンを右クリック → 「ターミナル」** が一番早いです
（`Win` + `X` でも同じメニューが出ます）。スタートメニューで `PowerShell` と
打って選んでもかまいません。管理者権限は要りません。

Windows 11 に最初から入っているのは **Windows PowerShell 5.1** です。
このページのコマンドはそのまま動きます。開いているものが何かは、これで
分かります。

```powershell
$PSVersionTable.PSVersion
```

より新しい [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows)
（コマンド名は `powershell` ではなく `pwsh`）でもかまいません。
このページの出力例は PowerShell 7.6.2 で取ったものです。

コマンドプロンプト（`cmd.exe`）でもビルドと書き込みはできますが、
例は PowerShell の書きかたに揃えてあります。

### uv を入れる

[uv](https://docs.astral.sh/uv/) は Python の環境とパッケージをまとめて
面倒みてくれるツールです。本書のサンプルコードはこれ 1 つで動きます。

PowerShell を開いて、次の 1 行を実行します。

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`winget install --id=astral-sh.uv -e` でも入ります。ほかの入れかたは
[uv のインストール手順](https://docs.astral.sh/uv/getting-started/installation/)
を参照してください。

インストーラは `%USERPROFILE%\.local\bin` に置いて、そこを PATH に足します。
**PowerShell を開き直さないと `uv` が見つかりません。** 開き直してから
確認してください。

```powershell
uv --version
```

```text
uv 0.9.26
```

### サンプルコードを取ってくる

```powershell
git clone https://github.com/iory/build-your-own-arduino-rtos.git
cd build-your-own-arduino-rtos\code
uv sync
```

`uv sync` で [PlatformIO](https://docs.platformio.org/) と
[pyserial](https://pyserial.readthedocs.io/) が入ります。以降、コマンドは
`uv run` を付けて呼びます。

## 2. ボードを見つける

USB でつないでから実行します。

```powershell
uv run pio device list
```

```text
COM3
----
Hardware ID: USB VID:PID=2341:1002 SER=B43A45B9F1CC LOCATION=-4:x.1
Description: USB シリアル デバイス (COM3)
```

番号は機械によって変わります（`COM4`、`COM5` …）。デバイスマネージャーの
**ポート (COM と LPT)** にも同じものが出ます。

```{figure} ../_static/windows_device_manager.png
:name: fig-windows-device-manager
:width: 100%

デバイスマネージャーでの見え方
```

ここで戸惑いやすいのが名前です。**`Arduino UNO R4 WiFi` とは表示されません。**
Windows 標準の USB CDC ドライバで動くので `USB シリアル デバイス (COMn)` に
なります。Arduino IDE を入れてもこの表示は変わりません。

見分ける手がかりは `Hardware ID` の **`VID:PID=2341:1002`** です。`2341` が
Arduino のベンダ ID で、複数の USB シリアル機器をつないでいるときはこれで
判別します（6 節でこの値を使います）。

## 3. ビルドして書き込む

`-d` に章のディレクトリを渡します。

```powershell
uv run pio run -d 05_shell -t upload
```

```text
Configuring upload protocol...
AVAILABLE: cmsis-dap, jlink, sam-ba
CURRENT: upload_protocol = sam-ba
Looking for upload port...
Auto-detected: COM3
Forcing reset using 1200bps open/close on port COM3
Uploading .pio\build\uno_r4_wifi\firmware.bin
Erase flash

Done in 0.000 seconds
Write 41200 bytes to flash (11 pages)

[==============================] 100% (11/11 pages)
Done in 2.803 seconds
========================= [SUCCESS] Took 7.23 seconds =========================
```

`Auto-detected: COM3` のとおり、ふつうはポートを指定しなくても見つかります。
ほかに USB シリアル機器がつながっていて誤検出されるときだけ
`--upload-port COM3` を足してください。

## 4. シリアルモニタで見る

```powershell
uv run pio device monitor -b 115200
```

```text
--- Terminal on COM3 | 115200 8-N-1
--- Available filters and text transformations: debug, default, direct, hexlify, log2file, nocontrol, printable, send_on_enter, time
--- More details at https://bit.ly/pio-monitor-filters
--- Quit: Ctrl+C | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H
```

抜けるときは `Ctrl-C` です。

```{important}
**この 4 行のあとに何も出なくても故障ではありません。**

UNO R4 WiFi は、**シリアルポートを開いてもリセットされません**。USB の
シリアル通信はボード上の ESP32-S3 が受け持っていて、プログラムが動いている
RA4M1 とは独立しているためです。多くの Arduino 互換ボードのように
「モニタを開いた瞬間にプログラムが最初から走り直す」ことはありません。

そのため `setup()` の中でしか出力しない章では、モニタを開いても
**起動時のバナーはすでに流れ終わっています**。バナーを見たいときは、
書き込み直後にモニタを開くか、RESET ボタンを 1 回押してください。
第5章のシェルなら `reboot` と打っても同じことができます。
```

## 5. Windows でつまずくところ

### シリアルモニタを開いたままだと書き込めない

Windows ではシリアルポートを 1 つのプロセスが排他的に握ります。モニタを
開いたまま `upload` すると、こうなります。

```text
Looking for upload port...
Auto-detected: COM3
*** [upload] could not open port 'COM3': PermissionError(13, 'アクセスが拒否されました。', None, 5)
========================== [FAILED] Took 0.94 seconds ==========================
```

末尾の `5` は Windows のエラーコード `ERROR_ACCESS_DENIED` です（メッセージは
OS の言語で変わります）。Linux の `Device or resource busy` にあたります。
**モニタを `Ctrl-C` で閉じてから**書き込み直してください。

同じことは Arduino IDE のシリアルモニタや、自分で書いた Python スクリプトが
ポートを掴んでいるときにも起きます。**COM ポートを開けるのは、同時に 1 つだけ**です。

### COM 番号が違う

存在しないポートを指定すると、別のエラーになります。

```text
Looking for upload port...
Using manually specified: COM9
*** [upload] could not open port 'COM9': FileNotFoundError(2, '指定されたファイルが見つかりません。', None, 2)
========================== [FAILED] Took 0.94 seconds ==========================
```

`FileNotFoundError` はポート番号の間違い、`PermissionError` は使用中、と
覚えておくと切り分けが早くなります。`uv run pio device list` で確認してください。

### `No device found on COMn` で止まる

ブートローダに入れていないときの症状です。**RESET ボタンを素早く 2 回押す**と
ブートローダに落ちます（L の LED がゆっくり明滅すれば成功）。そのまま
もう一度 `upload` してください。

デバッガ（CMSIS-DAP / VS Code のデバッグ）で CPU を停止させた直後は、
書き込み時の 1200bps リセットが効かずにこの状態になることがあります。

### そのほか

- **USB ハブ経由ではなく、PC 本体に直挿し**してください。ハブ経由だと
  書き込みに失敗することがあります
- ケーブルがデータ通信対応か確認してください（充電専用ケーブルでは
  ポートが出てきません）

## 6. Python からボードと通信する

シリアルモニタの代わりに Python から話しかけると、出力を保存したり、
応答を見て次のコマンドを送ったりできます。第13章の四脚ロボットも、この
やりかたで PC 側から動かします。

使うのは [pyserial](https://pyserial.readthedocs.io/) です
（`uv sync` 済みなら入っています）。

### 最小の例

第5章（`05_shell`）を書き込んだ状態で実行します。

```python
import sys
import time

import serial

ser = serial.Serial("COM3", 115200, timeout=0.2)
time.sleep(1.0)
ser.reset_input_buffer()

for cmd in (b"help\n", b"info\n"):
    ser.write(cmd)
    time.sleep(0.6)
    text = ser.read(8192).decode("utf-8", "replace")
    sys.stdout.write(text.replace("\r\n", "\n"))

ser.close()
```

```powershell
uv run python hello_serial.py
```

```text
help
Available commands:
  ps      - List all tasks
  kill N  - Suspend task N
  exec N  - Resume task N
  info    - System information
  reboot  - Reboot system
  help    - Show this help
> info

=== System Information ===
System Ticks:  67770
Uptime:        67 s
Task Count:    5
Time Slice:    10 ms

>
```

`ps` を送れば、そのままタスク表が返ってきます。

```text
ID  NAME           STATE      CPU%
--  ----           -----      ----
0   idle           READY     100%
1   LED1           BLOCKED   0%
2   LED2           BLOCKED   0%
3   Heartbeat      BLOCKED   0%
4   Shell          RUNNING   0%
```

### ポート番号を書かずに済ませる

`COM3` を直接書くと、別の PC やポートが変わった途端に動かなくなります。
Arduino のベンダ ID（`0x2341`）で探せば、Windows でも Linux でも macOS でも
同じコードが動きます。

```python
import serial.tools.list_ports

ARDUINO_VID = 0x2341


def find_board():
    """Arduino のポート名を返す。Windows なら COM3、Linux なら /dev/ttyACM0。"""
    for port in serial.tools.list_ports.comports():
        if port.vid == ARDUINO_VID:
            return port.device
    raise RuntimeError("ボードが見つかりません")


print(find_board())
```

```text
COM3
```

`comports()` は Windows ではレジストリを、Linux では `/sys` を見ます。
返る名前だけが違い、呼びかたは同じです。

### 覚えておくと詰まらない 3 つ

**改行が二重になる。**
ボードは行末に `CRLF` を送ってきます。それをそのまま `print` すると、
Windows では `\n` がもう一度 `\r\n` に変換されて行間が開きます。
上の例のように `text.replace("\r\n", "\n")` を通してから出力してください。

**ポートは同時に 1 つしか開けない。**
シリアルモニタ・Arduino IDE・自分のスクリプトのうち、**開けるのはどれか 1 つ**
です。スクリプトが `PermissionError` を出したら、まずモニタを閉じてください。

**ポートを開いてもボードは再起動しない。**
4 節のとおりです。`Serial()` を開いた直後に `setup()` の出力を待っても、
いつまでも来ません。起動時の出力が見たいときは、書き込んだ直後にポートを
開いてください。UNO R4 WiFi は書き込みの前後で COM ポートが消えないので、
`upload` の直後にすぐ開けば起動メッセージから受け取れます。

```text
=== Interactive Shell Demo ===

Tasks created. Starting OS...


Mini OS Shell
Type 'help' for commands.
>
```

## 7. 四脚ロボットを PC から動かす

第13章の四脚ロボットは、マイコンに焼く前に PC から直接サーボを叩いて
立ち上げるのが早道です。そのツールが
[`code/13_quadruped/host/`](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/13_quadruped/host)
にあります。Windows でもそのまま動きます。

```powershell
cd code\13_quadruped\host
uv run python quad_host.py --port COM3 scan        # バスに何個いるか
uv run python quad_host.py --port COM3 calibrate   # sign と zero を測る -> calib.json
uv run python quad_host.py --port COM3 stand       # home 姿勢を保持
uv run python quad_host.py --port COM3 teleop      # w/s/a/d で歩かせる
```

`--port` に渡すのは **サーボバスの USB シリアルアダプタ**の COM 番号です。
Arduino をブリッジとして使う場合（`--bus bridge`）は Arduino の COM 番号に
なります。省略すると `calib.json` に記録されたポート、それも無ければ
接続されている USB シリアル機器を順に探します。

`teleop` はキーを 1 つずつ読むので、**PowerShell の窓から直接**実行して
ください。`Ctrl-C` でサーボのトルクが抜けます。

```{warning}
サーボ 8 個の電源は必ずバッテリーから取ってください。PC の USB からは
絶対に取らないでください（1 個あたりストール 2.7 A）。
組み立てと安全上の注意は[四脚ロボットを歩かせる](../hardware/walk.md)にあります。
```

## 8. 全章をまとめて確認する

同梱のスクリプトで、全章のビルド・書き込み・出力の突き合わせを一度に
実行できます。

```powershell
cd code
uv run python scripts\verify_chapters.py --port COM3
```

```text
OS: Windows 11  Python: 3.12.12
ボード: COM3

=== 01_boot =====================================================
  -> PASS  (15.5s)
     OK  === Boot Sequence Check ===
     OK  BSS がゼロクリアされている
     OK  DATA が Flash からコピーされている
     OK  ベクタテーブルが RAM 上にある
     OK  If you see this, boot sequence completed!

=== 05_shell ====================================================
  -> PASS  (19.7s)
     OK  Available commands:
     OK  ID\s+NAME\s+STATE\s+CPU%
     OK  idle タスクが ID 0 で並ぶ
     OK  CPU% の合計 = 99%（5 タスク）
```

`--only` で章を絞れます（上の例は `--only 01_boot 05_shell`）。
`--build-only` を付ければボード無しでビルドだけ確かめられます。
オプションの一覧と対話モードは[全章の動作確認](../chapters/verify.md)を
参照してください。
