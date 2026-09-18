# Advanced 1: Locks and Synchronization

## Sample code

- Directory: `docs/os-on-arduino/code/adv1_sync`

```bash
pio run -d adv1_sync -t upload
pio device monitor -b 115200
```

## Source code

The sketch for this chapter. Click a file name to expand. The code is mirrored automatically from the manuscript repository, so what you see here is always current.

:::{dropdown} `src/main.cpp` — 140 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/main.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_atomic.h` — 28 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_atomic.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_atomic.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_fault.h` — 46 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_fault.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_fault.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_kernel.h` — 76 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_kernel.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_kernel.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_sync.h` — 53 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/include/os_sync.h)

```{literalinclude} ../../../../code/adv1_sync/include/os_sync.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_fault.cpp` — 170 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_fault.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_fault.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_kernel.cpp` — 231 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_kernel.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_kernel.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_sync.cpp` — 150 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv1_sync/src/os_sync.cpp)

```{literalinclude} ../../../../code/adv1_sync/src/os_sync.cpp
:language: cpp
:linenos:
```
:::


## Pitfalls

(Collected from reader questions — ask via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).)
