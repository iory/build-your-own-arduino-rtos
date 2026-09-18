# PlatformIO で動かす（本書の標準環境）

サンプルコードは章ごとの PlatformIO プロジェクトとして提供します。

## インストール

```bash
# uv を使う場合（推奨）
uv tool install platformio

# pip の場合
pipx install platformio
```

VS Code を使う場合は拡張機能 **PlatformIO IDE** を入れると
ビルド・書き込み・シリアルモニタが GUI から使えます。

## ビルドと書き込み

```bash
pio run -d <章のディレクトリ> -t upload   # ビルドして書き込み
pio device monitor -b 115200              # シリアルモニタ
```

## 動作確認

サンプルコード一式の入手方法は [章ごとのサポート](../chapters/index.md)
を参照してください。入手したら、`docs/os-on-arduino/code/` で環境確認用のスケッチを書き込みます。

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
