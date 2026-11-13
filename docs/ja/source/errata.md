# 正誤表

現在、報告されている正誤情報はありません。

誤りを見つけた場合は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
から報告をお願いします。

| ページ | 誤 | 正 | 反映刷 |
|---|---|---|---|
| — | — | — | — |

## お知らせ: サンプルコードの URL（p.33）

発売直後（2026年9月18日〜19日）、p.33 に載っている
`https://github.com/iory/learning-os-from-arduino` が公開されておらず、
`git clone` が失敗していました（[#20](https://github.com/iory/build-your-own-arduino-rtos/issues/20)）。
ご迷惑をおかけしました。

現在は公開済みで、書籍の手順のまま使えます。

```bash
git clone https://github.com/iory/learning-os-from-arduino.git
cd learning-os-from-arduino/docs/os-on-arduino/code
```

書籍に出てくる `docs/os-on-arduino/code/...` のパスも、そのまま通ります。

## お知らせ: サンプルコードの更新

2026年11月13日、第5章の `05_shell/src/os_kernel.cpp` にある `os_get_stack_used()` から、
計算するだけで使っていなかった変数 `base` の 1 行を削除しました
（[#72](https://github.com/iory/build-your-own-arduino-rtos/issues/72)）。
関数の戻り値と動作は変わりません。書籍の本文に変更はなく、
すでに `git clone` したコードもそのまま使えます。
