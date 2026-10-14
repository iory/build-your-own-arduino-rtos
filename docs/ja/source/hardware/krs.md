# 近藤科学の KRS サーボで組む（RCB-4mini 版）

第13章の四脚ロボットは、Feetech の STS3215 の代わりに **近藤科学の ICS サーボ
（KRS-3302 ICS）** でも組めます。サーボは近藤科学のコントロールボード
**RCB-4mini** にまとめてつなぎ、Arduino は RCB-4mini に「この角度にして」と
頼む形になります。ファームウェアの制御ループと学習済みの方策は Feetech 版と
同じものが走ります。

```{raw} html
<figure style="margin:1.5rem auto; max-width:80%;">
  <video src="../_static/krs_walk.mp4" poster="../_static/krs_walk_poster.jpg" autoplay loop muted playsinline preload="metadata"
         style="width:100%; border-radius:8px;" aria-label="KRS サーボ版の四脚ロボットが廊下の床を歩く"></video>
  <figcaption style="font-size:0.9em;">KRS-3302 ICS ×8 と RCB-4mini で組んだ四脚ロボット。Ni-MH バッテリー（ROBO パワーセル E タイプ、7.2 V）1 本だけで、ケーブルをつながずに歩いている</figcaption>
</figure>
```

```{note}
胴体と脚の 3D プリント部品は、KRS サーボの形に合わせたもので、Feetech 版の
STL とは形が違います（STL は {doc}`krs_bom` にあります）。
このページでは、サーボの準備、3D ビューアでの組み立て、配線、書き込みを説明します。
```

(krs-v2)=
## 胴体の設計を更新しました（第 2 版）

3D ビューア・手順の図・STL は、次のように直した第 2 版の胴体です。このページの写真と
動画は第 1 版で撮ったもので、胴体の形が少し違います（配線と組み方は同じです）。

| | 第 1 版 | 第 2 版 |
|---|---|---|
| 股のサーボの向き | 4 個とも同じ向き（前後で非対称） | **前後対称**。4 個ともケースを胴体の中央へ向ける |
| 股の間隔（前後） | 150 mm（−90 / +60 mm） | **132 mm（±66 mm）** |
| 胴体の大きさ | 230 × 110 × 50 mm | **176 × 110 × 50 mm**。Bambu Lab A1 mini（180 mm 角）でも刷れる |
| バッテリー | — | **胴体の中**、Arduino の下の 27 mm のすき間に平置き |
| 蓋 | なし | **スナップフィットの蓋**（前が高い頭の形）。ネジなしで、爪 4 本で胴体の窓に掛かる |
| 基板の固定 | スナップフック（すき間 0） | 爪の下に 0.4 mm、横に 0.2 mm のすき間を足し、爪の先を 0.8 mm（4 層）に厚くした |

股のサーボを前後対称にしたのは、KRS-3302 が角度を測れるのが真ん中から ±135 度だけ
だからです（下の「なぜ真ん中に合わせるのか」）。前後の脚で、使う角度の範囲が同じに
なります。胴体の前にある丸い穴と台座は、カメラ（Arducam B0642）を付けるためのもので、
部品表と手順には入れていません。

## Feetech 版との違い

| | Feetech 版 | KRS 版（このページ） |
|---|---|---|
| サーボ | STS3215 ×8 | KRS-3302 ICS ×8 |
| サーボをまとめる基板 | Waveshare Bus Servo Adapter (A) | 近藤科学 RCB-4mini |
| ID を振る道具 | 基板の USB と `feetech` コマンド | **Dual USB アダプター HS** と `ics-manager` コマンド |
| Arduino との配線 | D0 / D1（Serial1） | **D8 / D9**（D0 / D1 は空けておく） |
| 電源 | 12 V | 近藤科学の AC アダプター（5.9 V）か、ケーブルなしで歩かせるときは ROBO パワーセル E タイプ（Ni-MH 7.2 V）。Arduino も同じ電源から |
| 書き込み | `pio run -e uno_r4_wifi` | `pio run -e uno_r4_wifi_rcb4` |

ID の振り方と、どの ID をどの関節に使うかは Feetech 版と同じです。

## 用意するもの

**{doc}`krs_bom` に、近藤科学の商品ページへのリンクと価格つきの部品表があります。**
近藤科学の部品をまとめて買うなら、サーボ 18 個・RCB-4mini・Dual USB アダプター HS・
バッテリー・充電器が入った **KXR アドバンスセット B Ver.2** がおすすめです。

```{figure} ../_static/krs_parts.jpg
:target: ../_static/krs_parts.jpg
:alt: 胴体、脚、ブラケットの 3D プリント部品、KRS サーボ 8 個、ホーン、ネジのケース

部品一式。KRS 版の 3D プリント部品、KRS-3302 ICS ×8、ホーン、ネジ
```

## Dual USB アダプター HS の使い方

Dual USB アダプター HS は、PC とサーボ（または RCB-4）を USB でつなぐための
近藤科学の純正アダプターです。**ICS モード**（サーボと話す）と **シリアルモード**
（RCB-4 と話す）の 2 つを切り替えて使います。このページで使うのは ICS モードだけです。

```{figure} ../_static/krs_dual_usb.jpg
:target: ../_static/krs_dual_usb.jpg
:width: 60%
:alt: DUAL USB ADAPTER HS と書かれた USB アダプター。ICS と Serial の切り替え表示がある

Dual USB アダプター HS。スイッチで ICS / Serial を切り替える
```

1. **ICS モードにする。** LED が赤なら ICS モード、緑ならシリアルモードです。
2. サーボを **1 個だけ** アダプターのケーブルにつなぐ。
3. アダプターを PC の USB に差す。

```{include} _tips/one_servo.md
```

```{figure} ../_static/krs_id_setup.jpg
:target: ../_static/krs_id_setup.jpg
:alt: ノート PC の USB に Dual USB アダプター HS を差し、そのケーブルの先に KRS-3302 サーボを 1 個つないだところ

PC → Dual USB アダプター HS → KRS-3302 を 1 個。これで ID を振る
```

### OS ごとの準備

macOS と Linux では、下で入れる `ics-manager` を使います。Windows では、近藤科学の
公式ソフト **ICS3.5/3.6 マネージャー** を使ってください。

