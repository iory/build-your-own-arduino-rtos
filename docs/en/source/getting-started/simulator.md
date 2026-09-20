# Appendix: Running Without the Board

You can follow the book without an Arduino UNO R4 WiFi on your desk. The
**same firmware you would flash to the board** runs on your PC instead, with
the 12×8 LED matrix and the built-in LED drawn on a photo of the board in your
browser. The shell works too.

```
pio run -e sim   →   firmware.elf   →   Renode (RA4M1)   →   browser
  (the usual        (the very ELF        (the same           (LEDs light up
   build)            you would flash)     Cortex-M4)          on the board)
```

Not a single line of the sample code changes. The only difference from the
build for real hardware is one extra flag, `-D NO_USB`, which comes from the
Arduino core itself (see below).

:::{note}
The kernel in this book only uses standard Cortex-M facilities — SysTick,
PendSV, NVIC, MPU. Those behave in the emulator exactly as they do on silicon.
:::

## What you need

| | Where to get it |
| --- | --- |
| **Renode** 1.17 or later | <https://github.com/renode/renode/releases> |
| **Python** 3.10 or later | Standard library only, no `pip install` needed |
| **PlatformIO** | The same one as in {doc}`platformio` |

### Installing Renode

::::{tab-set}
:::{tab-item} macOS
```bash
brew trust renode/tap
brew install renode/tap/renode
```
Recent Homebrew versions do not trust third-party taps by default. Without the
`brew trust` line, the install downloads every bottle and then stops with
`Refusing to load formula renode/tap/renode-nightly from untrusted tap`.

Without Homebrew, open `renode-*.osx-arm64-portable.dmg` (Apple Silicon) from
the releases page and move `Renode.app` into Applications. From the command
line it then lives at `/Applications/Renode.app/Contents/MacOS/renode`.
:::
:::{tab-item} Windows
Run `renode-*.setup.exe` from the releases page. Let the installer add Renode
to your PATH so that `renode` works from any shell. If you would rather not
use an installer, unpack `renode-*.windows-portable.zip` and point `--renode`
at the `Renode.exe` inside it.

Renode only ships x64 builds, but they have been confirmed to run on
**Windows on ARM (Snapdragon X and friends) through x64 emulation**.
:::
:::{tab-item} Linux
Install `renode_*_amd64.deb` or `renode-*.x86_64.rpm` with your package
manager, or unpack `renode-*.linux-portable.tar.gz` and add it to your PATH.

The portable tarball bundles its own .NET runtime, so there is nothing else to
install. Nothing here uses a GUI, so it also runs fine without `DISPLAY` (over
SSH, for instance).
:::
::::

## Running it

```bash
cd code/04_scheduler
pio run -e sim                       # build for the simulator
python3 ../sim/board.py --chapter .  # start the virtual board
```

Open `http://localhost:8080`. Stop it with Ctrl-C. On Windows, type `python`
instead of `python3`.

If Renode is not on your PATH, point at it directly:

```bash
python3 ../sim/board.py --chapter . \
    --renode /Applications/Renode.app/Contents/MacOS/renode
```

## What you are looking at

- **12×8 LED matrix** — read straight out of the framebuffer (12 bytes) that
  `Arduino_LED_Matrix` scans out on real hardware
- **L (D13)** — read from the output bit of the `PCNTR1` port register
- **Serial monitor** — bidirectional. Type into the input box and the shell
  (chapter 5 onwards) or TinyPython (chapter 11) responds as usual

Chapter 1 waits for an `S` at startup, exactly as on hardware. Type `S` into
the input box.

## Chapter coverage

| Chapter | Simulator |
| --- | --- |
| Chapters 0–11, Advanced 1–3 | ✅ Works |
| Chapter 12 (hardware) | ❌ Needs the real sensors and actuators |
| Chapter 13 (quadruped robot) | ❌ Needs servos and the robot |
| Advanced 4 (file system) | ❌ Needs the Renesas FSP flash driver |

## How it differs from real hardware

These are the places where the simulator and the book part ways. **When
something does not match the text, come back to this list.**

- **`Serial` is a hardware UART, not USB.**
  The Renode RA4M1 model has no USB, so `-D NO_USB` switches `Serial` over to
  a hardware UART. The fact that `Serial` on the UNO R4 WiFi is USB CDC is
  itself a topic in the book — confirm that part on real hardware.
- **SCI channel numbers are shifted.**
  Renode's platform description is for the UNO R4 **Minima**, so the pin to
  SCI mapping differs from the WiFi board. Output arrives on `sci9` (on real
  hardware, D0/D1 are SCI2).
- **No ESP32, no Wi-Fi.**
  The second chip on the UNO R4 WiFi is not modelled.
- **Interrupt jitter is not real.**
  Scheduling periods and CPU-usage trends are meaningful, but any final
  real-time claim has to be checked on the board.
- **The chapter 6 faults never fire.**
  Renode does not implement `CCR.DIV_0_TRP`, so a divide by zero raises no
  UsageFault, and a write to unmapped memory raises no BusFault either. The
  task simply ends, so chapter 6's actual claim — only the broken task dies,
  everything else keeps running — still holds, but `FAULT DETECTED` and the
  diagnosis of the cause are hardware-only.

:::{note}
Verified on **macOS (Apple Silicon)**, **Windows 11 (ARM64)** and
**Ubuntu 24.04 (x86_64)**. Please report problems on
[Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).
:::

## Troubleshooting

**"firmware not found"**

Did you run `pio run -e sim`? A plain `pio run` only builds for real hardware
and does not produce `.pio/build/sim/firmware.elf`.

**"cannot connect to Renode's Monitor"**

Check that `renode` is on your PATH, or pass the executable with `--renode`.

**Nothing appears on the serial console**

Some chapters are waiting for input (`S` in chapter 1, a shell prompt from
chapter 5 onwards). If it still stays silent, try another output channel with
`--uart sci2`.

**Port already in use**

Change the numbers with `--http-port`, `--monitor-port` and `--uart-port`.

## Running the chapter checks automatically

The book's verification script also runs against the emulator, using the same
expectations taken from the "expected output" sections of the text.

```bash
cd code
uv run python scripts/verify_chapters.py --sim
uv run python scripts/verify_chapters.py --sim --only 05_shell
```

Anything the emulator cannot reproduce (the chapter 6 faults, for instance) is
reported as `SKIP` together with the reason.

`code/sim/record.py` records the board's LEDs straight into an animated GIF.

## How it works

`code/sim/README.md` documents which addresses are read, and how the values
reach the browser. The virtual board itself (`board.py` and `board.html`) is
about 600 lines.
