# PlatformIO で動かす（本書の標準環境）

サンプルコードは章ごとの PlatformIO プロジェクトとして提供します。
PlatformIO は、コマンドラインでビルドと書き込みができる組み込み開発の道具で、VS Code の拡張としても使えます。

Arduino IDE ではなく PlatformIO を本書の標準にしているのは、ボードやビルドの設定が
章ごとの `platformio.ini` というテキストファイルに残り、コードと一緒に Git で
バージョン管理できるからです。PlatformIO 本体のバージョンも `uv.lock` で固定して
います。Arduino IDE はボードの設定を IDE 全体で持つので、IDE やボードパッケージを
更新したときに、それまで動いていたサンプルが動かなくなるおそれがあります。

## インストール

```bash
# uv を使う場合（推奨）
uv tool install platformio

# pip の場合
pipx install platformio
```

OS 別のページ（{doc}`windows`・{doc}`linux`・{doc}`macos`）では、
サンプルコードのフォルダで `uv sync` を実行して PlatformIO を入れ、`uv run pio` として呼びます。
ここに示したインストールは、`uv run` を付けずに `pio` とだけ打って使いたい場合にだけ必要です。

VS Code を使う場合は拡張機能 **PlatformIO IDE** を入れると
ビルド・書き込み・シリアルモニタが GUI から使えます。

## ビルドと書き込み

```bash
pio run -d <章のディレクトリ> -t upload   # ビルドして書き込み
pio device monitor -b 115200              # シリアルモニタ
```

`-b 115200` はボーレート（通信速度。スケッチの `Serial.begin(115200)` と揃える）です。

## 動作確認

サンプルコード一式の入手方法は [章ごとのサポート](../chapters/index.md)
を参照してください。
このあとの OS 別のページでも、`git clone` で取ってくる手順から説明しています。
入手したら、`docs/os-on-arduino/code/` で環境確認用のスケッチを書き込みます。

```bash
pio run -d 00_intro -t upload
pio device monitor -b 115200
```

シリアルモニタに `Environment OK! Ready to start.` と `Loop count:` が出て、
LED マトリクスに「OS」が表示されれば準備完了です。

```{figure} ../_static/uno_r4_wifi_os.jpg
:name: fig-platformio-os
:width: 80%

`00_intro` を書き込んだところ。LED マトリクスに「OS」が出ています
```

```{note}
このスケッチは PC からシリアルモニタが開かれるまで待ち、開かれてから
「OS」を表示します。書き込んだだけではマトリクスは消えたままなので、
シリアルモニタを開いてください。
```
