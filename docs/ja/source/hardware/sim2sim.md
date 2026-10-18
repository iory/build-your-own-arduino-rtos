# Genesis で学習して MuJoCo で歩かせる（sim2sim）

{doc}`walk` の方策は MuJoCo（mjlab）で学習し、同じ MuJoCo で歩かせています。
このページでは、同じタスクを**別の物理シミュレータ Genesis で学習**し、その方策を
**ブラウザの MuJoCo で歩かせます**。学習したシミュレータとは別のシミュレータで
動かすことを **sim2sim** と呼びます。

方策が、学習に使った物理エンジンの癖（接触の柔らかさ、摩擦の扱い、数値積分の
細かい違い）に頼って歩いているなら、別のシミュレータに移すと歩けなくなります。
別のシミュレータでも歩けるなら、実機（sim2real）に持っていく前の確認として
一段安心できます。

```{note}
Genesis 版は書籍の本文には載っていない、サポートページだけの内容です。実機に
書き込んでいる方策は、これまでどおり {doc}`walk` のもの（MuJoCo で学習）です。
```

## ブラウザで歩かせてみる

下は「RL 方策（Genesis で学習）」を選んだ状態で開きます。**Genesis で学習した
重みを、MuJoCo の WebAssembly 版で動かしています。** 物理は {doc}`walk` と同じ
（足先の球 4 つだけが接地、サーボは位置制御 + 逆起電力の粘性減衰、指令は
20〜35 ms 遅れて届く）で、方策の入出力（観測 87 次元・関節 8 つ）も同じです。
「制御」を「RL 方策」に切り替えると、MuJoCo で学習した方策と見比べられます。

```{raw} html
<p>
  <a class="sd-btn sd-btn-primary" href="../assembly/quadruped/walk/index.html?mode=genesis"
     target="_blank" rel="noopener">sim2sim のシミュレーションを開く ↗</a>
</p>
<iframe src="../assembly/quadruped/walk/index.html?mode=genesis"
        style="width:100%; height:70vh; border:1px solid var(--pst-color-border, #ddd); border-radius:8px;"
        loading="lazy"
        title="Genesis で学習した四脚の方策を MuJoCo で歩かせるシミュレーション"></iframe>
```

ブラウザ版と同じ MuJoCo WASM を Node で回し、指令ごとに 20 秒ずつ 5 回歩かせた
実測です（後半 10 秒の平均）。

| 指令 | 前進 [m/s] | 旋回 [rad/s] | 転倒 |
|---|---|---|---|
| 前進 0.06 m/s | 0.057 | −0.026 | 0 / 5 |
| 前進 0.09 m/s | 0.086 | 0.000 | 0 / 5 |
| 前進 0.12 m/s | 0.110 | 0.022 | 0 / 5 |
| 前進 0.15 m/s | 0.132 | 0.034 | 0 / 5 |
| 旋回 0.3 rad/s | −0.006 | 0.155 | 0 / 5 |

## Genesis と MuJoCo で同じ方策を比べる

`rl/genesis/sim2sim.py` は、1 つの方策を Genesis と MuJoCo の両方で、同じ指令・
同じ測り方で歩かせます。MuJoCo 側は CPU 版の学習環境（`rl/cpu/quad_env.py`）で、
ブラウザ版と同じ物理です。下は配布している方策（seed 1、iteration 2299）を
64 台 × 20 秒ずつ歩かせた実測で、速さは後半 10 秒の平均です。

| 指令 vx, wz | Genesis 前進 / 旋回 | MuJoCo 前進 / 旋回 | 転倒（G / M） | 対角の同期（G / M） | 滑り [mm/s]（G / M） |
|---|---|---|---|---|---|
| 0.06, 0 | 0.061 / −0.015 | 0.057 / −0.023 | 0 / 0 | 0.81 / 0.80 | 17 / 27 |
| 0.09, 0 | 0.091 / −0.002 | 0.087 / 0.001 | 0 / 0 | 0.85 / 0.85 | 19 / 30 |
| 0.12, 0 | 0.113 / 0.012 | 0.111 / 0.024 | 0 / 0 | 0.89 / 0.85 | 21 / 30 |
| 0, 0.3 | 0.000 / 0.130 | −0.006 / 0.153 | 0 / 0 | 0.72 / 0.63 | 18 / 25 |
| 0.06, −0.3 | 0.053 / −0.153 | 0.047 / −0.168 | 0 / 0 | 0.80 / 0.80 | 21 / 28 |

