# 部品表（BOM）— 8 自由度四脚ロボット

第13章の機体を作るのに要るもの。**本書の実機と同じ構成**で、価格は 2026 年 8 月時点。

```{contents} このページの内容
:local:
:depth: 2
```

---

## 電子部品

| # | 品目 | 通販コード | 単価 | 数 | 小計 |
|---|---|---|---|---|---|
| 1 | [FEETECH シリアルバスサーボ STS3215 12V 30kg·cm](https://akizukidenshi.com/catalog/g/g130969/) | 秋月 130969 | ¥3,580 | 8 | **¥28,640** |
| 2 | [シリアルバスサーボドライバーボード (Waveshare 25514)](https://akizukidenshi.com/catalog/g/g131227/) | 秋月 131227 | ¥1,280 | 1 | ¥1,280 |
| 3 | [スイッチング AC アダプター 12V5A AD-A120P500](https://akizukidenshi.com/catalog/g/g110663/) | 秋月 110663 | ¥2,380 | 1 | ¥2,380 |
| 4 | [ブレッドボード・ジャンパーワイヤ (オス−メス) 15cm](https://akizukidenshi.com/catalog/g/g108932/) | 秋月 108932 ほか | ¥280 | 1 | ¥280 |
| 5 | USB Type-C ケーブル（データ通信対応）: [C-to-C — CIO SL30000-CC](https://www.amazon.co.jp/dp/B0B2PQ5N71) / [A-to-C — CIO SL30000-AC](https://www.amazon.co.jp/dp/B09LC5T7YL) | — | ¥1,500〜 | 1 | ¥1,500 |
| 6 | [ROBOTIS 3P Extension PCB](https://e-shop.robotis.co.jp/product.php?id=96)（バスの分岐。任意） | 903-0142-000 | ¥495 | 2 | ¥990 |

ケーブルは**どちらか 1 本でよい**。PC の USB ポートが Type-C なら C-to-C、
**Type-A しかないなら A-to-C** を買う。

**合計 約 ¥35,100。** サーボが 81% を占める。

このほかに **Arduino UNO R4 WiFi** と、走行用の **12V バッテリ（3S LiPo 相当）** が要る。

### AC アダプターの容量

データシートの **ストール 2.942 N·m / 2.7 A** から、電流はトルクにほぼ比例するとして
**0.92 A/(N·m)** で見積もった。

| 状態 | 1 関節のトルク | 8 個の合計 |
|---|---|---|
| 立ち姿勢の保持（実測 0.27 N·m） | 9% | 約 2 A |
| 歩行（rms 0.75 N·m、最速歩容） | 76% | 約 5.5 A |
| 8 個同時ストール | 100% | 21.6 A |

**5A を選んでいる。** 卓上作業（校正・同定・姿勢保持）は 2 A で足り、歩かせても平均では
収まる。踏み替えの瞬間のピークは 5A を超えるので、**ターミナルブロックに電解コンデンサ
（2200〜4700 µF / 25V）を 1 個足す**と、電圧の垂下によるサーボのリセットが減る。

21.6 A の電源を買う意味はない。全関節が同時にストールするのは事故のときだけ。

**床を歩かせるときはバッテリを使うこと。** 1 m の DC ケーブルを引きずって歩く四脚は
危険で、実際にケーブルが抜けたことがある。AC アダプターは卓上用。

ドライバーボードの入力上限は **12.6 V**。3S LiPo の満充電がちょうど 12.6 V で、上限に張り付く。

### バッテリー駆動（任意）

床を歩かせるならバッテリーが要る。**USB-C PD のモバイルバッテリーから 12 V を取り出す
のがいちばん簡単で、実機で動作を確認した。**

| # | 品目 | 条件 |
|---|---|---|
| a | USB-C PD モバイルバッテリー | **出力 PDO に `12V ⎓ 3A` が明記されていること** |
| b | USB Type-C to C ケーブル（短いもの） | データ通信対応。3 A なら普通の 60W ケーブルでよい |
| c | [PD トリガーケーブル PDC-12VE](https://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-5X3J) | **12V 固定**・5A・DC 5.5/2.1・**センタープラス**・¥1,830 |

半田付けも圧着も要らない。バッテリー → C to C ケーブル → トリガーケーブル →
ボードの DC ジャック、と挿すだけ。

**製品名ではなく条件で選ぶこと。** モバイルバッテリーは世代交代が速く、下に挙げる型番は
数年で消える。判断基準は 1 つだけで、**販売ページの出力仕様に `12V` が列挙されているか**。
「PD 65W」「最大 100W」だけでは分からない。

```{admonition} PD の 12V は任意規定
:class: warning
USB PD の固定電圧は 5V / 9V / 15V / 20V が基本で、**12V は任意**。持っていない製品が普通に
ある。実際、**Anker は USB-C 出力に 12V を積んでいない**（公式仕様で確認。Nano Power Bank
10K 45W は 5V/9V/**10V**/15V/20V で、12V が出るのは USB-A ポートの QC 系のみ）。

PPS（3.3〜11V などの可変）しか無い製品も、**普通の 12V 固定トリガーケーブルでは
12V を引き出せない**。

そして **15V と 20V はボードの上限 12.6 V を超える**。切替式のトリガーケーブルを使うなら、
誤って 15V に入れないこと。固定品のほうが事故らない。
```

**参考として、公式仕様で 12V/3A を確認できた製品**（2026 年 8 月時点。あくまで例）:

| 製品 | 容量 | 重量 | 12V |
|---|---|---|---|
| [CIO SMARTCOBY TRIO 67W](https://connectinternationalone.co.jp/cioproduct/mobilebattery/smartcoby/cio-mb67w2c1a-20000/) | 20000mAh | 約 333 g | 3A |
| [CIO SMARTCOBY Pro PLUGⅡ 67W3C](https://connectinternationalone.co.jp/cioproduct/mobilebattery/smartcoby/cio-mb67w3c-10k-p2/) | 5000mAh | 約 308 g | 3A |
| [エレコム DE-C81L-10000](https://www.elecom.co.jp/products/DE-C81L-10000BK.html) | 10000mAh | **約 220 g** | 3A |

**軽い機種は 12V を持っていても 1.6〜2.5 A で止まる。** 100 g 台で 12V/3A というものは
見つからなかった。12V/3A を出すには 45W 級以上が要り、その回路とセルは 200 g を切れない。

**極性を必ず確認すること。** エフェクター用に**センターマイナス**の PD トリガーケーブルが
売られていて、見た目は同じ。挿した瞬間に逆接になる。

12V/3A = 36 W には余裕が無いので、**電解コンデンサ（2200〜4700 µF / 25V）を 1 個**入れて
突入電流を吸わせること。落ちるようなら 67W 級に上げる。

### 配線で先に知っておくこと

**このボードの UART は `RX-RX` / `TX-TX` で繋ぐ。** Waveshare の説明にそう書いてある。

> the connection must be RX-RX, TX-TX

普通の UART の常識と逆で、実際に 2 回はまった。

ボードには **USB Type-C と A/B ジャンパ**があり、「PC から USB で叩く」と
「Arduino から UART で叩く」を切り替える。立ち上げと校正は USB 側が早いので、
**両方使えるようにしておくとよい**。

Arduino とボードの接続はジャンパーワイヤ 3 本
（ボードの UART ヘッダ ←→ D0/D1/GND）で足りる。歩行中に抜けると転倒するので、
固くしたいときは 2.54 mm のピンヘッダ・ピンソケットで自作する。

### バスの分岐（任意）

サーボどうしは**数珠つなぎ**にできる（各サーボが 3 ピンコネクタを 2 個持つ）ので、
ハブは必須ではない。ただし四脚は 4 隅から脚が出るので、配線長を短くする目的で
分岐基板を使うと取り回しが楽になる。

FEETECH のコネクタは **Molex Mini-SPOX 5264**（2.50 mm ピッチ、
1=GND / 2=Vcc / 3=信号）で、これは **Dynamixel の Molex 系（AX / MX）と同じ**。
ROBOTIS の分岐基板がそのまま使える。

| 商品 | 型番 | コネクタ | 税込 | この機体に |
|---|---|---|---|---|
| [3P Extension PCB](https://e-shop.robotis.co.jp/product.php?id=96) | 903-0142-000 | **Molex 3P**（ヘッダ 22-03-5035） | **495 円** | **これ。6 ポート、M2 ネジ穴** |
| [3P JST Expansion Board](https://e-shop.robotis.co.jp/product.php?id=506) | 903-0306-000 | JST 3P | 1,584 円 | 系列が違う |
| [4P JST Expansion Board](https://e-shop.robotis.co.jp/product.php?id=505) | 903-0307-000 | JST 4P | 1,716 円 | RS-485 用 |

**Molex 版と JST 版を間違えないこと。** ROBOTIS 自身が、Molex 版は「JST コネクタを
使う X シリーズと非互換」、JST 版は「Molex コネクタの AX / MX と非互換」と書いている。
FEETECH は Molex 側。

ヘッダの `22-03-5035` は Mini-SPOX 5267 系で、5264 ハウジングの正規の嵌合相手。
**ただし ROBOTIS の基板に FEETECH のケーブルを挿した実例は確認していない。**
495 円なので 1 個買って現物で確かめるのが早い。

**2 個買って左右の脚で分けること。** Mini-SPOX 5264 の定格は 1 極 **3.0 A** で、
歩行時の合計は約 5.5 A（上の表）。8 サーボ全部を 1 個のハブに通すと定格を超える。
左右に分ければ 1 個あたり 4 サーボ = 約 2.7 A で収まる。

**基板の裏面は絶縁されていない。** 樹脂の胴体に付けるぶんには問題ないが、金属の上に
置かないこと（ROBOTIS の注意書き）。

秋月電子とスイッチサイエンスには、これに相当する分岐基板は無い（探した範囲では、
出てくるのは単体のコネクタ・ハウジングか、I²C / USB のハブ）。

---

## 3D プリント部品

STL は下からダウンロードできます（単位はミリメートル。
[組み立て手順](assembly.md) の 3D ビューアと同じ CAD データから書き出したもの）。

| 部品 | ファイル | 外形 [mm] | 個数 | 実体積 |
|---|---|---|---|---|
| 胴体 | `body.stl` | **230.0 × 110.0 × 50.0** | 1 | 240.6 cm³ |
| 脚ブラケット | `bracket_outline.stl` | 127.8 × 52.2 × 12.0 | 4 | 19.0 cm³ |
| 脚リンク | `leg_link1.stl` | 80.0 × 52.0 × 26.0 | 4 | 39.4 cm³ |

::::{grid} 3
:gutter: 2

:::{grid-item}
```{button-link} ../assembly/quadruped/stl/body.stl
:color: primary
:expand:
body.stl（×1）
```
:::
:::{grid-item}
```{button-link} ../assembly/quadruped/stl/bracket_outline.stl
:color: primary
:expand:
bracket_outline.stl（×4）
```
:::
:::{grid-item}
```{button-link} ../assembly/quadruped/stl/leg_link1.stl
:color: primary
:expand:
leg_link1.stl（×4）
```
:::
::::

まとめて読み込むなら 3MF が楽です（単位ミリ指定・必要個数（1 + 4 + 4）を配置済み。
1 プレートに収まらない分はスライサの自動整列で分割してください）:

```{button-link} ../assembly/quadruped/stl/quadruped_parts.3mf
:color: secondary
quadruped_parts.3mf（9 部品入り）
```

**9 部品、実体積の合計 約 474 cm³。**

**左右の脚は同じ部品。** ブラケットもリンクも 1 つの STL を 4 回刷ればよく、
左右の作り分けは要らない。

---

## 自分で刷る

| | |
|---|---|
| 素材 | **PLA で十分**。PETG・ABS でも可（ABS は反りやすいのでエンクロージャ付きの機種で） |
| 必要なベッド | **片辺 230 mm 以上**。胴体の長辺が 230 mm |
| フィラメント | **240 g 前後**（推定。スライスすれば正確に出る） |
| 費用 | **約 ¥700**（PLA 1 kg ¥2,500〜3,500 の 1/4 程度） |

胴体が 230 mm あるので、**ベッドサイズを買う前に確認すること。**

| プリンタ | ベッド | 胴体 |
|---|---|---|
| Bambu X1C / P1S | 256 × 256 | 入る |
| Prusa MK4 | 250 × 210 | 入る |
| Bambu A1 mini | 180 × 180 | 入らない |

ジョブは「胴体で 1 回、ブラケット 4 + リンク 4 でもう 1 回」が目安。
ブラケットは 12 mm 厚の板なので平置きでよい（サーボのトルクを受ける部品なので、
積層方向が面内になる平置きが強度の面でも正しい）。

スライサの設定は **PLA の既定プロファイル（層厚 0.20 mm）のままで十分**です。
強度を上げたいときは充填率よりも**壁の数を増やす**（2 → 4〜6 本）ほうが効きます。

---

## 注文して買う

プリンタが無い、ベッドが 230 mm に足りない、ナイロンの粘りが欲しい、のいずれかのとき。

| サービス | 方式 | 単価の目安 | 474 cm³ だと |
|---|---|---|---|
| [PCBWay Shared Projects](https://www.pcbway.com/project/shareproject/?category=3D+Printing) | FDM / SLA / MJF ほか | FDM が選べるので安い | 要見積もり |
| [DMM.make 3Dプリント](https://make.dmm.com/print/) | MJF PA12 | 113 円/cm³〜 | **約 ¥54,000〜** |
| DMM.make | SLS PP | 63 円/cm³〜 | 約 ¥30,000〜 |

**代行に出すとサーボ代を超える。** 自分で刷れば ¥700 なので **77 倍**の開きがある。
230 mm が刷れるプリンタは ¥40,000〜90,000 で、**1 回外注する金額でほぼプリンタが買える。**

そしてロボットのフレームは必ず作り直す。脚が折れる、穴位置を変える、取り付け角を変える。
作り直すたびに ¥54,000 かかる前提で設計するのは現実的ではない。
**「自分で刷る」が本線、「外注」は例外。**

---

## 質量はシミュレーションモデルと違う

プリント部品の質量は素材と充填率で大きく変わる（474 cm³ を PLA 中実で刷れば
約 590 g、充填 20% なら 240 g 程度）。シミュレーションモデルの質量とは必ず
ずれるので、シミュレーションと突き合わせたいときは、**作った部品を秤で量って
モデル側の質量を直す**こと。慣性も重心も変わる。

---

## 出典

- 秋月電子通商の各商品ページ（上記リンク）
- [Bus Servo Adapter (A) — Waveshare](https://www.waveshare.com/bus-servo-adapter-a.htm)（RX-RX / TX-TX、9〜12.6V）
- [3P Extension PCB — ROBOTIS 日本 e-shop](https://e-shop.robotis.co.jp/product.php?id=96)（価格・在庫・M2・ヘッダ 22-03-5035・裏面非絶縁）
- [USBインターフェース / ハブ基板 — ROBOTIS 日本 e-shop](https://e-shop.robotis.co.jp/list.php?c_id=117)（ハブ基板 4 種の比較）
- [How to Use STS3215 — Cirkit Designer](https://docs.cirkitdesigner.com/component/ff940def-9432-4e1a-bede-b65e49fd0ea7/sts3215)（5264-3P、1=GND / 2=Vcc / 3=信号）
- [Molex Mini-SPOX (5264) Connector Guide — Keszoox](https://keszoox.com/blogs/news/molex-mini-spox-connector-guide)（3.0 A / 2.50 mm / フリクションロック）
- [PKT shop PDC-12VE — 千石電商](https://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-5X3J)（12V固定 5A センタープラス）
- [Anker Nano Power Bank (10K, 45W)](https://www.anker.com/products/a1638-10k-45w-power-bank)（USB-C の PDO に 12V が無いことの確認）
- CIO / エレコムのモバイルバッテリーの PDO は各公式製品ページ（上記リンク）
- [DMM.make 3Dプリント](https://make.dmm.com/print/)（素材別 1 cm³ 単価、造形サイズ）
- 寸法・体積は配布している STL の実測
