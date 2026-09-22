# 付録: 実機がなくても試せる

Arduino UNO R4 WiFi が手元に無くても、**実機と同じファームウェアを PC の中で
動かして**本書を読み進められます。LED マトリクスと内蔵 LED はブラウザ上の
基板写真に重ねて表示され、シェルもそのまま使えます。

```
pio run -e sim   →   firmware.elf   →   QEMU (RA4M1)   →   ブラウザ
  （いつもの        （実機に書くものと     （実機と同じ        （基板の上で
    ビルド）          同じ ELF）           Cortex-M4）         LED が光る）
```

サンプルコードは 1 行も変えません。実機向けのビルドとの違いは、Arduino コア
公式のフラグ `-D NO_USB` を足すことだけです（理由は後述）。

:::{tip}
**インストールなしで、まずブラウザで試せます。** 各章のファームウェアを
ブラウザの中の QEMU（WebAssembly 版）で動かすページを用意しました。
PC に何も入れずに、LED の点滅やシェルを触れます。

<a class="sd-btn sd-btn-primary" href="../sim/index.html">ブラウザで動かす</a>

ブラウザ版の QEMU は命令をインタプリタで実行するため、タイマや点滅は実時間
どおりですが、重い計算は実機より遅くなります。本文の出力と細かく比べるときは、
以下の手順で PC に入れたものか実機を使ってください。
:::

:::{note}
本書のカーネルが使うのは SysTick・PendSV・NVIC・MPU といった Cortex-M の
標準機能です。エミュレータ上でもこれらは実機と同じように動き、第6章の
フォールト（ゼロ除算・不正アドレス）も本文どおりに起きます。
:::

## 必要なもの

| | 入手先 |
| --- | --- |
| **QEMU**（UNO R4 対応版） | <https://github.com/iory/qemu-arduino-uno-r4/releases> |
| **Python** 3.10 以降 | 標準ライブラリのみ使用（`pip install` は不要） |
| **PlatformIO** | {doc}`platformio` と同じもの |

本家の QEMU には UNO R4 のマイコン（Renesas RA4M1）が入っていないので、
それを足したものを本書用に配布しています。Homebrew や apt で入る
`qemu-system-arm` では動きません。

(install-qemu)=
### QEMU のインストール

リリースページから OS に合ったファイルを取ってきて、ホームの `qemu-unor4`
フォルダに展開するだけです。この場所に置けば、仮想ボードが自動で見つけます。

::::{tab-set}
:::{tab-item} macOS
Apple Silicon（macOS 14 以降）と Intel Mac（macOS 15 以降）に対応しています。

```bash
mkdir -p ~/qemu-unor4 && cd ~/qemu-unor4
arch=$(uname -m)   # arm64 か x86_64
curl -fLO "https://github.com/iory/qemu-arduino-uno-r4/releases/download/v11.1.1-unor4.5/qemu-arduino-uno-r4-v11.1.1-unor4.5-macos-$arch.tar.gz"
tar xzf qemu-arduino-uno-r4-*-macos-*.tar.gz --strip-components=1
~/qemu-unor4/bin/qemu-system-arm --version
```

必要なライブラリは同梱しているので、Homebrew は要りません。

ブラウザでダウンロードした場合は、macOS が「開発元を検証できない」として
起動を止めます。展開したフォルダで一度だけ次を実行してください。

```bash
xattr -dr com.apple.quarantine ~/qemu-unor4
```

macOS 15 に上げられない古い Intel Mac では、後述の Renode を使ってください。
:::
:::{tab-item} Windows
x64 版と ARM64 版（Snapdragon X など）があります。**Windows on ARM では
必ず ARM64 版を使ってください。** x64 版はエミュレーション経由では動きません。

PowerShell で:

```powershell
$arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'x86_64' }
$name = "qemu-arduino-uno-r4-v11.1.1-unor4.5-windows-$arch"
Invoke-WebRequest "https://github.com/iory/qemu-arduino-uno-r4/releases/download/v11.1.1-unor4.5/$name.zip" -OutFile "$name.zip"
Expand-Archive "$name.zip" -DestinationPath "$HOME\qemu-unor4"
& "$HOME\qemu-unor4\$name\bin\qemu-system-arm.exe" --version
```

