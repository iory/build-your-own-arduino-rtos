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
を参照してください。
