# Arduino IDE で動かす（入門編）

最初の動作確認は Arduino IDE が手軽です。

1. [Arduino IDE のダウンロードページ](https://www.arduino.cc/en/software) を開き、
   プルダウンから自分の OS に合うものを選んで **DOWNLOAD** を押し、インストールする

   ```{figure} ../_static/arduino_ide_download.png
   :name: fig-arduino-ide-download
   :width: 100%

   Arduino IDE のダウンロードページ（Arduino IDE 2.3.10、2026 年 9 月時点）。
   出典: [arduino.cc/en/software](https://www.arduino.cc/en/software)
   ```

   | OS | 選ぶもの |
   |---|---|
   | Windows | `Windows Win 10 or newer (64-bit)` |
   | macOS（Apple M シリーズ） | `macOS Apple Silicon 12 Monterey or newer (64-bit)` |
   | macOS（Intel） | `macOS Intel 12 Monterey or newer (64-bit)` |
   | Linux（x86-64） | `Linux AppImage (64-bit X86-64)` |

   Mac のチップは、アップルメニュー →「この Mac について」で確かめられます。
   「チップ」に Apple M… と出れば Apple Silicon、「プロセッサ」に Intel と
   出れば Intel です。
2. ボードマネージャで **Arduino UNO R4 Boards** を追加
3. ボードに **Arduino UNO R4 WiFi**、ポートに接続中のポートを選択
4. `ファイル → スケッチ例 → 01.Basics → Blink` を書き込み、
   LED が点滅すれば準備完了

```{note}
本書の標準環境は次ページの **PlatformIO** です。Arduino IDE は
ボードの疎通確認と、書籍前半の導入で使います。
```
