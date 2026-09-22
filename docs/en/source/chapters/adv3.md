# Advanced 3: Writing Your Own Heap

## Sample code

- Directory: `docs/os-on-arduino/code/adv3_heap`

```bash
pio run -d adv3_heap -t upload
pio device monitor -b 115200
```

## Source code

The sketch for this chapter. Click a file name to expand. The code is mirrored automatically from the manuscript repository, so what you see here is always current.

:::{dropdown} `src/main.cpp` — 75 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv3_heap/src/main.cpp)

```{literalinclude} ../../../../code/adv3_heap/src/main.cpp
:language: cpp
:linenos:
```

:::

:::{dropdown} `include/os_heap.h` — 22 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv3_heap/include/os_heap.h)

```{literalinclude} ../../../../code/adv3_heap/include/os_heap.h
:language: cpp
:linenos:
```

:::

:::{dropdown} `src/os_heap.cpp` — 128 lines
:icon: code

[Open on GitHub](https://github.com/iory/learning-os-from-arduino/blob/main/docs/os-on-arduino/code/adv3_heap/src/os_heap.cpp)

```{literalinclude} ../../../../code/adv3_heap/src/os_heap.cpp
:language: cpp
:linenos:
```

:::


## Pitfalls

(Collected from reader questions — ask via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).)
