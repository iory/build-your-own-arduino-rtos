# Advanced 4: A Minimal Filesystem — LittleFS

## Sample code

- Directory: `code/adv4_fs`

```bash
pio run -d adv4_fs -t upload
pio device monitor -b 115200
```

## Source code

The sketch for this chapter. Click a file name to expand. The code is mirrored automatically from the manuscript repository, so what you see here is always current.

:::{dropdown} `src/main.cpp` — 97 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/main.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/fs.h` — 18 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/include/fs.h)

```{literalinclude} ../../../../code/adv4_fs/include/fs.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/fs_flash_hal.h` — 19 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/include/fs_flash_hal.h)

```{literalinclude} ../../../../code/adv4_fs/include/fs_flash_hal.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/fs.cpp` — 70 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/fs.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/fs.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/fs_flash_hal.cpp` — 53 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv4_fs/src/fs_flash_hal.cpp)

```{literalinclude} ../../../../code/adv4_fs/src/fs_flash_hal.cpp
:language: cpp
:linenos:
```
:::


## Pitfalls

(Collected from reader questions — ask via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).)
