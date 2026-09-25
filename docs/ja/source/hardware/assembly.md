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

(servo-id)=
## サーボに ID を振る

**ユニットを組む前に、8 個のサーボに 1〜8 の ID を振ります。** 8 個は 1 本の
バスにつながり、マイコンは ID で相手を呼び分けます。ところが新品の STS3215 は
**全部 ID 1** で出荷されているので、そのままでは区別できません。

ID を振るときは**サーボを 1 個ずつ**つなぎます。ID 1 のサーボが 2 個つながって
いると、「ID 1 を 2 に変えろ」という命令が両方に届き、両方とも ID 2 になって
しまいます。しかもツールからは 1 個に見えるので、失敗したことに気づけません。

### 用意するもの

- PC（Windows / macOS / Linux）
- ドライバーボード（Waveshare Bus Servo Adapter (A)）と USB Type-C ケーブル
- 12 V の AC アダプタ（[部品表](bom.md) の 3）
- STS3215（最初は 1 個だけ）
- マスキングテープとペン（番号のラベル用）

### ツールを入れる

ID の設定には [feetech-cli](https://github.com/iory/feetech-cli) を使います。
開発環境の準備で入れた uv で、次の 1 行で `feetech` コマンドが入ります
（uv がまだなら [macOS](../getting-started/macos.md) /
[Windows](../getting-started/windows.md) / [Linux](../getting-started/linux.md)
の「uv を入れる」を先に）。

```console
$ uv tool install feetech-cli
```

Python の用意は uv がするので要りません。コマンドは uv 本体と同じ場所に入るので、
`uv` が動くシェルならそのまま `feetech` も動きます。

### つなぐ

1. ボードの **ジャンパを 2 個とも B（USB-SERVO）** に差す。A は Arduino から
   動かすときの位置で、A のままだと PC からはサーボが見えません。
2. サーボを 1 個だけ、ボードの 3 ピンコネクタ（D V G）に差す。
3. AC アダプタをボードの DC ジャックに差す。**サーボの電源は USB からは取れない**
   ので、これを忘れるとサーボが応答しません。
4. USB Type-C で PC とボードをつなぐ。

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/servo_id_setup.jpg
:target: ../_static/servo_id_setup.jpg
:alt: PC、AC アダプタ、ドライバーボード、サーボ 1 個をつないだところ

全体。PC とボードは USB Type-C で、ボードの電源は AC アダプタから。
サーボは 1 個だけ
```

:::
:::{grid-item}

```{figure} ../_static/servo_id_wiring.jpg
:target: ../_static/servo_id_wiring.jpg
:alt: ドライバーボードに DC ジャック、USB Type-C、サーボのケーブルを差したところ

ボードまわり。左から DC ジャック（電源）、USB Type-C（PC）。サーボのケーブルは
上の 3 ピンコネクタへ。電源が入ると PWR の LED が赤く点く
```

:::
:::{grid-item}

```{figure} ../_static/servo_id_jumper.jpg
:target: ../_static/servo_id_jumper.jpg
:alt: ジャンパ 2 個が B の位置に差さっている。基板には A が UART-SERVO、B が USB-SERVO と印刷されている

ジャンパは 2 個とも **B（USB-SERVO）**。基板の表に A / B の意味が印刷されている
```

:::
::::

### 1 個ずつ番号を振る

1. サーボが見えることを確かめる。

   ```console
   $ feetech scan
   Found 1 servo(s) on /dev/cu.usbmodem59710813431 at 1.00Mbps:
     id   1  model   777  position  4095 (+179.9 deg)  12.3V  32C
   ```

   `id 1` が 1 行だけ出れば準備完了です。ポート名は環境によって違います
   （Windows なら `COM3` など）。ツールが自動で探すので、指定は要りません。

2. 新しい ID を書き込む。確認に `y` と答えると書き込まれます。1 個目は ID 1 の
   ままでよいので、この手順は 2 個目からです。

   ```console
   $ feetech set-id 1 2
   Change servo 1 to id 2? This writes the servo EEPROM. [y/N] y
   Servo 1 is now id 2.
   ```

   ID はサーボの EEPROM に書かれるので、電源を切っても消えません。

3. もう一度 `feetech scan` を実行して、新しい ID で見えることを確かめる。

4. **サーボにラベルを貼る。** ばらばらになってからでは、1 個ずつつなぎ直さないと
   見分けられません。組み立てたあとも見える面に貼っておくと、配線や交換のときに
   も困りません。

5. サーボを外し、次の新品をつないで 1 に戻る。3 個目は `feetech set-id 1 3`、
   4 個目は `feetech set-id 1 4`、…と 8 まで続けます。

```{figure} ../_static/servo_set_id.gif
:alt: feetech scan で ID 1 のサーボが見え、feetech set-id 1 2 で ID 2 に変え、もう一度 scan すると ID 2 で見える

手順 1〜3 を実機で実行したところ
```

```{figure} ../_static/servo_id_label.jpg
:target: ../_static/servo_id_label.jpg
:width: 50%
:alt: 「ID:1」と書いたラベルを側面に貼ったサーボ

番号を書いたラベルを貼ったサーボ
```

### どのサーボをどこに使うか

ID は脚と関節ごとに決まっています。この割り当てはファームウェアの
`include/quad_calib.h`（`QUAD_SERVO_ID`）と同じなので、**この通りに組み付けて
ください。** 違う位置に付けると、別の関節に命令が届いてしまいます。

```{figure} assembly_img/servo_ids.png
:target: assembly_img/servo_ids.png
:alt: 四脚ロボットを上と左から見た図に、各サーボの ID を書き込んだもの。右前 1・2、左前 3・4、右後 5・6、左後 7・8。それぞれ股が奇数、膝が偶数

サーボ ID の割り当て。上から見て、胴体の短い辺の中央に出っ張りがある側が前
（歩く向き）
```

下のユニットを組むときは、この ID のサーボを使います。

| ユニット | 入るサーボ | 使う ID |
|---|---|---|
| body_servo（胴体） | 4 本の脚の股 | 1（右前）、3（左前）、5（右後）、7（左後） |
| leg_right（右脚）×2 | 右の脚の膝 | 2（右前）、6（右後） |
| leg_left（左脚）×2 | 左の脚の膝 | 4（左前）、8（左後） |

### うまくいかないとき

| 症状 | 確かめること |
|---|---|
| `feetech scan` で何も見つからない | AC アダプタが差さっているか（PWR の LED）。ジャンパが B か。サーボのケーブルが奥まで差さっているか |
| ポートが見つからない | USB ケーブルがデータ通信対応か（充電専用のケーブルでは見えない） |
| 以前に通信速度を変えたサーボが見つからない | `feetech scan --all-baudrates` ですべての速度を試す |
| `id 2 is already used by another servo on this bus` | その ID のサーボが別につながっている。1 個だけにしてやり直す |

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
組み始める前に、**各サーボに ID を振っておく**こと（[サーボに ID を振る](#servo-id)）。
機体に組み込んでからだと、どのサーボがどれか見分けられない。

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
