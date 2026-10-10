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
  <figcaption style="font-size:0.9em;">KRS-3302 ICS ×8 と RCB-4mini で組んだ四脚ロボット。2S LiFe バッテリー 1 本だけで、ケーブルをつながずに歩いている</figcaption>
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
| 電源 | 12 V | 2S LiFe（6.6 V）1 本で、Arduino も同じ電池から |
| 書き込み | `pio run -e uno_r4_wifi` | `pio run -e uno_r4_wifi_rcb4` |

ID の振り方と、どの ID をどの関節に使うかは Feetech 版と同じです。

## 用意するもの

```{figure} ../_static/krs_parts.jpg
:target: ../_static/krs_parts.jpg
:width: 60%
:alt: 胴体、脚、ブラケットの 3D プリント部品、KRS サーボ 8 個、ホーン、ネジのケース

部品一式。KRS 版の 3D プリント部品、KRS-3302 ICS ×8、ホーン、ネジ
```

| 部品 | 数 | 役目 |
|---|---|---|
| 近藤科学 KRS-3302 ICS | 8 | 関節のサーボ |
| 近藤科学 RCB-4mini | 1 | 8 個のサーボをまとめて動かす基板 |
| 近藤科学 Dual USB アダプター HS | 1 | PC からサーボに ID を振る。組み上げたあとは使わない |
| 近藤科学の 2S LiFe バッテリー（6.6 V） | 1 | サーボ・RCB-4mini・Arduino の電源 |
| Arduino UNO R4 WiFi | 1 | 制御ループと方策を回す |
| ZH 3 ピンのケーブル、ジャンパワイヤ | 少々 | RCB-4mini と Arduino の配線 |

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
2. サーボを **1 個だけ** アダプターのケーブルにつなぐ。2 個以上つなぐと、同じ ID の
   サーボが同時に返事をして、どれも正しく読めません。
3. アダプターを PC の USB に差す。サーボに別の電源はつないでいません（下の写真の
   状態で、`ics-manager` からサーボの設定が読めることを確かめています）。

```{figure} ../_static/krs_id_setup.jpg
:target: ../_static/krs_id_setup.jpg
:alt: ノート PC の USB に Dual USB アダプター HS を差し、そのケーブルの先に KRS-3302 サーボを 1 個つないだところ

PC → Dual USB アダプター HS → KRS-3302 を 1 個。これで ID を振る
```

### OS ごとの準備

| OS | 準備 |
|---|---|
| macOS | `brew install libusb`。`ics-manager` は libusb 経由でアダプターに直接つなぐ（ドライバは要らない） |
| Linux | アダプターを FTDI のシリアルとして認識させる。下のコマンドを 1 回実行する |
| Windows | 近藤科学の KO Driver を入れる。**Windows で `ics-manager` が動くかは、まだ確かめていません** |

Linux では、`ics-manager` がつながらないときに自分でこの手順を表示します。

```console
$ sudo su
# modprobe ftdi-sio
# echo 165C 0008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
# exit
```

## サーボの設定を確かめて、ID を振る

### ics-manager を入れる

