# 組み立て手順 — 8 自由度四脚ロボット

先に 3 種類のユニット（サーボ入りの胴体・左脚・右脚）を組み、最後に脚を
胴体へ取り付けます。

ネジは **M3×6 が 40 本、M2×6 が 16 本** — どちらも **STS3215 に付属している
ネジだけで足ります**（8 個買えば十分な本数が付いてきます）。別途購入は不要です。

::::{grid} 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_parts.jpg
:target: ../_static/quadruped_parts.jpg
:alt: 用意する部品。3D プリントの 9 部品（胴体 ×1・脚ブラケット ×4・脚リンク ×4）、STS3215 ×8、付属のネジ

用意する部品。3D プリントの 9 部品（胴体 ×1・脚ブラケット ×4・脚リンク ×4）、STS3215 ×8、付属のネジ
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_screws.jpg
:target: ../_static/quadruped_screws.jpg
:alt: STS3215 に付属するネジ（3 種類）

STS3215 に付属するネジ（3 種類）
```

:::
::::

## インタラクティブ 3D ビューア

ブラウザ上で 1 ステップずつアニメーションを再生できます。マウスで視点を回し、
スライダーで手順を前後できます。

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../assembly/quadruped/index.html"
     target="_blank" rel="noopener">ビューアを全画面で開く ↗</a>
  &nbsp;
  <a class="sd-btn sd-btn-outline-primary" href="../assembly/quadruped/instructions.pdf"
     target="_blank" rel="noopener">PDF 版の手順書</a>
</p>
<iframe src="../assembly/quadruped/index.html"
        style="width:100%; height:75vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="四脚ロボット 組み立てビューア"></iframe>
```

---

## 部品のユニット構成

機体は 3 種類のユニット（サブアセンブリ）を先に組み、最後に胴体へ脚を
取り付けます。単一部品は全部で **81 個（8 種類）**。

| ユニット | 数量 | 内部部品数 |
|---|---|---|
| body_servo（胴体 + サーボ 4） | ×1 | 13 |
| leg_left（左脚） | ×2 | 11 |
| leg_right（右脚） | ×2 | 11 |

| 部品 | 個数 |
|---|---|
| ネジ M3×6 | ×40 |
| ネジ M2×6 | ×16 |
| STS3215（ケース + ホーン） | ×8 |
| bracket_outline | ×4 |
| leg_link1 | ×4 |
| 胴体（body） | ×1 |

## ユニットの事前組み立て

同じユニットは 1 回だけ手順を示します。**×N** はロボット全体で使う個数です。
上から順に組めば部品が揃います。

:::{dropdown} STS3215 サーボ（ホーン取り付け） **×8**
:open:

ホーンが外れた状態で届いた場合のみ。取り付け済みならこのユニットは飛ばして
かまいません。

1. **STS3215_horn** を置く（土台）

   ![STS3215 step 1](assembly_img/units/STS3215/step_01.png)

2. **STS3215_case** をホーンへ — 同軸 φ4.8mm（×2）、面合わせ ×2

   ![STS3215 step 2](assembly_img/units/STS3215/step_02.png)

```{figure} ../_static/quadruped_horn_screw.jpg
:target: ../_static/quadruped_horn_screw.jpg
:width: 50%

ネジを回すときは、ドライバーの先端をネジ穴と平行に当てる。先端が斜めになっていると力が伝わらず、ネジ頭をなめやすい
```

:::

:::{dropdown} body_servo（胴体にサーボ 4 個を固定） **×1**

使う部品: 胴体 ×1、STS3215 ×4、M3x6 ×8

1. **body**（胴体）を置く（土台）

   ![body_servo step 1](assembly_img/units/body_servo/step_01.png)

2. **STS3215-4** — 胴体へ差し込む（同軸 φ4.2mm ×4、面合わせ ×2）

   ![body_servo step 2](assembly_img/units/body_servo/step_02.png)

3. 🔩 **M3x6 ×2** を締める（STS3215-4 ↔ 胴体）

   ![body_servo step 3](assembly_img/units/body_servo/step_03.png)

4. **STS3215-3** — 胴体へ差し込む

   ![body_servo step 4](assembly_img/units/body_servo/step_04.png)

5. 🔩 **M3x6 ×2** を締める

   ![body_servo step 5](assembly_img/units/body_servo/step_05.png)

6. **STS3215-2** — 胴体へ合わせる（面合わせ ×2）

   ![body_servo step 6](assembly_img/units/body_servo/step_06.png)

7. 🔩 **M3x6 ×2** を締める

   ![body_servo step 7](assembly_img/units/body_servo/step_07.png)

8. **STS3215-1** — 胴体へ合わせる（面合わせ ×2）

   ![body_servo step 8](assembly_img/units/body_servo/step_08.png)

9. 🔩 **M3x6 ×2** を締める

   ![body_servo step 9](assembly_img/units/body_servo/step_09.png)

```{figure} ../_static/quadruped_body_servo.jpg
:target: ../_static/quadruped_body_servo.jpg
:width: 50%

4 個のサーボを固定した胴体（実物）
```

:::

::::::{dropdown} leg_left（左脚） **×2**

使う部品: STS3215 ×1、bracket_outline ×1、leg_link1 ×1、M3x6 ×4、M2x6 ×4

1. **STS3215** を置く（土台）

   ![leg_left step 1](assembly_img/units/leg_left/step_01.png)

