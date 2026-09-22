# Checking every chapter on your own board

The sample code ships with a script that **builds every chapter, uploads it to the
board and automatically compares the serial output with what the book says**. It
checks in one go that your board gives the same results as the book.

The same commands work on Linux, macOS and Windows.

## Usage

```bash
cd docs/os-on-arduino/code
uv sync                                            # first time only
uv run python scripts/verify_chapters.py --list    # chapters and their expectations
uv run python scripts/verify_chapters.py --build-only  # build only, no board needed
uv run python scripts/verify_chapters.py           # every chapter on the board
```

The serial port is found automatically from the Arduino USB vendor ID. If other USB
serial devices are connected, pass it with `--port` (`COM3` / `/dev/ttyACM0` /
`/dev/cu.usbmodem...`).

Example output (the script prints its messages in Japanese):

```text
OS: Darwin 25.5.0  Python: 3.14.2
ボード: /dev/cu.usbmodemXXXXXXXXXXXXX

=== 01_boot =====================================================
  -> PASS  (13.4s)
     OK  === Boot Sequence Check ===
     OK  BSS がゼロクリアされている
     OK  DATA が Flash からコピーされている
     OK  ベクタテーブルが RAM 上にある
     OK  If you see this, boot sequence completed!
```

What it checks is not the output text itself but **the properties the book
claims**. For chapter 1, for example, it confirms from the printed values that BSS
was zeroed and DATA was copied from Flash. Values that depend on the environment,
such as addresses and times, are matched with regular expressions that allow for
the variation.

Three checks cannot be written as regular expressions:

| Check | What it verifies | Where in the book |
|---|---|---|
| `cpu_sum` | The CPU% column of `ps` does not add up to more than 100% | Chapter 4, 4.7 ("the total is close to 100%") |
| `preemption` | The 1-second task keeps its period while a heavy computation runs | The point of chapter 4 itself |
| `philosophers` | All five philosophers keep eating | Deadlock avoidance in Advanced 1 |

## Stepping through the chapters while watching the LEDs

`-i` switches to interactive mode. It uploads one chapter at a time and **moves on
when you press Enter, so you can watch the LEDs on the board**. The automatic checks
cannot see the LEDs or the matrix, so use this mode for visual checks.

```bash
uv run python scripts/verify_chapters.py -i
```

| Input | Action |
|---|---|
| Enter alone | Next chapter |
| Any text | Sent to the board as is (`ps`, `kill 1`, ...) |
| `!` | Sends the chapter's "things to try" in order |
| `r` / `b` / `q` | Re-upload / previous chapter / quit |

Each chapter shows what to look for (in Japanese):

```text
========================================================================
[7/20] 07_led_matrix   本編 第7章 LEDマトリクス可視化
========================================================================
目で見るポイント:
  ・マトリクス上半分に CPU 負荷グラフ（左が古い、右が新しい）
  ・マトリクス下半分にタスクごとの実行状況
  ・kill 3 で Heavy を止めると、負荷グラフが目に見えて下がる
試せること: ps / kill 3 / ps / exec 3
```

## Throwing bad input at the shell

`scripts/fuzz_shell.py` sends badly behaved input to the shells and REPLs (lines
that are too long, task IDs that do not exist, control characters, unclosed
brackets and so on) and checks that **the OS survives**. It checks the board is
still alive after every input, so you can tell which input made it hang.

```bash
uv run python scripts/fuzz_shell.py
```

## Tested environments

| | |
|---|---|
| macOS (Apple Silicon) | All 20 projects PASS |
| Windows 11 (ARM64) | All 20 projects PASS |
| Ubuntu | Build checked in CI |

The output of chapter 1 and of chapter 13's `iktest` was byte-for-byte identical on
macOS and Windows.
