---
og:description: Arduino UNO R4 WiFi でプリエンプティブなリアルタイム OS を一から自作する書籍『つくりながら学ぶ！リアルタイムOS自作入門』のサポートページ。開発環境の準備、章ごとのサンプルコード、四脚ロボットの組み立て、正誤表。
---

# 『つくりながら学ぶ！リアルタイムOS自作入門』サポートページ

Arduino UNO R4 WiFi の上で、プリエンプティブなリアルタイム OS を
一から自作する書籍のサポートページです。開発環境の準備、章ごとの
サンプルコードと動作確認、四脚ロボットの組み立て、正誤表をまとめています。

```{raw} html
<video src="_static/promo.mp4" poster="_static/og_image.png" controls muted playsinline loop preload="metadata"
       style="width:100%; border-radius:8px;"
       aria-label="書籍の紹介動画: 自作 OS の起動から四脚ロボットの歩行まで"></video>
```

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} 🚀 はじめに
:link: getting-started/index
:link-type: doc
準備するものと開発環境（Arduino IDE / PlatformIO）のセットアップ。
:::

:::{grid-item-card} 💻 実機がなくても試せる
:link: getting-started/simulator
:link-type: doc
基板が手元になくても、実機と同じファームウェアを PC 上で動かせます。
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

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item}
:columns: 12 12 4 4
```{image} _static/book_cover.jpg
:alt: 『つくりながら学ぶ！リアルタイムOS自作入門』の表紙
:width: 240px
:align: center
:target: https://book.mynavi.jp/ec/products/detail/id=152331
```
:::

:::{grid-item}
:columns: 12 12 8 8
- 対象ボード: **Arduino UNO R4 WiFi**（Renesas RA4M1 / Arm Cortex-M4）
- 本編 13 章＋応用編 4 章。ブートシーケンスから始めて、
  コンテキストスイッチ・プリエンプティブスケジューラ・メモリ保護・
  シェル・インタプリタを積み上げ、最後は自作 OS で四脚ロボットを歩かせます

**購入する**

{bdg-link-primary}`マイナビブックス（紙・PDF）<https://book.mynavi.jp/ec/products/detail/id=152331>`
{bdg-link-primary}`Amazon<https://www.amazon.co.jp/dp/4839991871>`
{bdg-link-primary}`楽天ブックス<https://books.rakuten.co.jp/rb/18716697/>`
{bdg-link-primary}`honto（電子書籍）<https://honto.jp/isbn/9784839991876>`

全国の書店でも ISBN（978-4-8399-9187-6）で注文できます。
:::
::::

### 書誌情報

| | |
|---|---|
| 書名 | つくりながら学ぶ！リアルタイムOS自作入門（Compass Books シリーズ） |
| 著者 | 矢野倉伊織 |
| 出版社 | マイナビ出版 |
| 発売日 | 2026年9月18日 |
| ISBN | 978-4-8399-9187-6 |
| 形態 | 書籍（紙）／電子版（PDF） |

```{toctree}
:hidden:
getting-started/index
chapters/index
hardware/index
faq
errata
```
