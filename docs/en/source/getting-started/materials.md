# What You Need

| Item | Qty | Notes |
|---|---|---|
| Arduino UNO R4 **WiFi** | 1 | The WiFi variant (with the LED matrix), not the Minima |
| USB-C cable | 1 | Must support data |
| A computer | 1 | Windows / macOS / Linux |

```{warning}
There are two UNO R4 variants; this book uses the **WiFi** one.
```

```{figure} ../_static/uno_r4_minima_vs_wifi.png
:name: fig-materials-minima-vs-wifi
:width: 90%

Left: Minima. Right: WiFi. Only the WiFi board has the 12×8 LED matrix (bottom right)
and the ESP32-S3 Wi-Fi module (the large square on the left).
Source: Arduino, product images on docs.arduino.cc
([UNO R4 Minima](https://github.com/arduino/docs-content/blob/dab66ecbd6ad52cd742da6c19c5b6330a7f2caae/content/hardware/uno/boards/uno-r4-minima/image.svg) / [UNO R4 WiFi](https://github.com/arduino/docs-content/blob/dab66ecbd6ad52cd742da6c19c5b6330a7f2caae/content/hardware/uno/boards/uno-r4-wifi/image.svg)), placed side by side and labelled.
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```

```{figure} ../_static/uno_r4_wifi_os.jpg
:name: fig-materials-uno-r4-wifi
:width: 80%

The Arduino UNO R4 WiFi. The 12×8 LED matrix at the lower right of the board
marks the WiFi variant (shown here displaying "OS")
```

## Where to buy the Arduino UNO R4 WiFi

The part number is **ABX00087**. Prices include tax and are as of 2026-09-14.

| Store | Price | Notes |
|---|---|---|
| [Arduino Official Store](https://store.arduino.cc/products/uno-r4-wifi) | €30.50 | |
| [DigiKey (Japan)](https://www.digikey.jp/ja/products/detail/arduino/ABX00087/20371539) | ¥5,033 | |
| [RS Components (Japan)](https://jp.rs-online.com/web/p/arduino/2662937) | ¥5,173 | |
| [Akizuki Denshi](https://akizukidenshi.com/catalog/g/g118246/) | ¥4,850 | Japan |
| [Kyoritsu Eleshop](https://eleshop.jp/shop/g/gNBA313/) | ¥5,060 | Japan |
| [Marutsu](https://www.marutsu.co.jp/pc/i/2773981/) | ¥5,322 | Japan |
| [Sengoku Densho](https://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-6864) | ¥5,400 | Japan; also in the Akihabara and Osaka stores |
| [Switch Science](https://www.switch-science.com/products/9090) | ¥5,500 | Japan |
| [Amazon.co.jp](https://www.amazon.co.jp/dp/B0C8V88Z9D) | ¥5,639 | Price depends on the seller |

Look-alike **compatible boards** are also sold (especially on Amazon). The
sample code was tested on the genuine Arduino UNO R4 WiFi, so pick one whose
brand is Arduino and whose part number is ABX00087.

## Board pinout

Use this when wiring (the servos and potentiometer in Chapters 9 and 12, the
servo driver board in Chapter 13). The on-board **L LED** is `LED_BUILTIN`
(D13 / P102); serial `D0/RX` and `D1/TX` are P301 and P302.

```{figure} ../_static/uno_r4_wifi_pinout.png
:name: fig-uno-r4-wifi-pinout
:width: 100%

Arduino UNO R4 WiFi pinout.
Source: Arduino,
[ABX00087 Full Pinout](https://docs.arduino.cc/resources/pinouts/ABX00087-full-pinout.pdf)
(page 1, cropped to omit the legend).
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```

## Board block diagram

USB-C goes through analog switches to either the RA4M1 or the ESP32-S3, and
the LED matrix is wired directly to 11 pins of the RA4M1.

```{figure} ../_static/uno_r4_wifi_block_diagram.png
:name: fig-uno-r4-wifi-block-diagram
:width: 100%

Arduino UNO R4 WiFi block diagram.
Source: Arduino,
[ABX00087 Datasheet](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf),
"3 Block Diagram".
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```
