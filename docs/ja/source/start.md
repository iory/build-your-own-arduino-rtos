---
og:description: 『つくりながら学ぶ！リアルタイムOS自作入門』を、気になっていることから読み始めるための案内。
---

# 気になることから読む

本書は第1章から順に積み上げる構成ですが、最初から順に読まなくてもかまいません。
下から、気になっているものを選んでください。
読んでいて分からない言葉が出てきたら、そのときに前の章へ戻れば十分です。

## まず動くところを見たい

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 自作 OS をブラウザで動かす
:link: getting-started/simulator
:link-type: doc
実機と同じファームウェアをブラウザの中の QEMU で動かします。
インストールは要りません。
:::

:::{grid-item-card} 四脚ロボットをブラウザで歩かせる
:link: hardware/walk
:link-type: doc
学習済みの歩行方策を物理シミュレーションで動かします。
前進・旋回はスライダーで変えられます。
:::
::::

## 普段使っているコンピュータの「なぜ？」

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 重い処理があっても、ほかのアプリが止まらないのはなぜ？
:link: chapters/ch04
:link-type: doc
第4章: タイマ割り込みで、走っているタスクを強制的に切り替えます。
:::

:::{grid-item-card} アプリが落ちても、OS が落ちないのはなぜ？
:link: chapters/ch06
:link-type: doc
第6章: ゼロ除算や不正なアドレスへの書き込みを受け止め、
起こしたタスクだけを止めます。
:::

:::{grid-item-card} `top` やタスクマネージャの CPU % はどう数えている？
:link: chapters/ch07
:link-type: doc
第7章: OS が数えている CPU 使用率を LED マトリクスに出します。
:::

:::{grid-item-card} 電源を入れた瞬間、CPU は何をしている？
:link: chapters/ch01
:link-type: doc
第1章: リセット直後から `main()` にたどり着くまでを追いかけます。
:::

:::{grid-item-card} `malloc` の中では何が起きている？
:link: chapters/adv3
:link-type: doc
応用編 第3章: `malloc` / `free` を自分で書きます。
:::

:::{grid-item-card} 「ファイル」はどうやってできている？
:link: chapters/adv4
:link-type: doc
応用編 第4章: Flash の上にファイルシステムを載せます。
:::
::::

## 好きなものから

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} ロボットを歩かせたい
:link: chapters/ch13
:link-type: doc
第13章: 自作 OS でサーボを 8 個動かして四脚を歩かせます。
部品と組み立ては {doc}`hardware/index` にあります。
:::

:::{grid-item-card} Python が好き
:link: chapters/ch11
:link-type: doc
第11章: マイコンの上で動く小さな Python を作ります。
その手前の第8章では、もっと小さな言語を作ります。
:::

:::{grid-item-card} 仕事で FreeRTOS を使っている
:link: chapters/ch10
:link-type: doc
第10章: 自作 OS と同じ課題を FreeRTOS で書いて、設計を比べます。
:::

:::{grid-item-card} 電子工作が好き
:link: chapters/ch12
:link-type: doc
第12章: PWM の生成と A/D 変換を、レジスタのレベルから理解します。
:::
::::

## 動いているものを壊してみたい

第4章・第6章・第7章の終わりに「壊してみる」を置きました。コードを 1 か所だけ
変えて、何が起きるかを予想してから動かします。ブラウザ版でも試せます。

- {ref}`ch04-break`
- {ref}`ch06-break`
- {ref}`ch07-break`
