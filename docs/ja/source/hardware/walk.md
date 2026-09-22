# 歩行を学習させる（強化学習）

第13章の四脚は、**強化学習（PPO）で学習した方策**で歩きます。紙面の都合で
本には載せられなかった学習まわりを、ここでまとめてサポートします。

## ブラウザで歩かせてみる

学習済み方策を **MuJoCo（WebAssembly 版）** で動かすシミュレーションです。
実機に書き込むものと同じニューラルネットワークが、ブラウザの中で
50 Hz の制御ループを回しています。前進・旋回の指令をスライダーで変えられます。

物理は**学習したときと同じ**にしてあります。接地するのは足先の球 4 つだけ、
サーボは位置制御（kp 25・kd 0.5）+ 逆起電力に相当する粘性減衰 + ギアの摩擦で、
指令は 20〜35 ms（実機で測った 27 ms を挟む幅）遅れてサーボに届きます。

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../assembly/quadruped/walk/index.html"
     target="_blank" rel="noopener">歩行シミュレーションを開く ↗</a>
</p>
<iframe src="../assembly/quadruped/walk/index.html"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="四脚ロボット 歩行シミュレーション"></iframe>
```

```{note}
初回は物理エンジン（WASM）とロボットモデルで約 16 MB ダウンロードします。
```

「制御」の切替で、**本文 13.5 の sin/cos 歩行**（状態機械 + trot）と
RL 方策を比べられます。sin/cos 側は、遊脚を sin で山なりに持ち上げて
2 リンク IK（本文 13.3）で関節角に変換するもので、本のサンプルコード
`src/gait.cpp` + `src/leg_ik.cpp` をそのままブラウザに移植したものです。
ただ、この機体は前後が非対称なので、進む向きで歩き方がまるで変わります。
同じストライド 0.02 m（スライダー ±0.05）で、前へはほとんど進まず
（0.006 m/s）、後ろへは 0.10 m/s で進みます。前進はスライダー 0.12
（ストライド 0.048 m）で 0.06 m/s、0.15 まで上げると 8 回に 1 回は横倒しに
なります。係数を手で回してもどちらかにしか合わせられない——それが RL に
行く動機です。

## 方策の中身

小さな MLP 1 つだけで歩いています。Arduino UNO R4 でも毎周期推論できる
サイズです。

| | |
|---|---|
| 入力（観測） | **87 次元** = 指令 (vx, vy, wz) ・歩容位相 (sin/cos) ・関節角 8 ・関節速度 8 ・前回 action 8、それぞれ **3 ステップ分の履歴** |
| ネットワーク | 全結合 [96, 64]、活性化 ELU |
| 出力 | 8（各関節）。サーボ目標角 = home 角 + 0.25 × action |
| 制御周期 | 50 Hz（0.02 s）、歩容クロック 0.32 s |
| センサ | **関節角・関節速度のみ。IMU は使っていない**（この機体に無いため。胴体の姿勢は方策から見えていない） |

外転関節が無いので横移動（vy）はできません。旋回は左右の歩幅差で作ります。

シミュレーションでの性能: 前進指令 0.12 m/s で 0.115 m/s（0.46 体長/秒）、
最大の指令 0.15 m/s で 0.157 m/s。指令にほぼ追従します。旋回は指令
0.3 rad/s で 0.15 rad/s と、指令の半分です。対角トロットは約 3.1 Hz
（歩容周期 0.32 s）。いずれも上のシミュレーションと同じモデル・同じ制御で
20 秒ずつ 5 回歩かせ、後半 10 秒の平均を取った値です。遅いのはサーボの無負荷回転数で決まる
機体の性質で、学習の失敗ではありません。

## 学習のコード

学習は [mjlab (unitree_rl_mjlab)](https://github.com/unitreerobotics/unitree_rl_mjlab)
の PPO（rsl_rl）で行い、ロボット定義・報酬・環境設定を差し替える overlay として
書いてあります:

- コードを見る: [docs/os-on-arduino/code/13_quadruped/rl](https://github.com/iory/learning-os-from-arduino/tree/main/docs/os-on-arduino/code/13_quadruped/rl)
- ロボット記述一式（**URDF**・MJCF・メッシュ・RViz 設定、SolidWorks
  エクスポートから MJCF を再現するスクリプト付き）:
  [docs/os-on-arduino/code/13_quadruped/arduino_os_quad_robot](https://github.com/iory/learning-os-from-arduino/tree/main/docs/os-on-arduino/code/13_quadruped/arduino_os_quad_robot)

sim2real のために、摩擦（0.4〜1.1）・付加質量（電装ぶん 0〜250 g）・
ゼロ点誤差（±1.7°）・関節角（±8.6°）などをランダム化して学習したあと、
リセット姿勢・速度をさらに乱した fine-tune（ロバスト化）を重ねています。
だから組み立てで数度ずれても歩きます。

**自分で学習し直す手順は {doc}`train` にまとめました。**
報酬や速度上限を変えて回してみたいとき、そして
**GPU が無い場合の Google Colab での通し方**はそちらです。

## 実機で歩かせる

使うのは第13章のサンプルコード
[`code/13_quadruped/`](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/13_quadruped)
です。学習済み方策は `include/arduino_quad_policy.h` に入っていて、
**上のブラウザのシミュレーションと同じ方策**です。書き込めばそのまま歩きますが、
その前に**自分の機体で校正**が要ります（サーボの ID・回る向き・ゼロ点は
機体ごとに違うため）。

```{figure} ../_static/quadruped_walk.gif
:name: fig-walk-real
:width: 80%