`ics-manager` は、ICS サーボの ID や設定を見たり書いたりするコマンドです。
[rcb4](https://github.com/iory/rcb4) という Python パッケージに入っています。
開発環境の準備で入れた uv で、次の 1 行で入ります
（uv がまだなら [macOS](../getting-started/macos.md) /
[Windows](../getting-started/windows.md) / [Linux](../getting-started/linux.md)
の「uv を入れる」を先に）。

```console
$ uv tool install rcb4
```

### 画面の見方

サーボを 1 個つないで `ics-manager` を実行すると、次の画面が出ます（実機の ID 2 の
サーボで実行したもの）。

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

ID はサーボの中（EEPROM）に書かれるので、電源を切っても消えません。

### Rotation Mode や Reverse Mode が Enabled だったら

- **Rotation Mode** は `r` キーで切り替わります。`Disabled` になるまで押してください。
- **Reverse Mode** には切り替えのキーがありません。`d` を押して `y` で答えると、
  サーボの設定が標準の値（回転モード・逆転モードともに無効、通信速度 1.25Mbps）に
  戻ります。そのあと **ID を確かめ直し、違っていれば振り直してください**。`d` は
  サーボの設定をまとめて書き換えるので、上の 2 つで困ったときだけ使います。

### どのサーボをどこに使うか

ID の割り当ては Feetech 版と同じです。

```{figure} assembly_img/servo_ids.png
:target: assembly_img/servo_ids.png
:alt: 四脚ロボットを上と左から見た図に、各サーボの ID を書き込んだもの。右前 1・2、左前 3・4、右後 5・6、左後 7・8。それぞれ股が奇数、膝が偶数

サーボ ID の割り当て。上から見て、胴体の短い辺の中央に出っ張りがある側が前
```

## ホーンの向き（サーボのゼロ点）を合わせる

サーボの出力軸にホーン（脚を固定する円盤）を付ける向きで、「サーボが真ん中のとき
脚がどちらを向くか」が決まります。

```{figure} ../_static/krs_servo_spline.jpg
:target: ../_static/krs_servo_spline.jpg
:width: 60%
:alt: ホーンを付ける前の KRS サーボ 2 個。出力軸のギザギザ（スプライン）と、ケースの目盛りが見える

ホーンを付ける前のサーボ。出力軸はギザギザ（スプライン）になっていて、ホーンは
ギザギザ 1 山ずつの向きにしか付かない
```

**ぴったり合わせる必要はありません。** 最後に組み上げた機体で、脚をまっすぐ
伸ばしたときのサーボの値を測ってファームウェアに書きます（下の「校正する」）。
ホーンのずれは、そこで吸収されます。

ただし、大きくずれると関節の動く範囲がサーボの範囲（中央から ±135 度）からはみ出す
ので、次の手順でだいたい合わせておきます。

1. サーボを Dual USB アダプターにつないで `ics-manager` を実行する。
   `Free: Enabled`（脱力）なので、出力軸は手で回せます。
2. 出力軸を手で回して、`Angle` が **0 付近** になるところで止める。
3. 脚をまっすぐ真下に伸ばした向き（CAD の 0 度）になるように、ホーンと脚を付ける。

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

### サーボ → RCB-4mini

RCB-4mini の SIO ポートは 2 系統に分かれていて、**右側（SIO1〜4）につないだ ID n の
サーボは RCB-4 の中で n × 2 番、左側（SIO5〜8）なら n × 2 + 1 番** として扱われます
（RCB-4 コマンドリファレンス）。ファームウェアは起動時に両方を調べるので、
**どちらの系統に挿してもかまいません。** サーボどうしは数珠つなぎにできます。

```{figure} ../_static/krs_rcb4_wiring.jpg
:target: ../_static/krs_rcb4_wiring.jpg
:alt: RCB-4mini の SIO ポートにサーボのケーブルが何本も差さっているところ

RCB-4mini まわり。白いコネクタが SIO ポート、緑が AD ポート
```

### RCB-4mini → Arduino

RCB-4mini の **COM ポート**（青い 3 ピン）と Arduino を、ZH 3 ピンのケーブルと
ジャンパワイヤでつなぎます。COM ポートのピンは GND 側から **GND・Rx・Tx** の順です。

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

2S LiFe バッテリー 1 本で、サーボ・RCB-4mini・Arduino をまとめて動かします。

1. バッテリーを RCB-4mini の **電源端子** につなぐ。サーボの電源はここから SIO ポート
   経由で配られます。
2. **空いている SIO ポート** の **Vcc を Arduino の VIN** へ、**GND を Arduino の GND**
   へつなぐ。SIO ポートの Vcc にはバッテリーの電圧（6.6〜7.2 V）がそのまま出ていて、
   Arduino の VIN は 6〜24 V を受け付けます。**SIO ポートの信号線はつながないでください**
   （サーボの通信線そのものです）。

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item}

```{figure} ../_static/krs_wiring.jpg
:target: ../_static/krs_wiring.jpg
:alt: 胴体の中の配線全体。緑のバッテリー、RCB-4mini、Arduino、サーボのケーブル

配線の全体。右下の緑がバッテリー
```

:::
:::{grid-item}