対角の同期は、対角 2 本（左前 + 右後、右前 + 左後）が同時に接地・離地している
時間の割合で、きれいなトロットほど 1 に近づきます。滑りは、接地している足先の
水平速度の平均です。

- **前進の速さは 0.006 m/s 以内で一致します。** MuJoCo の方がわずかに遅く、
  0.06・0.09 m/s の指令では MuJoCo で 0.003 m/s 指令に届きません。
- **どちらでも 1 台も倒れません。** 学習時のドメインランダマイゼーション
  （摩擦・質量・重心・サーボのゲインなどを機体ごとに変える）を入れた機体でも、
  MuJoCo で 64 台とも倒れませんでした（前進 0.09 m/s の指令で 0.082 m/s）。
- **足先の滑りは MuJoCo の方が 1.5 倍ほど大きくなります**（20 mm/s 前後 →
  30 mm/s 前後）。接触の解き方が違うためで、MuJoCo の方が足先がわずかに
  流れます。
- 旋回は両方とも指令の半分ほど（0.3 rad/s の指令で 0.13〜0.17 rad/s）しか
  出ません。これは Genesis 版の方策そのものの性質です。

### 逆向き: MuJoCo で学習した方策を Genesis で歩かせる

配布している MuJoCo の方策（{doc}`walk` のもの）を、同じスクリプトで Genesis に
移しても歩きます（32 台 × 12 秒、転倒はどちらも 0）。

| 指令 vx, wz | Genesis 前進 / 旋回 | MuJoCo 前進 / 旋回 |
|---|---|---|
| 0.12, 0 | 0.117 / −0.002 | 0.120 / −0.008 |
| 0, 0.3 | −0.001 / 0.174 | −0.004 / 0.214 |
| 0.06, −0.3 | 0.047 / −0.187 | 0.046 / −0.225 |

この方策は 0.06・0.09 m/s の指令では、どちらのシミュレータでも歩き出さずに
立ったままでした。

## Genesis で学習する

学習コードは `13_quadruped/rl/genesis/` にあります。タスク（観測・報酬 26 項・
指令・終了条件・ドメインランダマイゼーション・PPO の設定）は CPU 版の
`rl/cpu/task.py` をそのまま読み込み、物理だけを Genesis（GPU）に置き換えて
います。チェックポイントの形式は mjlab 版・CPU 版と同じなので、同じエクスポータで
実機用のヘッダとブラウザ用の JSON に書き出せます。

```bash
cd 13_quadruped/rl/genesis               # docs/os-on-arduino/code から
uv sync                                   # genesis-world 1.4.4 + rsl-rl-lib 5.0.1 + mujoco 3.7.0
export ARDUINO_QUAD_HOME_HEIGHT=0.11 ARDUINO_QUAD_GAIT_PERIOD=0.32
uv run train.py --num-envs 4096 --iterations 2300 --seed 1
uv run sim2sim.py --checkpoint logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt

# 実機用ヘッダ（.h / .npz / .json）と、ブラウザ用の policy_genesis.json
uv run python ../../host/export_quad_policy.py \
    logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt 出力先 --backend genesis
uv run python ../../host/make_walk_bundle.py 出力先 \
    ../../../../docs/assembly/quadruped/walk/policy_genesis.json
```

RTX 4090 1 枚で 4096 環境 × 2300 iteration が **約 41 分**でした（1 iteration
0.72〜0.79 秒。2 本を別々の GPU で同時に回したときの値）。seed 2 も同じく歩けるように
なりましたが、胴体の揺れが大きかった（ロール・ピッチ 4〜5°、seed 1 は 1〜2°）ので
seed 1 を配布しています。

