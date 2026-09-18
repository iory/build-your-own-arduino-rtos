# 正誤表

誤りを見つけた場合は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
から報告をお願いします。

| ページ | 誤 | 正 | 反映刷 |
|---|---|---|---|
| p.33 | `git clone https://github.com/iory/learning-os-from-arduino.git`<br>`cd learning-os-from-arduino/docs/os-on-arduino/code` | `git clone https://github.com/iory/build-your-own-arduino-rtos.git`<br>`cd build-your-own-arduino-rtos/code` | — |

## サンプルコードのリポジトリとパスについて

書籍（初版第1刷）に載っている `learning-os-from-arduino` は、執筆に使った非公開のリポジトリの名前でした（[#20](https://github.com/iory/build-your-own-arduino-rtos/issues/20)）。サンプルコードの本家は [iory/build-your-own-arduino-rtos](https://github.com/iory/build-your-own-arduino-rtos) で、コードは `code/` にあります。

書籍どおりの手順でも動くように、同じ URL に**ミラー** [iory/learning-os-from-arduino](https://github.com/iory/learning-os-from-arduino) を置いています。本家の `code/` を書籍と同じ `docs/os-on-arduino/code/` に自動でコピーしたもので、中身は本家と同じです。

これから始める場合は本家を使い、書籍に出てくる `docs/os-on-arduino/code/...` は `code/...` に読み替えてください。