本書の実機（自作 OS で 8 個のサーボを制御）が歩くところ（1.5 倍速）
```

### 1. PC からサーボを校正する

ドライバーボードのジャンパを **B（USB → SERVO）** にして、ボードの USB Type-C を
PC につなぎます。Arduino を焼かずに、PC から直接サーボを動かして測ります。

```bash
cd code/13_quadruped/host
uv sync                                        # pyserial と numpy が入る

uv run python quad_host.py scan                # 8 個応答するか、ボーレートは合っているか
uv run python quad_host.py calibrate --write-middle
uv run python quad_host.py stand               # home 姿勢を保持して確かめる
```

`calibrate` は対話式です（**機体を吊るすか手で持って**行う）。関節と ID の対応、
回る向き（sign）、ゼロ点を順に測り、`host/calib.json` に書き出します。
`--write-middle` を付けるとゼロ点をサーボの EEPROM に書くので、ゼロ点は全関節
2048 になります。

ポートは自動で探します。ほかに USB シリアル機器がつながっていて誤検出される
ときだけ `--port` を足してください（Linux は `/dev/ttyACM0`、macOS は
`/dev/cu.usbmodem...`、Windows は `COM3` のような名前です）。OS ごとの詰まり
どころは {doc}`../getting-started/linux` と {doc}`../getting-started/windows` に
まとめてあります。

### 2. 校正値をファームウェアに写す

`host/calib.json` の値を `include/quad_calib.h` に写します。

| `calib.json` | `quad_calib.h` |
|---|---|
| `id` | `QUAD_SERVO_ID` |
| `sign` | `QUAD_SERVO_SIGN` |
| `zero` | `QUAD_SERVO_ZERO`（`--write-middle` を使ったなら全部 2048 のままでよい） |

並び順は両方とも同じ（FL_hip, FL_knee, RL_hip, RL_knee, RR_hip, RR_knee,
FR_hip, FR_knee）です。**`quad_calib.h` に最初から入っている値は本書の機体の
もので、そのまま使うと暴れます。**

### 3. Arduino に書き込んで歩かせる

ジャンパを **A（UART → SERVO）** に戻し、ボードの UART ヘッダ（TX / RX / GND）と
Arduino の D1 / D0 / GND を 3 本でつなぎます
（**RX 同士・TX 同士**。{doc}`bom` の「配線で先に知っておくこと」）。

```bash
pio run -d code/13_quadruped -t upload
pio device monitor -d code/13_quadruped -b 115200
```

シリアルモニタからコマンドを打ちます。**この順で**進めてください:

1. `iktest` — 脚を動かさずに FK/IK の往復を確かめる
2. **機体を吊るして** `stand` — home 姿勢へ 2 秒で立ち上がる。4 本とも同じ格好に
   なること。1 本だけ鏡像になるなら、その脚の sign が逆
3. 吊るしたまま `rl 0.06 0` — 学習済み方策で脚を動かす
4. 床に下ろして `rl 0.12 0`（`rl <前進 m/s> <旋回 rad/s>`）。止めるときは
   `stop`（home 姿勢を保持）、トルクを切るのは `free`

歩いているあいだ、毎秒こういう行が出ます:

```
loop avg 3210 us  max 6980 us  late 0/50  skipped 0  read_fail 0
```

`skipped` は制御周期（50 Hz）を落とした回数、`read_fail` はサーボが応答しなかった
回数で、**どちらも 0 のまま**が正常です。増えるなら配線か電源を疑ってください。

```{warning}
- サーボ 8 個の電源は**必ずバッテリーから**。PC の USB からは絶対に取らない
  （1 個あたりストール 2.7 A）
- `stand` と最初の `rl` は**まず機体を吊るして**から。符号や ID を間違えると、
  下手に歩くのではなく暴れます
- 足裏にゴムかシリコンを貼ること（素の樹脂は硬い床で滑ります）
```

## FAQ

**転倒から起き上がれる？** — できません。IMU が無く自分の姿勢を観測できない
ためです（学習しても成功率 1%）。IMU を載せる価値が最も高いのはここです。

**もっと速くならない？** — 45 rpm のサーボに 0.19 m の脚という構成では
0.05〜0.2 m/s が素の実力です（シミュレーションでは最大の指令で 0.16 m/s）。律速はトルクではなく無負荷回転数なので、
速くしたければサーボか脚長の変更になります。