Mac（Apple シリコン）でも同じコマンドで学習できます。`--device` の既定の `gpu` は、Mac では
Genesis が Metal、PPO の更新が MPS（Apple の GPU で torch を動かす仕組み）になります。
M4 Max では 4096 環境の 1 iteration が約 1.4 秒でした（5 iteration だけ回して測った値）。
`uv sync` で torch の wheel が無いと言われたら x86_64 の Python が選ばれているので、
`uv sync --python cpython-3.12-macos-aarch64` で arm64 の Python を指定してください。

歩くところは `render.py` で mp4 に書き出せます。歩かせるのは MuJoCo（既定）か
Genesis（`--sim genesis`）で、絵はどちらも MuJoCo で描きます。画面の無い Linux（Colab や
ssh 先のサーバ）では、`render.py` が自動で `MUJOCO_GL=egl` にします。

```bash
uv run render.py \
    --checkpoint logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt --out walk.mp4
```

### Google Colab で学習する

手元に GPU が無くても、ブラウザだけで学習から書き出しまで通せるノートブックが
あります。

```{raw} html
<p>
  <a href="https://colab.research.google.com/github/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/rl/colab/genesis_colab.ipynb"
     target="_blank" rel="noopener">
    <img src="https://colab.research.google.com/assets/colab-badge.svg"
         alt="Open In Colab"></a>
</p>
```

ノートブックの流れ:

1. GPU の確認（**ランタイム → ランタイムのタイプを変更 → T4 GPU**）
2. コードを取ってきて、学習環境（genesis-world + rsl_rl + MuJoCo）を入れる
3. **配布済みの MuJoCo の方策を Genesis で歩かせる** — 環境が正しく組めたかの確認
4. 割り当てられた GPU で 30 iteration 回して**学習速度を実測**し、所要時間を見積もる
5. 学習する（チェックポイントは Google Drive に置いて、切れても続きから再開できる）
6. 学習した方策を Genesis と MuJoCo の両方で歩かせて比べ、
   **歩くところを動画で並べて見る**（左が MuJoCo、右が Genesis）
7. 実機用の `.h` と、ブラウザ版の `policy_genesis.json` に書き出す

書き出した `policy_genesis.json` を `docs/assembly/quadruped/walk/` に置き換えると、
上のブラウザ版の「RL 方策（Genesis で学習）」が自分の方策になります。

### MuJoCo 版との違い

| | MuJoCo（mjlab・CPU 版） | Genesis 版 |
|---|---|---|
| 物理 | MuJoCo（mjlab は GPU の MuJoCo Warp、CPU 版は `mujoco.rollout`） | Genesis（GPU） |
| タスクの数値 | `rl/cpu/task.py` | 同じものを読む |
| 足先の摩擦 | 足先の値を使う（`priority`） | 接触する 2 つの大きい方を使う仕様なので、床の摩擦を下限の 0.01 にして足先の値が効くようにしている |
| リセット直後の 0 rad 指令・1 物理ステップ古い報酬 | mjlab の実装どおり再現（`rl/cpu/README.md`） | 再現しない（ロボットではなく mjlab の実装の細部なので） |
| 凹凸地面・ERFI | あり（環境変数で有効） | なし（指定するとエラーで止まる） |

```{note}
`uv run ../../host/export_quad_policy.py`（`python` を挟まない形）にすると、
uv がスクリプトの置き場所の `host/` を別プロジェクトとして扱い、torch の無い
環境で動かして失敗します。`uv run python ...` と書いてください。
```

## 参考

- Genesis（genesis-world 1.4.4）: <https://pypi.org/project/genesis-world/1.4.4/>
- 接触の摩擦を 2 つの大きい方に決める処理: genesis-world 1.4.4 の
  `genesis/engine/solvers/rigid/collider/contact.py`
