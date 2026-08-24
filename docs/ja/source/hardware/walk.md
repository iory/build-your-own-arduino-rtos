# 歩行を学習させる（強化学習）

第13章の四脚は、**強化学習（PPO）で学習した方策**で歩きます。紙面の都合で
本には載せられなかった学習まわりを、ここでまとめてサポートします。

## ブラウザで歩かせてみる

学習済み方策を **MuJoCo（WebAssembly 版）** で動かすシミュレーションです。
実機に書き込むものと同じニューラルネットワークが、ブラウザの中で
50 Hz の制御ループを回しています。前進・旋回の指令をスライダーで変えられます。

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

シミュレーションでの性能: 前進 0.148 m/s（0.59 体長/秒）、対角トロット
3.33 Hz。遅いのはサーボの無負荷回転数で決まる機体の性質で、学習の失敗では
ありません。

## 学習のコード

学習は [mjlab (unitree_rl_mjlab)](https://github.com/unitreerobotics/unitree_rl_mjlab)
の PPO（rsl_rl）で行い、ロボット定義・報酬・環境設定を差し替える overlay として
書いてあります:

- コードを見る: [code/13_quadruped/rl](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/13_quadruped/rl)

sim2real のために、摩擦（0.4〜1.1）・付加質量（電装ぶん 0〜250 g）・
ゼロ点誤差（±1.7°）・関節角（±8.6°）などをランダム化して学習したあと、
リセット姿勢・速度をさらに乱した fine-tune（ロバスト化）を重ねています。
だから組み立てで数度ずれても歩きます。

## 実機で歩かせる

学習済み方策・実行コード・校正ウィザードの一式:

- コードを見る: [code/13_quadruped/walk](https://github.com/iory/build-your-own-arduino-rtos/tree/main/code/13_quadruped/walk)
  — まず `HANDOFF.md` を読んでください

2 つの経路があります。**推奨は PC 直結**（Arduino を焼かずに済み、途中の値が
全部見える）:

```bash
# PC ─USB─ サーボドライバボード ─半二重TTL─ サーボ8個
pip install feetech-servo-sdk pyserial numpy
python host/quad_host.py --port /dev/tty.usbserial-XXXX scan
python host/quad_host.py --port ... calibrate --write-middle
python host/quad_host.py --port ... stand
python host/quad_host.py --port ... run --vx 0.05
```

PC で歩いてから `arduino/arduino_quad/` のスケッチ（同じ数値・同じ観測の
C 実装）に移します。校正は `arduino/calibrate/` の対話ウィザードでも
できます。

```{warning}
- サーボ 8 個の電源は**必ずバッテリーから**。PC の USB からは絶対に取らない
  （1 個あたりストール 2.7 A）
- `run` は**まず機体を吊るして**から。符号や ID を間違えると、下手に歩くの
  ではなく暴れます
- 足裏にゴムかシリコンを貼ること（素の樹脂は硬い床で滑ります）
```

## FAQ

**転倒から起き上がれる？** — できません。IMU が無く自分の姿勢を観測できない
ためです（学習しても成功率 1%）。IMU を載せる価値が最も高いのはここです。

**もっと速くならない？** — 45 rpm のサーボに 0.19 m の脚という構成では
0.05〜0.15 m/s が素の実力です。律速はトルクではなく無負荷回転数なので、
速くしたければサーボか脚長の変更になります。