2. **bracket_outline** — サーボのホーン側へ差し込む（同軸 φ3.2mm ×4、面合わせ ×2）

   ![leg_left step 2](assembly_img/units/leg_left/step_02.png)

3. 🔩 **M3x6 ×4** を締める（サーボ ↔ ブラケット）

   ![leg_left step 3](assembly_img/units/leg_left/step_03.png)

4. **leg_link1** — サーボのケース側へ差し込む（同軸 φ2.0mm ×4、面合わせ ×2）

   ![leg_left step 4](assembly_img/units/leg_left/step_04.png)

5. 🔩 **M2x6 ×4** を締める（サーボ ↔ リンク）

   ![leg_left step 5](assembly_img/units/leg_left/step_05.png)

**実物の写真**（左右の脚で手順は同じ）:

:::::{grid} 2 3 3 3
:gutter: 2

:::{grid-item}

```{figure} ../_static/quadruped_bracket_seat_1.jpg
:target: ../_static/quadruped_bracket_seat_1.jpg
:alt: 脚ブラケットのホーン取り付け部

脚ブラケットのホーン取り付け部
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_seat_2.jpg
:target: ../_static/quadruped_bracket_seat_2.jpg
:alt: 同じ部分を別の角度から

同じ部分を別の角度から
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_1.jpg
:target: ../_static/quadruped_bracket_1.jpg
:alt: 手順 2: ブラケットをサーボのホーン側へ

手順 2: ブラケットをサーボのホーン側へ
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_2.jpg
:target: ../_static/quadruped_bracket_2.jpg
:alt: 手順 3: ネジを締める途中

手順 3: ネジを締める途中
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_bracket_3.jpg
:target: ../_static/quadruped_bracket_3.jpg
:alt: 手順 3: M3x6 ×4 を締め終えたところ

手順 3: M3x6 ×4 を締め終えたところ
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_leg_link_1.jpg
:target: ../_static/quadruped_leg_link_1.jpg
:alt: 手順 4: 脚リンクをサーボのケース側へ

手順 4: 脚リンクをサーボのケース側へ
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_leg_link_2.jpg
:target: ../_static/quadruped_leg_link_2.jpg
:alt: 手順 4: 差し込んだところ

手順 4: 差し込んだところ
```

:::
:::{grid-item}

```{figure} ../_static/quadruped_legs_x4.jpg
:target: ../_static/quadruped_legs_x4.jpg
:alt: ブラケットを付けたサーボ 4 本（左右 2 本ずつ）

ブラケットを付けたサーボ 4 本（左右 2 本ずつ）
```

:::
:::::
::::::

:::{dropdown} leg_right（右脚） **×2**

使う部品: STS3215 ×1、bracket_outline ×1、leg_link1 ×1、M3x6 ×4、M2x6 ×4
（左脚と同じ構成。ブラケットの向きが鏡像）

1. **STS3215** を置く（土台）

   ![leg_right step 1](assembly_img/units/leg_right/step_01.png)

2. **bracket_outline** — サーボのホーン側へ差し込む

   ![leg_right step 2](assembly_img/units/leg_right/step_02.png)

3. 🔩 **M3x6 ×4** を締める

   ![leg_right step 3](assembly_img/units/leg_right/step_03.png)

4. **leg_link1** — サーボのケース側へ差し込む

   ![leg_right step 4](assembly_img/units/leg_right/step_04.png)

5. 🔩 **M2x6 ×4** を締める

   ![leg_right step 5](assembly_img/units/leg_right/step_05.png)
:::

```{warning}
組み始める前に、**各サーボにユニークな ID を振っておく**こと（工場出荷時は全部
同じ ID なので、1 個ずつ接続して設定する。機体に組み込んでからだと個体を特定
できない）。

原点（0 点）合わせは**組み上げた後にソフトウェアで行う**ので、組立時のホーンの
角度は気にしなくてよい。手順は第13章を参照。
```

## 本体の組み立て

事前に組んだユニットを胴体（body_servo）に取り付けます。

### Step 1: body_servo を置く

![Step 1](assembly_img/step_001.png)

### Step 2: leg_right（1 本目）を取り付ける

胴体後方のサーボホーンへ、脚のリンクを差し込みます（同軸 φ3.0mm ×4）。

![Step 2](assembly_img/step_002.png)

### Step 3: 🔩 M3x6 ×4 を締める

![Step 3](assembly_img/step_003.png)

### Step 4: leg_right（2 本目）を取り付ける

![Step 4](assembly_img/step_004.png)

### Step 5: 🔩 M3x6 ×4 を締める

![Step 5](assembly_img/step_005.png)

### Step 6: leg_left（1 本目）を取り付ける

反対側のサーボホーンへ差し込みます。挿入方向が右脚と逆になります。

![Step 6](assembly_img/step_006.png)

### Step 7: 🔩 M3x6 ×4 を締める

![Step 7](assembly_img/step_007.png)

### Step 8: leg_left（2 本目）を取り付ける

![Step 8](assembly_img/step_008.png)

### Step 9: 🔩 M3x6 ×4 を締める

![Step 9](assembly_img/step_009.png)

これで機体は完成です。配線と通電、キャリブレーションは第13章へ。

---

CAD データの書き出しには
[solidworks_urdf_exporter2](https://github.com/jsk-ros-pkg/solidworks_urdf_exporter2)
を使っています。