必要な DLL は `bin` に同梱しています。
:::
:::{tab-item} Linux
x86_64 版と arm64 版があります（glibc 2.35 以降、Ubuntu 22.04 相当以降）。
ただし本書のビルドに使う PlatformIO のコンパイラが Linux arm64 向けには
配布されていないため、**章をビルドできるのは x86_64 だけ**です
（Raspberry Pi の 64 ビット OS なども同じです）。

```bash
mkdir -p ~/qemu-unor4 && cd ~/qemu-unor4
arch=$(uname -m); [ "$arch" = aarch64 ] && arch=arm64
curl -fLO "https://github.com/iory/qemu-arduino-uno-r4/releases/download/v11.1.1-unor4.5/qemu-arduino-uno-r4-v11.1.1-unor4.5-linux-$arch.tar.gz"
tar xzf qemu-arduino-uno-r4-*-linux-*.tar.gz --strip-components=1
~/qemu-unor4/bin/qemu-system-arm --version
```

使うライブラリは glib だけで、ほとんどのディストリビューションに最初から
入っています。無い場合は `sudo apt install libglib2.0-0` です。画面は使わない
ので、`DISPLAY` の無い環境（SSH 越しなど）でもそのまま動きます。
:::
::::

## 動かす

```bash
cd code/04_scheduler
pio run -e sim                       # シミュレータ用にビルド
python3 ../sim/board.py --chapter .  # 仮想ボードを起動
```

ブラウザで `http://127.0.0.1:8080` を開くと基板が表示されます。終了は Ctrl-C です。
（`localhost` でも開けますが、Windows では IPv6 を先に試すぶん表示が数秒遅れます）

```{figure} ../_static/sim_browser.jpg
:name: fig-sim-browser
:width: 80%

第7章のサンプルを動かし、シリアルモニタに `ps` と打ったところ。
上が基板、下がシリアルモニタです。
```

Windows では `python3` ではなく `python` と打ってください。

QEMU を `qemu-unor4` 以外の場所に置いた場合は、`--qemu` でその
`qemu-system-arm`（Windows は `qemu-system-arm.exe`）を指定するか、
環境変数 `QEMU` に場所を入れておいてください。

## 画面の見かた

- **12×8 LED マトリクス** — `Arduino_LED_Matrix` が実機で走査しているフレーム
  バッファ（12 バイト）をそのまま読んで光らせています
- **L (D13)** — ポートレジスタ `PCNTR1` の出力ビットを読んでいます
- **シリアルモニタ** — 双方向です。入力欄にコマンドを打てば、第5章以降の
  シェルや第11章の TinyPython がそのまま使えます

第1章は実機と同じく起動時に `S` の入力を待ちます。入力欄に `S` と打って
ください。

```{figure} ../_static/sim_d13.gif
:name: fig-sim-d13
:width: 80%

第2章のサンプルで、内蔵 LED「L」（D13）が点滅する様子（D13 のまわりを拡大）。
```

```{figure} ../_static/sim_matrix_kill.gif
:name: fig-sim-matrix
:width: 80%

第7章のサンプル。LED マトリクスの上半分が CPU 負荷のグラフ、下半分がタスクごとの
実行状態です。シリアルから `kill 3` で重い計算のタスク（Heavy）を止めると、
CPU 負荷のグラフが消えていきます。
```

## 章ごとの対応

| 章 | シミュレータ |
| --- | --- |
| 第0章〜第11章、応用編 1〜3 | ✅ 動きます |
| 第12章（ハードウェア） | ❌ センサ・アクチュエータの実物が必要です |
| 第13章（四脚ロボット） | ❌ サーボとロボット本体が必要です |
| 応用編 4（ファイルシステム） | ❌ Renesas FSP のフラッシュドライバが必要です |

## 実機との違い

ここだけは実機と違います。**本文の説明と食い違う場面があるので、
気づいたときはこの節を思い出してください。**

- **`Serial` が USB ではなく UART になります**
  エミュレータには USB が実装されていないため、`-D NO_USB` で `Serial` を
  ハードウェア UART（SCI9）に切り替えています。UNO R4 WiFi の `Serial` が
  USB CDC であること自体は本書で扱う話題なので、そこは実機で確かめてください。
- **ESP32 / Wi-Fi はありません**
  UNO R4 WiFi のもう 1 つのチップは載っていません。
- **時間の進み方は近似です**
  命令 1 つを 16 ns（≒ 48 MHz）として時間を進めています。タスク切り替えの
  周期や CPU 使用率の傾向は追えますが、命令ごとのサイクル数や割り込みの
  ジッタは本物ではありません。リアルタイム性の最終確認は実機で行ってください。
