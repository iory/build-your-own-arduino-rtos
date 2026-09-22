# Getting started with the Arduino IDE

The Arduino IDE is the quickest way to check that the board works.

1. Open the [Arduino IDE download page](https://www.arduino.cc/en/software), pick
   the build for your OS from the drop-down, press **DOWNLOAD** and install it.

   ```{figure} ../_static/arduino_ide_download.png
   :name: fig-arduino-ide-download
   :width: 100%

   The Arduino IDE download page (Arduino IDE 2.3.10, as of September 2026).
   Source: [arduino.cc/en/software](https://www.arduino.cc/en/software)
   ```

   | OS | What to pick |
   |---|---|
   | Windows | `Windows Win 10 or newer (64-bit)` |
   | macOS (Apple M series) | `macOS Apple Silicon 12 Monterey or newer (64-bit)` |
   | macOS (Intel) | `macOS Intel 12 Monterey or newer (64-bit)` |
   | Linux (x86-64) | `Linux AppImage (64-bit X86-64)` |

   To see which chip your Mac has, open the Apple menu → "About This Mac". "Chip:
   Apple M…" means Apple Silicon; "Processor: … Intel" means Intel.
2. In the Boards Manager, add **Arduino UNO R4 Boards**.
3. Select **Arduino UNO R4 WiFi** as the board and the connected port as the port.
4. Upload `File → Examples → 01.Basics → Blink`. If the LED blinks, you are ready.

```{note}
The book's standard environment is **PlatformIO** (next page). The Arduino IDE is
used to check that the board talks to your computer and in the introduction of
the first part of the book.
```
