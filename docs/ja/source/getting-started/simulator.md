# 付録: 実機がなくても試せる

Arduino UNO R4 WiFi が手元に無くても、**実機と同じファームウェアを PC の中で
動かして**本書を読み進められます。LED マトリクスと内蔵 LED はブラウザ上の
基板写真に重ねて表示され、シェルもそのまま使えます。

```
pio run -e sim   →   firmware.elf   →   Renode (RA4M1)   →   ブラウザ
  （いつもの        （実機に書くものと      （実機と同じ        （基板の上で
    ビルド）          同じ ELF）            Cortex-M4）         LED が光る）
```

サンプルコードは 1 行も変えません。実機向けのビルドとの違いは、Arduino コア
公式のフラグ `-D NO_USB` を足すことだけです（理由は後述）。

:::{note}
本書のカーネルが使うのは SysTick・PendSV・NVIC・MPU といった Cortex-M の
標準機能です。エミュレータ上でもこれらは実機と同じように動きます。
:::

## 必要なもの

| | 入手先 |
| --- | --- |
| **Renode** 1.17 以降 | <https://github.com/renode/renode/releases> |
| **Python** 3.10 以降 | 標準ライブラリのみ使用（`pip install` は不要） |
| **PlatformIO** | {doc}`platformio` と同じもの |

### Renode のインストール

::::{tab-set}
:::{tab-item} macOS
```bash
brew trust renode/tap
brew install renode/tap/renode
```
最近の Homebrew は、公式以外の tap を既定では信用しません。`brew trust` を
先に実行しないと、ボトルを全部ダウンロードした後に
`Refusing to load formula renode/tap/renode-nightly from untrusted tap` で
止まります。

Homebrew を使わない場合は、リリースページの `renode-*.osx-arm64-portable.dmg`
（Apple Silicon）を開いて `Renode.app` を Applications へ入れます。その場合は
コマンドラインからは
`/Applications/Renode.app/Contents/MacOS/renode` で呼び出します。
:::
:::{tab-item} Windows
リリースページの `renode-*.setup.exe` を実行します。インストーラで PATH に
追加しておくと、以降 `renode` と打つだけで動きます。管理者権限を使いたく
ない場合は `renode-*.windows-portable.zip` を展開して、中の `Renode.exe` を
`--renode` で直接指定しても構いません。

Renode が配布しているのは x64 版だけですが、**Windows on ARM
（Snapdragon X など）でも x64 エミュレーション経由で動く**ことを確認しています。
:::
:::{tab-item} Linux
`renode_*_amd64.deb` / `renode-*.x86_64.rpm` をパッケージマネージャで入れるか、
`renode-*.linux-portable.tar.gz` を展開して PATH に足します。

portable 版は .NET を内蔵しているので、mono や dotnet を別途入れる必要は
ありません。GUI は使わないので、`DISPLAY` の無い環境（SSH 越しなど）でも
そのまま動きます。
:::
::::

## 動かす

```bash
cd code/04_scheduler
pio run -e sim                       # シミュレータ用にビルド
python3 ../sim/board.py --chapter .  # 仮想ボードを起動
```

`http://localhost:8080` を開くと基板が表示されます。終了は Ctrl-C です。
Windows では `python3` ではなく `python` と打ってください。

Renode が PATH に無いときは場所を渡してください。

```bash
python3 ../sim/board.py --chapter . \
    --renode /Applications/Renode.app/Contents/MacOS/renode
```

## 画面の見かた

- **12×8 LED マトリクス** — `Arduino_LED_Matrix` が実機で走査しているフレーム
  バッファ（12 バイト）をそのまま読んで光らせています
- **L (D13)** — ポートレジスタ `PCNTR1` の出力ビットを読んでいます
- **シリアルモニタ** — 双方向です。入力欄にコマンドを打てば、第5章以降の
  シェルや第11章の TinyPython がそのまま使えます

第1章は実機と同じく起動時に `S` の入力を待ちます。入力欄に `S` と打って
ください。

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
  Renode の RA4M1 モデルには USB が実装されていないため、`-D NO_USB` で
  `Serial` をハードウェア UART に切り替えています。UNO R4 WiFi の `Serial` が
  USB CDC であること自体は本書で扱う話題なので、そこは実機で確かめてください。
- **SCI チャネルの番号がずれます**
  Renode のプラットフォーム定義は UNO R4 **Minima** のものなので、ピンと
  SCI の対応が実機と異なります。出力は `sci9` に出ます（実機の D0/D1 は SCI2）。
- **ESP32 / Wi-Fi はありません**
  UNO R4 WiFi のもう 1 つのチップは載っていません。
- **割り込みのジッタは本物ではありません**
  タスク切り替えの周期や CPU 使用率の傾向は追えますが、リアルタイム性の
  最終確認は実機で行ってください。
- **第6章のフォールトは起きません**
  Renode は `CCR.DIV_0_TRP` を実装していないためゼロ除算で UsageFault に
  ならず、未マップ領域への書き込みでも BusFault を上げません。どちらも
  タスクはそのまま終了するので、「壊れたタスクだけが死んで他は動き続ける」
  という第6章の主張は観察できますが、`FAULT DETECTED` の表示と原因の特定は
  実機でしか見られません。

:::{note}
動作確認は **macOS (Apple Silicon)**・**Windows 11 (ARM64)**・
**Ubuntu 24.04 (x86_64)** で行っています。うまくいかない場合は
[Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
で教えてください。
:::

## うまくいかないとき

**「ファームウェアが見つかりません」と出る**

`pio run -e sim` を実行しましたか。実機向けの `pio run` だけでは、
エミュレータ用のビルド（`.pio/build/sim/firmware.elf`）ができません。

**「Renode の Monitor につながらない」と出る**

`renode` が PATH にあるか確認してください。`--renode` で実行ファイルを
直接指定することもできます。

**シリアルに何も出てこない**

章によっては入力待ちで止まっています（第1章は `S`、第5章以降はシェルの
プロンプト）。それでも出てこない場合は、`--uart sci2` のように出力先の
チャネルを変えて試してください。

**ポートが使用中**

`--http-port` / `--monitor-port` / `--uart-port` で番号を変えられます。

## 章の確認を自動で走らせる

本書の検証スクリプトは、実機の代わりにエミュレータでも走ります。
期待値は本文の「期待される出力」から起こしたものと同じです。

```bash
cd code
uv run python scripts/verify_chapters.py --sim
uv run python scripts/verify_chapters.py --sim --only 05_shell
```

エミュレータでは再現しない項目（第6章のフォールトなど）は `SKIP` と
理由が表示されます。

`code/sim/record.py` を使うと、基板の光り方をそのまま GIF に録れます。

## 仕組みを知りたい

`code/sim/README.md` に、どのアドレスから何を読んでいるか、ブラウザへ
どう流しているかを書いています。仮想ボード本体（`board.py` と
`board.html`）は 600 行ほどです。