| OS | 使うソフト | 準備 |
|---|---|---|
| Windows | [ICS3.5/3.6 マネージャー](https://kondo-robot.com/faq/ics35mag)（近藤科学の公式） | アダプターのドライバ（KO Driver）を入れる。使い方は [近藤科学の解説](https://kondo-robot.com/faq/how-to-use_ics3-5-manager) |
| macOS | `ics-manager` | `brew install libusb`。libusb 経由でアダプターに直接つなぐので、ドライバは要らない |
| Linux | `ics-manager` | アダプターを FTDI のシリアルとして認識させる。下のコマンドを 1 回実行する |

Linux では、`ics-manager` がつながらないときに自分でこの手順を表示します。

```console
$ sudo su
# modprobe ftdi-sio
# echo 165C 0008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
# exit
```

Windows の ICS3.5/3.6 マネージャーでも、確かめる項目（ID、通信速度、連続回転モード、
逆転モード）は下と同じです。

## サーボの設定を確かめて、ID を振る

### ics-manager を入れる

`ics-manager` は、ICS サーボの ID や設定を見たり書いたりするコマンドです。
[rcb4](https://github.com/iory/rcb4) という Python パッケージに入っています。
開発環境の準備で入れた uv で、次の 1 行で入ります
（uv がまだなら [macOS](../getting-started/macos.md) /
[Linux](../getting-started/linux.md) の「uv を入れる」を先に）。

```console
$ uv tool install rcb4
```

### 画面の見方

サーボを **1 個だけ** つないで `ics-manager` を実行すると、次の画面が出ます。
2 個以上つないだまま実行しないでください（上の「サーボは 1 個ずつつなぐ」）。

```console
$ ics-manager
--- Servo Status ---
>>  Current Servo ID: 2 -> Next Servo ID: [0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 ]
    Angle: -44
    Speed: 127
    Stretch: 90
    Baud Rate: 1.25Mbps
    Rotation Mode: Disabled
    Slave Mode: Disabled
    Reverse Mode: Disabled
    Serial Mode: Disabled
    Free: Enabled
----------------------
```

この四脚ロボットで **必ず確かめる行** は次の 4 つです。

| 行 | この機体で正しい値 | 違うと何が起きるか |
|---|---|---|
| `Current Servo ID` | 下の表の ID（1〜8） | 別の関節に命令が届く |
| `Baud Rate` | `1.25Mbps` | RCB-4mini と話せず、そのサーボだけ見つからない |
| `Rotation Mode` | **`Disabled`** | `Enabled` だと **連続回転（無限回転）モード**。角度ではなく回る速さを指示する車輪のようなサーボになり、関節として止まらない |
| `Reverse Mode` | **`Disabled`** | `Enabled` だと回る向きが逆になる。同じ型のサーボで 1 個だけ向きが違うと、その脚だけ逆に動く |

`Free: Enabled` は脱力している（力が入っていない）という意味で、ID を振るときは
このままでかまいません。`Angle` は今の出力軸の角度（度）で、手で軸を回すと変わります。

### ID を振る

1. `>>` が `Current Servo ID` の行にあることを確かめる（↑↓で移動）。
2. ←→ で緑色の数字を新しい ID に合わせ、**Enter** を押す。
3. `Current Servo ID:` の左の数字が新しい ID に変わったことを確かめる。
4. `Rotation Mode` と `Reverse Mode` が `Disabled`、`Baud Rate` が `1.25Mbps` で
   あることを確かめる。
5. `q` で終わり、**サーボに ID のラベルを貼る**。組み付けたあとに見える面に貼ると、
   配線や交換のときに困りません。
6. 次のサーボにつなぎ替えて、1 に戻る。

```{figure} ../_static/krs_set_id.gif
:alt: ics-manager の画面。Current Servo ID が 3 のサーボで、→ キーを 2 回押して緑色の数字を 2 に合わせ、Enter を押すと Current Servo ID が 2 に変わる

手順 1〜3 を実機で実行したところ。→ で緑色の数字を 2 に合わせて Enter を押すと、
ID 3 のサーボが ID 2 になる
```

ID はサーボの中の EEPROM に書かれるので、電源を切っても消えません。

```{include} _tips/eeprom.md
```

### Rotation Mode や Reverse Mode が Enabled だったら

- **Rotation Mode** は `r` キーで切り替わります。`Disabled` になるまで押してください。
- **Reverse Mode** は `v` キーで切り替わります。`Disabled` になるまで押してください。
  切り替える前にサーボを脱力させるので、軸が急に動くことはありません。

どちらも押すたびに EEPROM に書き込まれ、画面に `Rotation mode set to Disabled` の
ように結果が出ます。

### どのサーボをどこに使うか

ID の割り当ては Feetech 版と同じです。

```{figure} assembly_img/servo_ids.png
:target: assembly_img/servo_ids.png
:alt: 四脚ロボットを上と左から見た図に、各サーボの ID を書き込んだもの。右前 1・2、左前 3・4、右後 5・6、左後 7・8。それぞれ股が奇数、膝が偶数

サーボ ID の割り当て。上から見て、胴体の短い辺の中央に出っ張りがある側が前
```

## サーボを真ん中に合わせてから、ホーンと脚を付ける

サーボの出力軸にはホーンを付け、そこに脚をネジで止めます。

```{include} _tips/horn.md
```

ホーンを付ける向きは、**サーボを真ん中の角度（0 度）に動かしてから決めます。**

1. サーボを Dual USB アダプターにつなぎ、`ics-manager` を実行する。
2. **`z` を押す。** サーボが真ん中の角度（0 度、パルスの値で 7500）へ動き、
   その角度で止まります。
3. その状態のまま、**脚がまっすぐ真下を向く向き**（CAD の 0 度）でホーンをはめ、
   付属の M3-6 低頭ホーン止めビスで留める。膝は、先にホーンを足先にネジで止めておき、
   足先ごとはめる（下の {ref}`krs-assembly`）。

```{figure} ../_static/krs_servo_spline.jpg
:target: ../_static/krs_servo_spline.jpg
:width: 60%
:alt: ホーンを付ける前の KRS サーボ 2 個。出力軸のギザギザ（スプライン）が見える

ホーンを付ける前のサーボ。出力軸はギザギザ（スプライン）になっていて、ホーンは
ギザギザ 1 山ずつの向きにしか付かない
```

### なぜ真ん中に合わせるのか

KRS-3302 が角度を測れるのは、真ん中から **±135 度（合わせて 270 度）** の範囲だけです。

```{include} _tips/encoder.md
```

```{figure} ../_static/krs_servo_range.svg
:width: 100%
:alt: サーボの出力軸を上から見た図。真上が 0 度で、左右 135 度ずつ、合わせて 270 度の範囲が青く塗られ、下側の 90 度は測れない範囲として灰色の破線になっている。下にパルスの値 3500、7500、11500 と角度 −135 度、0 度、+135 度の対応

KRS-3302 が測れる・動ける範囲。真ん中（7500）で脚がまっすぐ真下を向くように付けておけば、
関節を動かしたい角度がこの範囲の中に収まる
```

この四脚ロボットでは、膝を立ち姿勢まで曲げると、脚がまっすぐのときから約 100 度
回ります。脚がまっすぐの向きを真ん中にしておけば、その角度も 270 度の範囲の中に
収まります。ホーンを大きくずらして付けると、曲げたい角度が範囲の外にはみ出して、
そこへは動けなくなります。

ギザギザ 1 山ぶんのずれは気にしなくてかまいません。組み上げたあと、脚をまっすぐ
伸ばしたときのサーボの値を測ってファームウェアに書く（下の「書き込んで、校正する」）
ので、小さなずれはそこで吸収されます。

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/krs_horn.jpg
:target: ../_static/krs_horn.jpg
:alt: KRS サーボと、外したホーン

サーボとホーン
```

:::
:::{grid-item}

```{figure} ../_static/krs_horn_screw.jpg
:target: ../_static/krs_horn_screw.jpg
:alt: 3D プリントの脚にホーンをネジ止めしているところ

ホーンを脚にネジ止めする。ドライバーの先はネジ穴と平行に当てる
```

:::
:::{grid-item}

```{figure} ../_static/krs_thigh.jpg
:target: ../_static/krs_thigh.jpg
:alt: ホーンを付けた太ももの部品と、サーボ

ホーンを付けた太もも
```

:::
:::{grid-item}

```{figure} ../_static/krs_bracket.jpg
:target: ../_static/krs_bracket.jpg
:alt: サーボを脚のブラケットに差し込み、ネジで止めたところ

サーボをブラケットに入れてネジで止める
```

:::
::::

(krs-assembly)=
## 組み立て

先に 4 種類のユニット（ホーン付きの股サーボ・サーボ入りの胴体・足先・脚）を組み、
最後に脚を胴体へ取り付けて、蓋をかぶせます。足先（脚ブラケット）は**先にホーンにネジで止めてから**、
ホーンごとサーボの出力軸にはめます。手順と図は、ネジまで入れた KRS 版の CAD から
自動で作ったものです。

ホーンをサーボにはめる前に、上の「サーボを真ん中に合わせてから、ホーンと脚を付ける」で
**サーボを真ん中（0 度）に合わせて**おいてください。

### インタラクティブ 3D ビューア

ブラウザ上で 1 ステップずつアニメーションを再生できます。マウスで視点を回し、
スライダーで手順を前後できます。

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../assembly/quadruped_krs/index.html"
     target="_blank" rel="noopener">ビューアを全画面で開く ↗</a>
  &nbsp;
  <a class="sd-btn sd-btn-outline-primary" href="../assembly/quadruped_krs/instructions.pdf"
     target="_blank" rel="noopener">PDF 版の手順書</a>
</p>
<iframe src="../assembly/quadruped_krs/index.html"
        style="width:100%; height:75vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="KRS 版四脚ロボット 組み立てビューア"></iframe>
```

(krs-screws)=
### ネジ

ネジはすべて近藤科学のもので、長さは近藤科学の資料の決め方に合わせてあります。

| ネジ | 本数 | 使う場所 | 長さの決め方 |
|---|---|---|---|
| **M3-6 低頭ホーン止めビス** | 8 | ホーン → サーボの出力軸 | サーボに 1 本ずつ付いてくる（近藤科学の取扱説明書「サーボホーンの取り付けについて」） |
| **M2-8 低頭ビス** | 8 | 胴体 → 股サーボのアッパーケース | アッパーケースのネジ穴（φ1.6 の下穴）は有効長 4.8mm。胴体の壁が 3.7mm なので、届く長さが 4.8mm 以内で一番長い 8mm |
| **M2-6 低頭ビス** | 8 | 脚リンク → 膝サーボのアッパーケース | 同じ決め方。脚リンクの板厚 2.0mm（座ぐりの底から）で 6mm |
| **M2-6 低頭ビス** | 16 | 脚ブラケット（足先） → 膝のホーン | 小径ホーン B のネジ穴は M2 のめねじで、厚み 2mm。ブラケットの板厚 4.0mm + 2mm = 6mm |
| **M2-4 低頭ビス** | 16 | 脚リンク → 股のホーン | 脚リンクの板厚 2.0mm + ホーン 2mm = 4mm |
| **ケースビス（2-20 低頭タッピングビス）** | 8 | 脚リンク → 膝サーボのボトムケース | 買わなくてよい。**買ってきたサーボに最初から締めてあるケースビス**を、いったん抜いて、脚リンクにはめたあとで同じネジで止め直す（近藤科学の指定） |

M2-4・M2-6・M2-8 の低頭ビスと M3-6 のホーン止めビスは、近藤科学の
[ビスセット A（KXR 用）](https://kondo-robot.com/product/02328) にまとめて入っています。
近藤科学の取扱説明書で「フラットヘッド」（2.6-4 フラットヘッドビス）が指定されているのは
フリーホーン側のネジで、このロボットでは使いません。

```{warning}
膝のボトムケース側は、サーボから抜いたケースビス（20mm）を脚リンク（座ぐりの底から
サーボまで約 3.5mm）ごと締めるので、**ケースビスがサーボにかかる長さが短くなります**。CAD で測ると、
下穴にかかるのは約 1.8mm です。締めすぎると下穴をなめるので、軽く締めて止めてください。
近藤科学の図は板厚 1mm のフレームでの例です。
```

### 部品のユニット構成

単一部品は全部で **90 個（11 種類）**。

| ユニット | 数量 | 単一部品の数 |
|---|---|---|
| body_servo_krs（胴体 + ホーン付きの股サーボ 4） | ×1 | 21 |
| foot_left_krs / foot_right_krs（足先 + ホーン） | 各 ×2 | 6 |
| leg_left_krs / leg_right_krs（脚。足先を含む） | 各 ×2 | 13 |

これに本体の組み立てで使う M2-4 低頭ビス 16 本と蓋 1 個を足して 90 個です。

| 部品 | 個数 |
|---|---|
| M2-6 低頭ビス | ×24 |
| M2-4 低頭ビス | ×16 |
| ケースビス（2-20 低頭タッピング） | ×8 |
| M2-8 低頭ビス | ×8 |
| M3-6 低頭ホーン止めビス | ×8 |
| KRS-3302 ICS（図では KRS3300_scale） | ×8 |
| 小径ホーン B（small_diameter_hornB） | ×8 |
| 脚ブラケット（bracket_outline_krs） | ×4 |
| 脚リンク（leg_link1_krs） | ×4 |
| 胴体（body_krs） | ×1 |
| 蓋（lid_krs） | ×1 |

図の **KRS3300-1〜4** は CAD 上の部品の通し番号で、サーボの ID ではありません。
上の「どのサーボをどこに使うか」の ID と、次のように対応します。

| ユニット | CAD の番号 → 位置 | 使う ID |
|---|---|---|
| body_servo_krs（胴体） | KRS3300-3 → 右前、KRS3300-4 → 左前、KRS3300-1 → 右後、KRS3300-2 → 左後 | 1（右前）、3（左前）、5（右後）、7（左後） |
| leg_right_krs（右脚）×2 | 右の脚の膝 | 2（右前）、6（右後） |
| leg_left_krs（左脚）×2 | 左の脚の膝 | 4（左前）、8（左後） |

### ユニットの事前組み立て

同じユニットは 1 回だけ手順を示します。**×N** はロボット全体で使う個数です。
上から順に組めば部品が揃います。図でオレンジの矢印が付いているのが、その手順で
付ける部品とネジです。

:::{dropdown} KRS3300（股のサーボにホーンを付ける） **×4**
:open:

股の 4 個（ID 1・3・5・7）だけです。膝のホーンは足先と一緒に付けます（下の foot と leg）。

1. **小径ホーン B** を置く（土台）

   ![KRS3300 step 1](krs_assembly_img/units/KRS3300/step_01.png)

2. **サーボ**をホーンへ — 真ん中に合わせたサーボの出力軸にはめる

   ![KRS3300 step 2](krs_assembly_img/units/KRS3300/step_02.png)

3. 🔩 **M3-6 低頭ホーン止めビス ×1** を締める（ホーン ↔ 出力軸）

   ![KRS3300 step 3](krs_assembly_img/units/KRS3300/step_03.png)

:::

:::{dropdown} body_servo_krs（胴体にサーボ 4 個を固定） **×1**

使う部品: 胴体 ×1、ホーン付きの股サーボ ×4、M2-8 低頭ビス ×8

サーボは胴体の内側から入れ、ホーンを胴体の壁の丸穴から外へ出します。
ネジは胴体の外側から、壁を通してアッパーケース（出力軸側）のネジ穴に締めます。

1. **body_krs**（胴体）を置く（土台）

   ![body_servo step 1](krs_assembly_img/units/body_servo_krs/step_01.png)

2. **KRS3300-4**（左前・ID 3）— 胴体へ差し込む（ホーンを壁の穴へ、同軸 φ2.3mm ×2、面合わせ ×2）

   ![body_servo step 2](krs_assembly_img/units/body_servo_krs/step_02.png)

3. 🔩 **M2-8 低頭ビス ×2** を締める（サーボ ↔ 胴体）

   ![body_servo step 3](krs_assembly_img/units/body_servo_krs/step_03.png)

4. **KRS3300-3**（右前・ID 1）— 胴体へ差し込む

   ![body_servo step 4](krs_assembly_img/units/body_servo_krs/step_04.png)

5. 🔩 **M2-8 低頭ビス ×2** を締める

   ![body_servo step 5](krs_assembly_img/units/body_servo_krs/step_05.png)

6. **KRS3300-2**（左後・ID 7）— 胴体へ差し込む

   ![body_servo step 6](krs_assembly_img/units/body_servo_krs/step_06.png)

7. 🔩 **M2-8 低頭ビス ×2** を締める

   ![body_servo step 7](krs_assembly_img/units/body_servo_krs/step_07.png)

8. **KRS3300-1**（右後・ID 5）— 胴体へ差し込む

   ![body_servo step 8](krs_assembly_img/units/body_servo_krs/step_08.png)

9. 🔩 **M2-8 低頭ビス ×2** を締める

   ![body_servo step 9](krs_assembly_img/units/body_servo_krs/step_09.png)

:::

:::{dropdown} foot_left_krs / foot_right_krs（足先にホーンを止める） **各 ×2**

使う部品: 脚ブラケット ×1、小径ホーン B ×1、M2-6 低頭ビス ×4

サーボにはめる前に、ホーンを足先（脚ブラケット）に止めます。左右で手順は同じで、
ホーンを付ける面が鏡像になります。

1. **小径ホーン B** を置く（土台）

   ![foot step 1](krs_assembly_img/units/foot_left_krs/step_01.png)

2. **bracket_outline_krs**（脚ブラケット）— ホーンに合わせる（同軸 φ8.4mm、同軸 φ2.3mm、面合わせ）

   ![foot step 2](krs_assembly_img/units/foot_left_krs/step_02.png)

3. 🔩 **M2-6 低頭ビス ×4** を締める（脚ブラケット ↔ ホーン）

   ![foot step 3](krs_assembly_img/units/foot_left_krs/step_03.png)

:::

:::{dropdown} leg_left_krs / leg_right_krs（脚） **各 ×2**

使う部品: 膝のサーボ（KRS-3302）×1、足先 ×1、脚リンク ×1、M3-6 低頭ホーン止めビス ×1、
M2-6 低頭ビス ×2、ケースビス ×2（サーボに最初から締めてあるもの）。右脚は足先が
foot_right_krs になるだけで、手順は同じです。

1. **KRS3300_scale**（膝のサーボ。真ん中に合わせておく）を置く（土台）

   ![leg step 1](krs_assembly_img/units/leg_left_krs/step_01.png)

2. **foot_left_krs**（ホーン付きの足先）— 脚がまっすぐ伸びる向きで、ホーンを出力軸にはめる

   ![leg step 2](krs_assembly_img/units/leg_left_krs/step_02.png)

3. 🔩 **M3-6 低頭ホーン止めビス ×1** を、脚ブラケットの真ん中の穴から締める（ホーン ↔ 出力軸）

   ![leg step 3](krs_assembly_img/units/leg_left_krs/step_03.png)

4. **leg_link1_krs**（脚リンク）— まず、サーボのボトムケース側（出力軸と反対側）の
   ケースビスのうち、脚リンクの穴に重なる 2 本をサーボから**抜いておく**。それから、
   サーボを脚リンクの間に差し込む（同軸 φ2.3mm ×4、面合わせ ×2）

   ![leg step 4](krs_assembly_img/units/leg_left_krs/step_04.png)

5. 🔩 **ケースビス ×2** — 手順 4 で抜いたケースビスを、脚リンクの座ぐりから通して
   サーボに締め直す

   ![leg step 5](krs_assembly_img/units/leg_left_krs/step_05.png)

6. 🔩 **M2-6 低頭ビス ×2** を締める（脚リンク ↔ アッパーケース）

   ![leg step 6](krs_assembly_img/units/leg_left_krs/step_06.png)

:::

### 本体の組み立て

事前に組んだユニットを胴体（body_servo_krs）に取り付けます。脚リンクの上の端を
股のホーンに合わせ、脚リンクの外側の穴から M2-4 低頭ビスでホーンに留めます。
股のサーボも真ん中のままにして、脚がまっすぐ真下を向く向きで合わせます。

#### Step 1: body_servo_krs を置く

![Step 1](krs_assembly_img/step_001.png)

#### Step 2: leg_right_krs（1 本目・右前）を取り付ける

右前の股のホーン（KRS3300-3）へ、脚リンクを合わせます（同軸 φ8.4mm、同軸 φ2.3mm ×2）。

![Step 2](krs_assembly_img/step_002.png)

#### Step 3: 🔩 M2-4 低頭ビス ×4 を締める

![Step 3](krs_assembly_img/step_003.png)

#### Step 4: leg_right_krs（2 本目・右後）を取り付ける

![Step 4](krs_assembly_img/step_004.png)

#### Step 5: 🔩 M2-4 低頭ビス ×4 を締める

![Step 5](krs_assembly_img/step_005.png)

#### Step 6: leg_left_krs（1 本目・左後）を取り付ける

反対側の股のホーンへ合わせます。差し込む向きが右脚と逆になります。

![Step 6](krs_assembly_img/step_006.png)

#### Step 7: 🔩 M2-4 低頭ビス ×4 を締める

![Step 7](krs_assembly_img/step_007.png)

#### Step 8: leg_left_krs（2 本目・左前）を取り付ける

![Step 8](krs_assembly_img/step_008.png)

#### Step 9: 🔩 M2-4 低頭ビス ×4 を締める

![Step 9](krs_assembly_img/step_009.png)

#### Step 10: lid_krs（蓋）をかぶせる

蓋は、配線（下の「配線」）を済ませ、バッテリーと基板を胴体に入れてから最後に
かぶせます。蓋の縁を胴体の上の縁に合わせて真上から押すと、左右 2 本ずつの爪が胴体の
側面の窓（蓋爪窓）にパチンと掛かります。外すときは、側面の窓から爪の先を内側へ押しながら
蓋を持ち上げます。ネジは使いません。

![Step 10](krs_assembly_img/step_010.png)

これで機体は完成です。

## 胴体に組み付ける

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/krs_body.jpg
:target: ../_static/krs_body.jpg
:alt: 胴体の中に股のサーボ 4 個、RCB-4mini、Arduino UNO R4 WiFi を置いたところ

胴体に股のサーボ 4 個、RCB-4mini、Arduino UNO R4 WiFi を置く
```

:::
:::{grid-item}

```{figure} ../_static/krs_body_wired.jpg
:target: ../_static/krs_body_wired.jpg
:alt: 胴体の中でサーボのケーブルを RCB-4mini につないだところ

サーボのケーブルを RCB-4mini へ
```

:::
::::

## 配線

### RCB-4mini の各部

```{figure} ../_static/krs_ref_rcb4mini_ports.png
:target: ../_static/krs_ref_rcb4mini_ports.png
:alt: RCB-4mini の各部の名称の図。SIO ポートは左の列が SIO3・SIO2・SIO1、右の列が SIO7・SIO6・SIO5。右に AD ポート AD1〜AD5、下に電源端子と COM ポート。SIO ポートのピンは SIO・Vcc・GND、COM ポートのピンは GND・Rx・Tx

RCB-4mini の各部の名称（出典：近藤科学「HeartToHeart4 取扱説明書 Ver.8」7 ページ）
```

| ポート | 使い方 |
|---|---|
| SIO1〜3、SIO5〜7 | サーボをつなぐ。ピンは SIO（信号）・Vcc（電池の電圧）・GND |
| COM | Arduino とつなぐ。ピンは GND 側から GND・Rx・Tx |
| 電源端子 | バッテリーをつなぐ |
| AD1〜AD5 | 使わない |

### サーボ → RCB-4mini

サーボは SIO ポートにつなぎ、サーボどうしは数珠つなぎにできます。RCB-4 は、つないだ
サーボを **ICS 番号** で区別します。ICS 番号は、サーボの ID と、どちらの系統の
SIO ポートにつないだかで決まります。

| つないだ SIO ポート | ICS 番号 | 例：ID 3 のサーボ |
|---|---|---|
| SIO1〜3 | ID × 2 | 6 |
| SIO5〜7 | ID × 2 + 1 | 7 |

```{figure} ../_static/krs_ref_ics_number.png
:target: ../_static/krs_ref_ics_number.png
:alt: ICS 番号はサーボ ID × 2（SIO1〜4 に接続の場合）、サーボ ID × 2 + 1（SIO5〜8 に接続の場合）という説明と、ICS0〜ICS7 のビットの並び

ICS 番号の決まり方（出典：近藤科学「RCB-4HV コマンドリファレンス」17 ページ、
RCB-4 リファレンスセット Ver.2.2 所収）。RCB-4HV は SIO が 1〜4 と 5〜8 の 8 個、
RCB-4mini は 1〜3 と 5〜7 の 6 個で、決まり方は同じ
```

ファームウェアは起動時に両方の系統を調べるので、**どちらの系統に挿してもかまいません。**
起動時の表示では、SIO1〜3 側を「右」、SIO5〜7 側を「左」と出します。

### つなぐもの

```{figure} ../_static/krs_wiring.jpg
:target: ../_static/krs_wiring.jpg
:width: 70%
:alt: 胴体の中の配線全体。番号 1 が RCB-4mini、2 が Arduino、3 がバッテリー、4 と 5 が ZH接続ケーブル2 Bタイプとジャンパワイヤ

配線の全体。番号は下の表と対応する
```

| 番号 | もの | つなぎ先 |
|---|---|---|
| 1 | RCB-4mini | SIO ポートにサーボ 8 個、COM ポートに 4、空いた SIO ポートに 5、電源端子にバッテリー |
| 2 | Arduino UNO R4 WiFi | D8・D9・GND に 4、VIN に 5 |
| 3 | バッテリー（ROBO パワーセル E タイプ（Ni-MH 7.2 V））か AC アダプター | RCB-4mini の電源端子 |
| 4 | ZH接続ケーブル2 Bタイプ ＋ ジャンパワイヤ 3 本（COM 用） | RCB-4mini の COM ポート → Arduino の D8・D9・GND |
| 5 | ZH接続ケーブル2 Bタイプ ＋ ジャンパワイヤ 1 本（電源用） | RCB-4mini の空いた SIO ポートの Vcc → Arduino の VIN |

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/krs_rcb4_wiring.jpg
:target: ../_static/krs_rcb4_wiring.jpg
:alt: RCB-4mini まわりに番号を付けた写真。1 が SIO1〜3、2 が SIO5〜7、3 が AD ポート、4 が COM ポート、5 が電源端子

RCB-4mini まわり。1：SIO1〜3、2：SIO5〜7、3：AD ポート（使わない）、
4：COM ポート、5：電源端子
```

:::
:::{grid-item}

```{figure} ../_static/krs_uno_wiring.jpg
:target: ../_static/krs_uno_wiring.jpg
:alt: Arduino UNO R4 WiFi に番号を付けた写真。1 が D8・D9 に挿したジャンパワイヤ、2 が VIN と GND に挿したジャンパワイヤ

Arduino 側。1：D8・D9（RCB-4 の COM へ）、2：VIN・GND（SIO ポートの電源）
```

:::
::::

### RCB-4mini の COM → Arduino

| RCB-4mini COM | Arduino UNO R4 WiFi |
|---|---|
| Rx（GND の隣） | **D9** |
| Tx（いちばん奥） | **D8** |
| GND | GND |

送る側（Arduino の D9）を受ける側（RCB-4 の Rx）へ、という普通の交差のつなぎ方です。
Feetech 版のボードとは違って、TX どうし・RX どうしではありません。

```{note}
D0 / D1 は Arduino のハードウェアシリアル（Serial1）のピンです。RCB-4 の COM ポートは
信号が反転した特殊なシリアル（1.25 Mbps）で Serial1 では話せないため、ファームウェアは
D8 / D9 をタイマーと DMA で直接動かして話します。D0 / D1 はほかの機器に使えます。
```

### 電源

電源は 2 通りあります。どちらも RCB-4mini の **電源端子** に入れ、サーボと Arduino には
そこから配ります。

| | AC アダプター | バッテリー |
|---|---|---|
| 使うもの | 近藤科学の **AC アダプター（5.9 V 2 A）**。付属の LV 変換 DC ジャックを付ける | **ROBO パワーセル E タイプ（Ni-MH 7.2 V）**（KXR アドバンスセット B に入っている） |
| 電圧 | 5.9 V | 公称 7.2 V |
| 向いている使い方 | 机の上で何度も試す。電池切れを気にしなくてよい | ケーブルなしで歩かせる |

LV 変換 DC ジャックの先はバッテリーと同じ VH 2 ピンのコネクターなので、バッテリーを
挿すところにそのまま挿せます。

1. AC アダプターかバッテリーを RCB-4mini の **電源端子** につなぐ。サーボの電源はここから
   SIO ポート経由で配られます。
2. **空いている SIO ポート** の **Vcc を Arduino の VIN** へつなぐ。SIO ポートの Vcc には
   電源端子の電圧がそのまま出ています。GND は COM ポートの GND でつながっています。
   **SIO ポートの SIO（信号）ピンはつながないでください**（サーボの通信線そのものです）。

USB ケーブルを同時に差していても問題ありません（理由は下の「VIN と USB を同時に
つないでよい理由」）。書き込みのときに外す必要はありません。

```{warning}
Arduino の VIN が受け付けるのは 6〜24 V です。

- **AC アダプター**の 5.9 V はこの範囲を少し下回ります。Arduino の 5 V が下がることが
  あるので、**AC アダプターのときは USB ケーブルも差しておいてください。** 足りない分は
  USB から入ります。
- **バッテリー**が減って 6 V を切ったときも同じです。その前に充電してください。
```

AC アダプターは 2 A までです。サーボ 8 個が同時に強く踏ん張ると足りなくなることがあり、
近藤科学の商品ページにも、サーボの数や動きの負荷によっては正常に動かないことがある、
とあります。歩かせている最中に RCB-4mini や Arduino がリセットするなら、バッテリーで
試してください。

#### VIN と USB を同時につないでよい理由

UNO R4 WiFi の回路図（電源まわり）の抜粋です。

```{figure} ../_static/uno_r4_wifi_power_schematic.png
:target: ../_static/uno_r4_wifi_power_schematic.png
:alt: UNO R4 WiFi の回路図の電源部分。左から DC ジャック J5、逆接続保護のショットキーダイオード D1、降圧コンバーター U3（ISL854102）、コイル L3 を経て +5V。右上の VUSB からショットキーダイオード D2 を通って同じ +5V へ

Arduino UNO R4 WiFi 回路図（ABX00087）の DC JACK・BUCK CONVERTER・USB SCHOTTKY の部分。
出典：Arduino SA、CC BY-SA 4.0
```

ピンヘッダーの VIN は、DC ジャック（J5）と同じ `VIN` の線です。電気の通り道は次のように
なっています。

```text
VIN ピン / DC ジャック ──D1──> 降圧コンバーター U3 ──> +5V ──> マイコン・3.3 V レギュレーター
USB-C の VBUS ─────────D2─────────────────────────> +5V
```

- **D1、D2 はショットキーダイオード**（PMEG6020AELRX）で、電流を矢印の向きにしか
  流しません。+5V には 2 つの電源がダイオードを挟んでつながっていて、電圧の高いほうから
  電気が入ります。
- VIN に電圧があると、降圧コンバーター U3 が +5V を 5.0 V に保ちます。USB 側は D2 で
  電圧が下がって約 4.7 V しか出せないので、D2 には逆向きの電圧がかかり、USB からは
  電流が流れません。**+5V から PC の USB へ流れ込むこともありません**（D2 が止める）。
- USB だけのときは、+5V が U3 の中を通って VIN 側へ漏れても D1 で止まるので、
  **USB からバッテリーや AC アダプターのほうへ流れることもありません。**
- VIN が 6 V より下がると U3 は 5 V を保てなくなりますが、USB を差していれば、
  +5V が USB 側の約 4.7 V より下がった分を D2 から USB が補います。上の warning で
  AC アダプターのときに USB を差しておく理由です。

### 下側の配線

膝のサーボのケーブルは、胴体の下を通して中へ入れます。ふたを閉めたあと、
下から見て次のようになっているか確かめてください。

```{figure} ../_static/krs_done.jpg
:target: ../_static/krs_done.jpg
:width: 70%
:alt: 組み上がった機体を下から見た写真。1 が四隅の膝のサーボ、2 がケーブルを胴体の中へ通す穴、3 がケーブルを留めるところ

下から見たところ。1：膝のサーボ（4 個）、2：ケーブルを胴体の中へ通す穴、
3：ケーブルを脚に沿わせて留めるところ
```

脚を動かしたときにケーブルが引っ張られたり、挟まれたりしないよう、留めるところ（3）で
ケーブルを脚に沿わせておきます。

## 書き込んで、校正する

ここからは {doc}`walk` と同じ流れです。違うのは、書き込むときの env と、校正の値を
書くファイルだけです。

1. **書き込む。** 校正する前のファームウェアは、サーボの角度を読むだけで、
   目標の角度は送りません。

   ```console
   $ uv run pio run -d 13_quadruped -e uno_r4_wifi_rcb4 -t upload
   ```

   起動するとシリアルモニタに、どの関節のサーボが RCB-4 の何番で見つかったかが
   出ます。`サーボ応答: 8 / 8` になっていることを確かめてください。

   ```text
   FL_hip id 3 -> 右 #6
   FL_knee id 4 -> 右 #8
   ...
   サーボ応答: 8 / 8
   ```

2. **脱力させる。** `free` を送ると全部の関節の力が抜けます。
3. **ゼロ点を測る。** 機体を吊るし、4 本とも脚をまっすぐ真下に伸ばして `raw` を
   送ります。関節ごとのパルス（中央が 7500）が出るので、それを
   `include/quad_calib_rcb4.h` の `QUAD_RCB4_ZERO` に書きます。
4. **向きを確かめる。** 股だけを動かして足先を後ろへ振り、`raw` の値が増えるか
   減るかを見ます。膝も同じように確かめます。ゼロ点より **減った** 関節は
   `QUAD_RCB4_SIGN` を `-1` にします（左の脚が `-1`、右の脚が `+1` になるはずです）。
5. `QUAD_RCB4_CALIBRATED` を `1` にして、もう一度書き込む。**起動するとすぐに 2 秒
   かけて立ち姿勢へ動く** ので、機体は吊るしたままにしてください。
6. 吊るしたまま `rl 0.06 0` を送り、4 本の脚が交互に足踏みすれば完成です。床に
   下ろして歩かせるのは、そのあとです。

キーボードで歩かせる方法（`quad_host.py serial`）と、WiFi で歩かせる版
（`-e uno_r4_wifi_rcb4_udp`）は、
[code/13_quadruped/README.md](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/README.md)
にあります。

## KRS 版の歩行方策

KRS 版には、Feetech 版とは別に学習した歩行方策があります。KRS-3302 のトルクは
0.54〜0.66 N·m（電源 5.9〜7.4 V）で、Feetech 版の STS3215（2.94 N·m）の 4 分の 1 以下です。
そのため、機体のモデル・関節の範囲（±135°）・質量（実測 610.8 g）をすべて KRS 版に合わせて、
最初から学習しました。観測には IMU（胴体の角速度と重力の向き）が入ります。

### ブラウザで歩かせてみる

{doc}`walk` と同じシミュレーションを、KRS 版の機体と方策で動かします。
**歩く** を押すと、「前進」と「旋回」の指令で歩きます。

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../assembly/quadruped/walk/index.html?robot=krs"
     target="_blank" rel="noopener">KRS 版のシミュレーションを開く ↗</a>
</p>
<iframe src="../assembly/quadruped/walk/index.html?robot=krs"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="KRS 版四脚ロボット 歩行シミュレーション"></iframe>
```

シミュレーション（64 台 × 10 秒）での成績です。

| 指令 | 実測 | 胴体の傾き（99 %） |
|---|---|---|
| 前進 0.04 m/s | 0.040 m/s | 4.1° |
| 前進 0.08 m/s | 0.083 m/s | 3.1° |
| 前進 0.12 m/s | 0.122 m/s | 3.7° |
| 後退 0.06 m/s | 0.055 m/s | 5.4° |
| 旋回 0.4 rad/s（前進 0.08 m/s） | 0.066 rad/s | 4.2° |

- 対角の 2 本ずつが交互に接地するトロットで、4 本とも 1 秒に 3.2〜3.9 歩踏みます。
- 胴体と膝は床に着きません。4 本とも浮く時間はほぼありません（0.1 % 以下）。
- 関節は ±135° に対して 32° 以上の余裕があります。トルクは 99 % 値で 0.33 N·m 以下です
  （最大トルクの約 5 割）。
- **旋回は苦手です。** 外転の関節が無いので、左右の歩幅の差で曲がるしかなく、
  指令の 2 割ほどしか回りません。

### 書き込む

```bash
cd code
uv run pio run -d 13_quadruped -e uno_r4_wifi_rcb4_krs -t upload       # USB シリアル
uv run pio run -d 13_quadruped -e uno_r4_wifi_rcb4_udp_krs -t upload   # WiFi
```

方策は `include/krs_quad_policy.h` です。Feetech 版の `arduino_quad_policy.h` とは混ざりません。
home の姿勢は股 +53.9°、膝 −89.3°（胴体の底面が床から 0.13 m）で、Feetech 版とは違います。

```{warning}
IMU が必要です。IMU の値は胴体の座標（x 前・y 左・z 上、水平で静止して重力が (0, 0, −1)）で
方策に渡します。センサ基板の取り付けの向きが Feetech 版と違うときは、
`src/quad_imu.cpp` のチップから胴体への回転を、KRS の胴体に合わせてください。
```

学習に使った値のうち、次は実測していない**仮定**です。

- サーボの位置ループのゲイン（kp 5.5 N·m/rad、kd 0.11）。学習では 0.5〜2 倍でばらつかせた
- 指令が届くまでの遅れ（20〜40 ms）
- 電池の位置と Arduino UNO R4 WiFi の質量（25 g）

学習のしかたは `code/13_quadruped/rl/README.md` の「KRS 版」にあります。

## うまくいかないとき

| 症状 | 確かめること |
|---|---|
| `ics-manager` が `Connection is not open.` のまま | アダプターの LED が赤（ICS モード）か。サーボを 1 個だけつないでいるか。macOS なら libusb、Linux なら上の `new_id` |
| 起動時に一部の関節が `見つからない` | そのサーボの ID と `Baud Rate`（1.25Mbps）を `ics-manager` で確かめる。ケーブルが奥まで差さっているか |
| 1 本の脚だけ逆に動く | そのサーボの `Reverse Mode` が `Enabled` になっていないか（`ics-manager` の `v` で戻す）。`QUAD_RCB4_SIGN` の値 |
| 関節が止まらずに回り続ける | そのサーボの `Rotation Mode` が `Enabled`（連続回転モード）になっていないか（`ics-manager` の `r` で戻す） |
| 関節が途中までしか曲がらない | ホーンを大きくずらして付けていないか。上の「サーボを真ん中に合わせてから、ホーンと脚を付ける」からやり直す |
| 歩いている最中に Arduino がリセットする | バッテリーの電圧。6 V を切っていないか。AC アダプターなら USB ケーブルも差しているか、バッテリーに替えるとどうか |

```{admonition} RCB-4mini に書き込まれたプロジェクトについて
:class: tip

RCB-4mini は、近藤科学の Heart to Heart 4 で書き込んだプロジェクトに「割り当て」られた
サーボとしか話しません。ファームウェアは起動時に、見つからない関節のサーボを自分で
割り当てるので、Heart to Heart 4 でプロジェクトを作り直す必要はありません
（RCB-4mini の RAM に書くだけで、中に保存されたプロジェクトは書き換えません）。
```

## 出典

- RCB-4mini の電源電圧（6〜12 V）: <https://kondo-robot.com/product/rcb4_mini>
- RCB-4mini の各部の名称（SIO / AD / COM / 電源端子、ピンの並び）の図:
  近藤科学「HeartToHeart4 取扱説明書 Ver.8」6〜7 ページ <https://www.kondokagaku.jp/data_download/HeartToHeart4_manual_Ver8_JP.pdf>
- ICS 番号の決まり方の図、ICS の割り当て表（RAM `$0044`）: 近藤科学「RCB-4HV コマンドリファレンス」17 ページと
  「RCB-4HV ファームウェアリファレンス」（RCB-4 リファレンスセット Ver.2.2 所収）<https://kondo-robot.com/faq/rcb-4-reference-ver-2_2>
- Dual USB アダプター HS（LED 赤が ICS、緑がシリアル）: <https://kondo-robot.com/product/02116>
- ICS3.5/3.6 マネージャー（Windows）: <https://kondo-robot.com/faq/ics35mag>、
  使い方 <https://kondo-robot.com/faq/how-to-use_ics3-5-manager>
- KRS-3302 の動作角 270 度（±135 度）: <https://kondo-robot.com/product/03146>、
  KRS シリーズ取扱説明書 V2.1 <https://kondo-robot.com/w/wp-content/uploads/KRS-series_manual_Download-V2_1.pdf>
- 位置の値 3500〜11500（中央 7500）: ICS3.5/3.6 ソフトウェアマニュアル v2.9
  <https://kondo-robot.com/w/wp-content/uploads/ICS3.5_3.6_SoftwareManual_2_9.pdf>
- 新品の KRS サーボの ID（0）: KRS シリーズ取扱説明書 V2.1（上と同じ）
- ROBO パワーセル E タイプ（Ni-MH 6 セル、公称 7.2 V、800 mAh、VH 2 ピン）: <https://kondo-robot.com/product/02335>
- Arduino UNO R4 WiFi の VIN（6〜24 V）、VUSB（4.8〜5.5 V）、USB 給電時の約 4.7 V、
  D1・D2 の品番: <https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf>
  （2 章「Recommended Operating Conditions」、11 章「Power Options」）
- Arduino UNO R4 WiFi の回路図（電源まわりの図の出典、CC BY-SA 4.0）:
  <https://docs.arduino.cc/resources/schematics/ABX00087-schematics.pdf>
- AC アダプター（5.9 V 2 A、品番 04052、LV 変換 DC ジャック付属、サーボの数や負荷で
  正常に動かないことがあるという注意）: <https://kondo-robot.com/product/04052>
- LV 変換 DC ジャック（VH 2 ピン ⇔ DC プラグ 5.5 × 2.1 mm）: <https://kondo-robot.com/product/02186>
- ホーン止めビス（KRS-3300 シリーズは M3-6 低頭ホーン止めビスが付属）、ホーン用ビス、
  フリーホーン側だけ 2.6-4 フラットヘッドビス: KRS シリーズ取扱説明書 V2.1 の 10 ページ
  「サーボホーンの取り付けについて」（上と同じ）
- フレーム取り付けビスの長さ（2-4 + フレーム厚、アッパーケースの下穴有効長 4.8mm、
  ボトムケースはケースビス 2-20 低頭タッピングビス）: 近藤科学「フレーム取り付けビス参考図
  KRS-3300 シリーズ」<https://kondo-robot.com/w/wp-content/uploads/KRS-3300_Frame-BISS-A4-0809.pdf>
  （<https://kondo-robot.com/faq/krs-3300dimention> から）
- アッパーケースには 2mm のビス、ボトムケースはケースビスを外して共締め:
  <https://kondo-robot.com/product/03146>
- 小径ホーン B（PCD φ12・M2）: <https://kondo-robot.com/product/02157>
- ビスセット A（KXR 用）の中身: <https://kondo-robot.com/product/02328>
- ケースビスセット KRS-3300 シリーズ用（2-20 タッピングビス）: <https://kondo-robot.com/product/02183>
- 板厚・ホーンのネジ穴の厚み・ケースビスと M3 ホーン止めビスのかかりは、KRS 版の CAD
  （SolidWorks）で測った値
- `ics-manager` の表示とキー操作: `rcb4/ics.py` <https://github.com/iory/rcb4>。
  逆転モードの `v` キーは <https://github.com/iory/rcb4/pull/232> で追加され、
  PyPI の rcb4 0.1.4 <https://pypi.org/project/rcb4/0.1.4/> に入っている
