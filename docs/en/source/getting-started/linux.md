# Developing on Linux

Linux builds and flashes every chapter with the same commands as Windows and
macOS. The differences are the port name (`/dev/ttyACM0`) and how you install
the tools.

There are a few **errors that only show up on Linux**, and they are hard to
diagnose if you have not seen them before, so this page lists them together
with the real output. It also covers **talking to the board from Python**,
which the book itself does not.

```{note}
The output on this page was captured from a real Arduino UNO R4 WiFi attached to
Ubuntu 24.04 LTS (x86_64). Differences on other distributions are in section 9.
```

## 1. Set up

### Install uv

[uv](https://docs.astral.sh/uv/) manages the Python environment and packages.
We run PlatformIO through it.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

It installs into `~/.local/bin`. Open a new shell, or reload your PATH:

```bash
source ~/.bashrc          # or ~/.zshrc for zsh
uv --version
```

Install `git` first if you do not have it:

```bash
sudo apt install -y git   # Ubuntu / Debian
```

### Get the sample code

```bash
git clone https://github.com/iory/build-your-own-arduino-rtos.git
cd build-your-own-arduino-rtos/code
uv sync
```

`uv sync` installs PlatformIO and pyserial. **You do not need to install a
compiler.** PlatformIO downloads its own toolchain into `~/.platformio` (a few
hundred MB on the first build, which takes a few minutes).

## 2. Before plugging in the board — install the udev rules

**Do this first.** It solves both problems described later (permissions and
ModemManager) in one step.

```bash
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/develop/platformio/assets/system/99-platformio-udev.rules \
  | sudo tee /etc/udev/rules.d/99-platformio-udev.rules >/dev/null
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**Unplug and replug the board afterwards.** Rules are not applied retroactively
to a device that is already connected.

These are PlatformIO's official udev rules
([official docs](https://docs.platformio.org/en/latest/core/installation/udev-rules.html)).

## 3. Find the board

```bash
uv run pio device list
```

```text
/dev/ttyACM0
------------
Hardware ID: USB VID:PID=2341:1002 SER=B43A45B9F1CC LOCATION=1-1:1.1
Description: UNO WiFi R4 CMSIS-DAP - TinyUSB CDC
```

`2341:1002` is the Arduino UNO R4 WiFi. `2341` is Arduino's USB vendor ID; we
use it later to find the port automatically from Python.

You may also see several `/dev/ttyS*` entries. Those are motherboard serial
ports and have nothing to do with the board. Look for **`ttyACM`**.

## 4. Build and flash

```bash
uv run pio run -d 01_boot -t upload
```

```{figure} ../_static/linux_upload.gif
:name: fig-linux-upload-en
:width: 100%

Checking the port and flashing, recorded on a real Ubuntu 24.04 machine
```

As `Auto-detected: /dev/ttyACM0` shows, you normally do not need to name the
port. Add `--upload-port /dev/ttyACM0` only if another USB serial device
confuses the detection.

## 5. Watch the serial monitor

```bash
uv run pio device monitor -b 115200
```

Chapter 1 **starts printing once you send a single `S`**. Type `S` after the
monitor opens.

```text
=== Boot Sequence Check ===

bss_var (should be 0): 0
data_var (should be 12345): 12345

=== Memory Addresses ===
&bss_var:  0x200000C4
&data_var: 0x20000000
VTOR:      0x20007F00
MSP:       0x20007EC8

If you see this, boot sequence completed!
```

Press `Ctrl-C` to leave the monitor.

## 6. Where Linux trips you up

### `Permission denied: /dev/ttyACM0`

If you plug in the board without installing the udev rules:

```text
$ cat /dev/ttyACM0
cat: /dev/ttyACM0: Permission denied
```

From Python:

```text
PermissionError: [Errno 13] Permission denied: '/dev/ttyACM0'
```

The cause is the device file's owning group:

```bash
$ ls -l /dev/ttyACM0
crw-rw---- 1 root dialout 166, 0 Aug 31 01:51 /dev/ttyACM0
#                  ^^^^^^^ you must be in this group to open it
```

**Installing the udev rules (section 2) avoids this entirely.** PlatformIO's
rules set `MODE="0666"`, so any user can open the port:

```bash
$ ls -l /dev/ttyACM0
crw-rw-rw- 1 root dialout 166, 0 Aug 31 02:12 /dev/ttyACM0
```

If you would rather not use the udev rules (for example if you only use the
Arduino IDE), add yourself to the `dialout` group instead:

```bash
sudo usermod -aG dialout $USER
```

**You must log out and back in afterwards** — group changes do not apply to an
existing session. `newgrp dialout` enables it in the current terminal only.

### ModemManager grabs the board

Ubuntu runs **ModemManager**, a daemon that inspects any USB serial device that
appears, in case it is a cellular modem. An Arduino is not a modem, but the port
gets **opened right after you plug it in**, so a sketch that prints only from
`setup()` can finish printing before your monitor is even open.

That is why Chapter 1 waits for an `S`.

Check what your machine does:

```bash
$ udevadm info -q property -n /dev/ttyACM0 | grep ID_MM
ID_MM_CANDIDATE=1
```

If you only see `ID_MM_CANDIDATE=1`, ModemManager is going to probe it.
**After installing the udev rules (section 2):**

```bash
$ udevadm info -q property -n /dev/ttyACM0 | grep ID_MM
ID_MM_CANDIDATE=1
ID_MM_DEVICE_IGNORE=1
ID_MM_PORT_IGNORE=1
```

With `ID_MM_DEVICE_IGNORE=1` set, ModemManager leaves the device alone.

```{admonition} Why PlatformIO's rules work here
:class: note

The Arduino line in the official rules restricts `idProduct` to `[08][023]*`,
and the UNO R4 WiFi's PID `1002` **does not match it**. What actually matches is
a different line further down:

    ATTRS{product}=="*CMSIS-DAP*", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1", ENV{ID_MM_PORT_IGNORE}="1"

The UNO R4 WiFi reports its USB product name as `UNO WiFi R4 CMSIS-DAP`, so it
matches **on the product name, not the PID**.
```

On a machine that never uses mobile broadband you can simply turn the service
off, though the udev rules make that unnecessary:

```bash
sudo systemctl disable --now ModemManager
```

### You cannot flash while the monitor is open

Only one process can hold the serial port. Flashing with the monitor still open
fails with `Device or resource busy` (the Linux equivalent of Windows'
`PermissionError`). **Close the monitor with `Ctrl-C`** and flash again.

The same applies to the Arduino IDE's serial monitor and to your own Python
scripts.

### Other things

- **`brltty`** is a braille-display daemon that ships with Ubuntu. It hijacks
  some USB serial devices, so if `/dev/ttyACM0` appears and immediately
  disappears, suspect it (`systemctl status brltty`). It has not been observed
  with the UNO R4 WiFi, but it can happen with USB-serial adapters
- Flashing **through a USB hub** sometimes fails. Try a direct port on the machine
- If the board stops responding, **press RESET twice quickly** to enter the
  bootloader

## 7. Talking to the board from Python

The book only goes as far as the serial monitor, but as soon as you build
something real you will want your PC to talk to the board. Use **pyserial**,
which `uv sync` already installed.

### A minimal example

Flash Chapter 5 (`05_shell`) first. The shell is running, so sending `ps`
returns the task table.

```python
import time
import serial
import serial.tools.list_ports

# Arduino's USB vendor ID — so you never have to hard-code the port name
port = next(p.device for p in serial.tools.list_ports.comports() if p.vid == 0x2341)
print("port:", port)

ser = serial.Serial(port, 115200, timeout=0.2)
time.sleep(1.6)          # opening the port resets the board, so wait
ser.reset_input_buffer()

ser.write(b"ps\n")
time.sleep(1.0)
print(ser.read(4096).decode("utf-8", errors="replace"))
ser.close()
```

```bash
uv run python hello_serial.py
```

```{figure} ../_static/linux_pyserial.gif
:name: fig-linux-pyserial-en
:width: 100%

Running `hello_serial.py` and getting a reply from the board's shell
```

```text
port: /dev/ttyACM0
ps

ID  NAME           STATE      CPU%
--  ----           -----      ----
0   idle           READY     100%
1   LED1           BLOCKED   0%
2   LED2           BLOCKED   0%
3   Heartbeat      BLOCKED   0%
4   Shell          RUNNING   0%

>
```

### Three things worth remembering

**Do not hard-code the port name.** Looking it up with `p.vid == 0x2341` means
**the same code runs on Linux, macOS and Windows** — only the returned string
differs (`/dev/ttyACM0` / `/dev/cu.usbmodem...` / `COM3`).

**Wait ~1.5 s after opening.** The UNO R4 restarts the sketch when the port is
opened. Without the wait you lose the first output, or your command never
arrives.

**Only one process can hold the port.** Close the PlatformIO monitor or the
Arduino IDE before running your script.

## 8. Driving the quadruped from your PC

Bringing up and calibrating the Chapter 13 robot is much faster from the PC —
every value is on screen and you do not reflash after each change.

```bash
cd code/13_quadruped/host
uv run python quad_host.py scan        # how many servos are on the bus
uv run python quad_host.py calibrate   # measure zero and sign -> calib.json
uv run python quad_host.py stand       # hold the home pose
uv run python quad_host.py teleop      # walk with w/s/a/d
```

Add `--port /dev/ttyACM0` if you need to name the port.

## 9. Other distributions

This page was verified on Ubuntu 24.04. The steps are essentially the same
elsewhere; **only package installation and the group name differ**.

| | Ubuntu / Debian | Fedora | Arch |
|---|---|---|---|
| Install git | `sudo apt install git` | `sudo dnf install git` | `sudo pacman -S git` |
| Serial group | `dialout` | `dialout` | **`uucp`** |

**Installing `uv` and PlatformIO's toolchain is identical on every
distribution.** You never need to provide your own compiler.

To find the group your system uses:

```bash
$ ls -l /dev/ttyACM0
crw-rw---- 1 root dialout 166, 0 Aug 31 01:51 /dev/ttyACM0
#                  ^^^^^^^ this is the group you need to join
```

With the udev rules installed, the group stops mattering at all.

## 10. Verifying every chapter at once

A bundled script builds every chapter, flashes it, and checks that the serial
output matches what the book says.

```bash
uv run python scripts/verify_chapters.py
```

`--only` narrows it to specific chapters, and `--build-only` checks the builds
without a board attached. The script's messages are in Japanese.

```{raw} html
<p><a href="../../chapters/verify.html">全章の動作確認 — full options and interactive mode, on the Japanese site ↗</a></p>
```
