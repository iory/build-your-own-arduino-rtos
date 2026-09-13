# 準備するもの

## 必須

| 品目 | 数量 | 備考 |
|---|---|---|
| Arduino UNO R4 **WiFi** | 1 | Minima ではなく WiFi 版（LED マトリクス搭載） |
| USB-C ケーブル | 1 | データ通信対応のもの |
| PC | 1 | Windows / macOS / Linux いずれも可 |

```{warning}
UNO R4 には **Minima** と **WiFi** の 2 種類があります。本書で使うのは
LED マトリクスを搭載した **WiFi 版**です。購入時にご注意ください。
```

```{figure} ../_static/uno_r4_wifi_os.jpg
:name: fig-materials-uno-r4-wifi
:width: 80%

Arduino UNO R4 WiFi。基板の右下にある 12×8 の LED マトリクスが WiFi 版の目印です
（写真は LED マトリクスに「OS」と表示したところ）
```

### Arduino UNO R4 WiFi の購入先

型番は **ABX00087** です。価格は税込で、2026 年 9 月 14 日時点のものです。

| 購入先 | 価格 | 備考 |
|---|---|---|
| [秋月電子通商](https://akizukidenshi.com/catalog/g/g118246/) | ¥4,850 | |
| [DigiKey](https://www.digikey.jp/ja/products/detail/arduino/ABX00087/20371539) | ¥5,033 | |
| [共立エレショップ](https://eleshop.jp/shop/g/gNBA313/) | ¥5,060 | |
| [RS コンポーネンツ](https://jp.rs-online.com/web/p/arduino/2662937) | ¥5,173 | |
| [マルツ](https://www.marutsu.co.jp/pc/i/2773981/) | ¥5,322 | |
| [千石電商](https://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-6864) | ¥5,400 | 秋葉原・大阪の店頭にもあり |
| [スイッチサイエンス](https://www.switch-science.com/products/9090) | ¥5,500 | |
| [Amazon](https://www.amazon.co.jp/dp/B0C8V88Z9D) | ¥5,639 | 出品者によって価格が変わる |
| [Arduino 公式ストア](https://store.arduino.cc/products/uno-r4-wifi) | €30.50 | 海外のストア |

Amazon などには、形の似た**互換ボード**も並んでいます。本書のサンプルコードは
Arduino 純正の UNO R4 WiFi で動作確認しているので、ブランドが Arduino で
型番が ABX00087 のものを選んでください。

## ボードのピン配置

配線する章（第9章・第12章のサーボと可変抵抗、第13章のサーボドライバーボード）で
ピンの位置を確かめるときに使ってください。基板の **L LED** は `LED_BUILTIN`
（D13 / P102）、シリアルの `D0/RX`・`D1/TX` は P301・P302 です。

```{figure} ../_static/uno_r4_wifi_pinout.png
:name: fig-uno-r4-wifi-pinout
:width: 100%

Arduino UNO R4 WiFi のピン配置図。
出典: Arduino,
[ABX00087 Full Pinout](https://docs.arduino.cc/resources/pinouts/ABX00087-full-pinout.pdf)
（1 ページ目から凡例を除いて切り抜き）。
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```

## ボードのブロック図

USB-C はアナログスイッチを通って RA4M1 と ESP32-S3 のどちらかにつながり、
LED マトリクスは RA4M1 のピン 11 本に直接つながっています。

```{figure} ../_static/uno_r4_wifi_block_diagram.png
:name: fig-uno-r4-wifi-block-diagram
:width: 100%

Arduino UNO R4 WiFi のブロック図。
出典: Arduino,
[ABX00087 Datasheet](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf)
「3 Block Diagram」。
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```

## 第13章（四脚ロボット）で追加で使うもの

部品表と組み立ては [四脚ロボットの組み立て](../hardware/index.md) を
参照してください。第12章までは本体とケーブルだけで進められます。
