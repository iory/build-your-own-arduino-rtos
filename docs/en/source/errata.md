# Errata

No corrections reported yet.

Please report mistakes via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).

| Page | Wrong | Right | Fixed in printing |
|---|---|---|---|
| — | — | — | — |

## Notice: sample-code URL (p.33)

Right after release (September 18–19, 2026), the repository named on p.33,
`https://github.com/iory/learning-os-from-arduino`, was not public, so
`git clone` failed ([#20](https://github.com/iory/build-your-own-arduino-rtos/issues/20)).
We apologize for the trouble.

It is public now, and the book's commands work as printed:

```bash
git clone https://github.com/iory/learning-os-from-arduino.git
cd learning-os-from-arduino/docs/os-on-arduino/code
```

Every `docs/os-on-arduino/code/...` path in the book works as-is.

## Notice: sample-code updates

On November 13, 2026, one line was removed from `os_get_stack_used()` in
Chapter 5's `05_shell/src/os_kernel.cpp`: the variable `base`, which was
computed but never used
([#72](https://github.com/iory/build-your-own-arduino-rtos/issues/72)).
The function's return value and behavior are unchanged. The book's text is
unaffected, and code you have already cloned keeps working as-is.
