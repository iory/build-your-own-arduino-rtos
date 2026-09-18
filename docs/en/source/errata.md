# Errata

Please report mistakes via
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).

| Page | Wrong | Right | Fixed in printing |
|---|---|---|---|
| p.33 | `git clone https://github.com/iory/learning-os-from-arduino.git`<br>`cd learning-os-from-arduino/docs/os-on-arduino/code` | `git clone https://github.com/iory/build-your-own-arduino-rtos.git`<br>`cd build-your-own-arduino-rtos/code` | — |

## About the sample-code repository and paths

The book (1st edition, 1st printing) names `learning-os-from-arduino`, which was the private repository used for writing ([#20](https://github.com/iory/build-your-own-arduino-rtos/issues/20)). The main repository for the sample code is [iory/build-your-own-arduino-rtos](https://github.com/iory/build-your-own-arduino-rtos), with the code under `code/`.

So that the book's commands still work, a **mirror** lives at that URL: [iory/learning-os-from-arduino](https://github.com/iory/learning-os-from-arduino). It is an automatic copy of `code/` placed at the book's path, `docs/os-on-arduino/code/`, with identical contents.

If you are starting fresh, use the main repository and read `docs/os-on-arduino/code/...` in the book as `code/...`.
