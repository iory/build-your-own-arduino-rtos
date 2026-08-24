# 『つくりながら学ぶ！リアルタイムOS自作入門』サポートページ

Arduino UNO R4 WiFi の上で、プリエンプティブなリアルタイム OS を
一から自作する書籍のサポートページです。開発環境の準備、章ごとの
サンプルコードと動作確認、四脚ロボットの組み立て、正誤表をまとめています。

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} 🚀 はじめに
:link: getting-started/index
:link-type: doc
準備するものと開発環境（Arduino IDE / PlatformIO）のセットアップ。
:::

:::{grid-item-card} 📖 章ごとのサポート
:link: chapters/index
:link-type: doc
各章のサンプルコード・ビルド方法・つまずきやすいポイント。
:::

:::{grid-item-card} 🤖 四脚ロボットの組み立て
:link: hardware/index
:link-type: doc
第13章で使う四脚ロボットのハードウェア準備と組立ガイド。
:::

:::{grid-item-card} ❓ FAQ / 正誤表
:link: faq
:link-type: doc
よくあるトラブルと修正情報。
:::
::::

## 書籍について

- 対象ボード: **Arduino UNO R4 WiFi**（Renesas RA4M1 / Arm Cortex-M4）
- 本編 13 章＋応用編 4 章。ブートシーケンスから始めて、
  コンテキストスイッチ・プリエンプティブスケジューラ・メモリ保護・
  シェル・インタプリタを積み上げ、最後は自作 OS で四脚ロボットを歩かせます
- 書誌情報・購入リンクは出版後にここに掲載します

```{toctree}
:hidden:
getting-started/index
chapters/index
hardware/index
faq
errata
```