```{figure} ../_static/krs_uno_wiring.jpg
:target: ../_static/krs_uno_wiring.jpg
:alt: Arduino UNO R4 WiFi の D8・D9 に黄と青のジャンパワイヤ、電源ヘッダの VIN と GND に赤と黒の線がつながっている

Arduino 側。黄と青が D8 / D9（RCB-4 の COM）、赤と黒が VIN / GND（SIO ポートの電源）
```

:::
::::

USB ケーブルを同時に差していても問題ありません。書き込みのときに外す必要はありません。

```{warning}
LiFe は使い終わり近くで電圧が急に下がります。6 V を切ると Arduino の VIN の範囲を
外れるので、その前に充電してください。
```

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
   `QUAD_RCB4_SIGN` を `-1` にします（本書の機体では左の脚が `-1`、右の脚が `+1`）。
5. `QUAD_RCB4_CALIBRATED` を `1` にして、もう一度書き込む。**起動するとすぐに 2 秒
   かけて立ち姿勢へ動く** ので、機体は吊るしたままにしてください。
6. 吊るしたまま `rl 0.06 0` を送り、4 本の脚が交互に足踏みすれば完成です。床に
   下ろして歩かせるのは、そのあとです。

キーボードで歩かせる方法（`quad_host.py serial`）と、WiFi で歩かせる版
（`-e uno_r4_wifi_rcb4_udp`）は、
[code/13_quadruped/README.md](https://github.com/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/README.md)
にあります。

```{figure} ../_static/krs_done.jpg
:target: ../_static/krs_done.jpg
:width: 60%
:alt: ふたを閉めた KRS 版の四脚ロボットを上から見たところ

組み上がった KRS 版
```

## うまくいかないとき

| 症状 | 確かめること |
|---|---|
| `ics-manager` が `Connection is not open.` のまま | アダプターの LED が赤（ICS モード）か。サーボを 1 個だけつないでいるか。macOS なら libusb、Linux なら上の `new_id` |
| 起動時に一部の関節が `見つからない` | そのサーボの ID と `Baud Rate`（1.25Mbps）を `ics-manager` で確かめる。ケーブルが奥まで差さっているか |
| 1 本の脚だけ逆に動く | そのサーボの `Reverse Mode` が `Enabled` になっていないか。`QUAD_RCB4_SIGN` の値 |
| 関節が止まらずに回り続ける | そのサーボの `Rotation Mode` が `Enabled`（連続回転モード）になっていないか |
| 歩いている最中に Arduino がリセットする | バッテリーの電圧。6 V を切っていないか |

```{admonition} RCB-4mini に書き込まれたプロジェクトについて
:class: tip

RCB-4mini は、近藤科学の Heart to Heart 4 で書き込んだプロジェクトに「割り当て」られた
サーボとしか話しません。本書の機体でも、届いた時点のプロジェクトは 8 個のうち 5 個しか
割り当てていませんでした。ファームウェアは起動時に割り当てを自分で足すので、
Heart to Heart 4 でプロジェクトを作り直す必要はありません（RCB-4mini の RAM に書くだけで、
中に保存されたプロジェクトは書き換えません）。
```

## 出典

- RCB-4mini の電源電圧（6〜12 V）・SIO / AD / COM ポートの配置: <https://kondo-robot.com/product/rcb4_mini>、
  HeartToHeart4 取扱説明書 Ver.8 の 6〜7 ページ <https://www.kondokagaku.jp/data_download/HeartToHeart4_manual_Ver8_JP.pdf>
- ICS 番号（SIO1〜4 は ID × 2、SIO5〜8 は ID × 2 + 1）と、ICS の割り当て表（RAM `$0044`）:
  RCB-4 リファレンスセット Ver.2.2 のコマンドリファレンスとファームウェアリファレンス <https://kondo-robot.com/faq/rcb-4-reference-ver-2_2>
- Dual USB アダプター HS（LED 赤が ICS、緑がシリアル）: <https://kondo-robot.com/product/02116>
- 近藤科学の 2S LiFe バッテリー（公称 6.6 V）: <https://kondo-robot.com/product/03241>
- Arduino UNO R4 WiFi の VIN（6〜24 V）: <https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf>
- `ics-manager` の表示とキー操作: rcb4 v0.1.3 の `rcb4/ics.py` <https://github.com/iory/rcb4>