- **本書で使わない周辺回路はありません**
  タイマ（AGT）・シリアル（SCI）・GPIO・割り込みコントローラ以外
  （ADC、I²C、SPI、PWM 用のタイマなど）は入っていません。

:::{note}
動作確認は **macOS 26 (Apple Silicon)**・**Windows 11 (ARM64)**・
**Ubuntu 24.04 (x86_64)** で行っています。加えて GitHub Actions で、macOS
（Apple Silicon / Intel）・Windows（x64 / ARM64）・Ubuntu（x86_64）の
5 環境で、この付録の手順どおりに全章を毎週確かめています。うまくいかない場合は
[Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
で教えてください。
:::

## うまくいかないとき

**「ファームウェアが見つかりません」と出る**

`pio run -e sim` を実行しましたか。実機向けの `pio run` だけでは、
エミュレータ用のビルド（`.pio/build/sim/firmware.elf`）ができません。

**「arduino-uno-r4 マシン入りの qemu-system-arm が見つかりません」と出る**

探した場所と、それぞれがダメだった理由が一緒に表示されます。QEMU を
ホームの `qemu-unor4` に展開したか、`--qemu` が展開した `qemu-system-arm` を
指しているか確認してください。Homebrew や apt で入れた本家の QEMU では
動きません。
macOS で「開発元を検証できない」と出た場合は、上の `xattr` を実行してください。

**シリアルに何も出てこない**

章によっては入力待ちで止まっています（第1章は `S`、第5章以降はシェルの
プロンプト）。

**ポートが使用中**

`--http-port` / `--monitor-port` / `--uart-port` で番号を変えられます。

**PC が重い・ファンが回り続ける**

`board.py` を `kill -9` などで強制終了すると、QEMU だけが残って動き続ける
ことがあります（Ctrl-C や端末を閉じた場合は自動で止まります）。
macOS / Linux は `pkill -f qemu-system-arm`、Windows はタスクマネージャーで
`qemu-system-arm.exe` を終了してください。

## 章の確認を自動で走らせる

本書の検証スクリプトは、実機の代わりにエミュレータでも走ります。
期待値は本文の「期待される出力」から起こしたものと同じです。

```bash
cd code
uv run python scripts/verify_chapters.py --sim
uv run python scripts/verify_chapters.py --sim --only 05_shell
```

`code/sim/record.py` を使うと、基板の光り方をそのまま GIF に録れます。

## Renode を使う場合

QEMU の代わりに、オープンソースのエミュレータ [Renode](https://renode.io/)
（1.17 以降）でも同じ画面が動きます。macOS 15 に上げられない Intel Mac では
こちらを使ってください。
Renode は RA4M1 を最初から持っているので、公式のリリースをそのまま使えます。

- macOS: `brew trust renode/tap && brew install renode/tap/renode`
  （`brew trust` を先に実行しないと `untrusted tap` で止まります）
- Windows: `renode-*.setup.exe`（Windows on ARM でも x64 エミュレーションで動きます）
- Linux: `renode-*.linux-portable.tar.gz` を展開（.NET 同梱）

いずれも <https://github.com/renode/renode/releases> から入手できます。
起動するときは `--emulator renode` を付けます。

```bash
python3 ../sim/board.py --chapter . --emulator renode
python3 ../sim/board.py --chapter . --emulator renode --renode /path/to/renode  # PATH に無いとき
```

検証スクリプトも `--emulator renode` で Renode を使います。

QEMU との違いは、**第6章のフォールトが起きない**ことです。
Renode は `CCR.DIV_0_TRP` を実装していないためゼロ除算で UsageFault に
ならず、未マップ領域への書き込みでも BusFault を上げません。「壊れたタスク
だけが死んで他は動き続ける」ことは観察できますが、`FAULT DETECTED` の表示と
原因の特定は見られません（検証スクリプトでは `SKIP` になります）。

Renode が残って動き続けたときは `pkill -f Renode`（Windows は `Renode.exe` を終了）
で止めてください。

## 仕組みを知りたい

`code/sim/README.md` に、どのアドレスから何を読んでいるか、ブラウザへ
どう流しているかを書いています。仮想ボード本体（`board.py` と
`board.html`）は 600 行ほどです。QEMU 側の実装（RA4M1 の割り込み
コントローラ・SCI・AGT・GPIO）は
<https://github.com/iory/qemu-arduino-uno-r4> にあります。
