# Advanced 2: User/Kernel Mode and SVC

## Sample code

- Directory: `code/adv2_syscall`

```bash
pio run -d adv2_syscall -t upload
pio device monitor -b 115200
```

## Source code

The sketch for this chapter. Click a file name to expand. The code is mirrored automatically from the manuscript repository, so what you see here is always current.

:::{dropdown} `src/main.cpp` — 94 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/main.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/main.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_kernel.h` — 74 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_kernel.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_kernel.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_syscall.h` — 33 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_syscall.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_syscall.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `include/os_syscall_user.h` — 38 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/include/os_syscall_user.h)

```{literalinclude} ../../../../code/adv2_syscall/include/os_syscall_user.h
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_kernel.cpp` — 231 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/os_kernel.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/os_kernel.cpp
:language: cpp
:linenos:
```
:::

:::{dropdown} `src/os_svc.cpp` — 95 lines
:icon: code

[Open on GitHub](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/adv2_syscall/src/os_svc.cpp)

```{literalinclude} ../../../../code/adv2_syscall/src/os_svc.cpp
:language: cpp
:linenos:
```
:::


## Pitfalls

(Collected from reader questions — ask via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).)
