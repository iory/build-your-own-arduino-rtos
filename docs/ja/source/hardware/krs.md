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
STL とは形が違います。KRS 版の CAD と組み立てのページは準備中です。
このページでは、サーボの準備・配線・書き込みを説明します。
```

## Feetech 版との違い

| | Feetech 版 | KRS 版（このページ） |
|---|---|---|
| サーボ | STS3215 ×8 | KRS-3302 ICS ×8 |
| サーボをまとめる基板 | Waveshare Bus Servo Adapter (A) | 近藤科学 RCB-4mini |
| ID を振る道具 | 基板の USB と `feetech` コマンド | **Dual USB アダプター HS** と `ics-manager` コマンド |
| Arduino との配線 | D0 / D1（Serial1） | **D8 / D9**（D0 / D1 は空けておく） |
| 電源 | 12 V | ROBO パワーセル E タイプ（Ni-MH 7.2 V） 1 本で、Arduino も同じ電池から |
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
   ホーンと脚をネジで止める。

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
| 3 | バッテリー（ROBO パワーセル E タイプ（Ni-MH 7.2 V）） | RCB-4mini の電源端子 |
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

近藤科学の **ROBO パワーセル E タイプ（Ni-MH 7.2 V）** 1 本で、サーボ・RCB-4mini・Arduino をまとめて動かします
（KXR アドバンスセット B に入っているバッテリーです）。

1. バッテリーを RCB-4mini の **電源端子** につなぐ。サーボの電源はここから SIO ポート
   経由で配られます。
2. **空いている SIO ポート** の **Vcc を Arduino の VIN** へつなぐ。SIO ポートの Vcc には
   バッテリーの電圧（公称 7.2 V）がそのまま出ていて、Arduino の VIN は 6〜24 V を
   受け付けます。GND は COM ポートの GND でつながっています。
   **SIO ポートの SIO（信号）ピンはつながないでください**（サーボの通信線そのものです）。

USB ケーブルを同時に差していても問題ありません。書き込みのときに外す必要はありません。

```{warning}
バッテリーが減って電圧が 6 V を切ると、Arduino の VIN の範囲を外れます。
その前に充電してください。
```

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

## うまくいかないとき

| 症状 | 確かめること |
|---|---|
| `ics-manager` が `Connection is not open.` のまま | アダプターの LED が赤（ICS モード）か。サーボを 1 個だけつないでいるか。macOS なら libusb、Linux なら上の `new_id` |
| 起動時に一部の関節が `見つからない` | そのサーボの ID と `Baud Rate`（1.25Mbps）を `ics-manager` で確かめる。ケーブルが奥まで差さっているか |
| 1 本の脚だけ逆に動く | そのサーボの `Reverse Mode` が `Enabled` になっていないか（`ics-manager` の `v` で戻す）。`QUAD_RCB4_SIGN` の値 |
| 関節が止まらずに回り続ける | そのサーボの `Rotation Mode` が `Enabled`（連続回転モード）になっていないか（`ics-manager` の `r` で戻す） |
| 関節が途中までしか曲がらない | ホーンを大きくずらして付けていないか。上の「サーボを真ん中に合わせてから、ホーンと脚を付ける」からやり直す |
| 歩いている最中に Arduino がリセットする | バッテリーの電圧。6 V を切っていないか |

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
- Arduino UNO R4 WiFi の VIN（6〜24 V）: <https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf>
- `ics-manager` の表示とキー操作: `rcb4/ics.py` <https://github.com/iory/rcb4>。
  逆転モードの `v` キーは <https://github.com/iory/rcb4/pull/232> で追加され、
  PyPI の rcb4 0.1.4 <https://pypi.org/project/rcb4/0.1.4/> に入っている
