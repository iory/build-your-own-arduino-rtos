# 2 段モデル (段 A + 関節ごとの残差 段 B) — Genesis 学習

sim のみ。実機エクスポート (`host/export_quad_policy.py`) と `sim2sim.py` の MuJoCo 側は対象外です。

## 1. 目的

従来は 87 次元の MLP が 1 本で、1 フレーム (20 ms) 以上の遅れ (遅延ライン 20〜35 ms) の先を読んで出力していました。
段 A の出力に加えて、**効き始める直前 (1 フレーム後) の状態 s_t** を見て関節ごとに補正する段 B を足します。
その分、sim のサーボ遅延は 0 にします (遅れはパイプライン構造が表す)。

## 2. 時刻と入力

時刻 t に最終出力 a_t を出します。段 A は 1 フレーム前に走ったものとして扱います。

| | 状態 (command, phase, q, q̇) | アクション |
|---|---|---|
| 段 A | s_{t-3}, s_{t-2}, s_{t-1} | a_{t-4}, a_{t-3}, a_{t-2} |
| 段 B (関節 j) | q_j, q̇_j: s_{t-2}, s_{t-1}, **s_t** | a_j: a_{t-3}, a_{t-2}, a_{t-1} |

- アクションは **最終出力 (段 B 適用後)** の履歴です (実際にサーボへ送った値)。
- 段 A の入力は、従来の 87 次元方策と同じ形式・同じ並びです (`gs_env.py` のアクター観測 4 フレームの先頭 3 フレーム)。
- 観測ノイズ (`joint_pos` ±0.02、`joint_vel` ±0.3) は、段 A と段 B で同じバッファを共有します (同じ時刻の読み値は同じ値)。
- Critic は変更しません (特権情報、現在値 1 フレーム)。

## 3. ネットワーク (`twostage.py`)

```
â   = A(norm_A(obs[0:3 frames]))                       # 87 → 96 → 64 → 8 (ELU)
Δ_j = B_j(norm_B([â_j, a_j×3, q_j×3, q̇_j×3]))         # 関節ごとに別の MLP: 10 → H → H → 1 (ELU), H=16
a_j = â_j + Δ_j                                        # 残差。B の最終層は 0 初期化 → 開始時は a = â
```

- 段 B は 8 関節で重みを**共有しません** (8 個の独立 MLP。einsum でバッチ化)。他の関節、command、phase は入りません。
- 入力正規化は A 用 (87 次元) と B 用 (8×10 要素ごと) を別々に持ちます。
- PPO のガウス分布の平均が a です。標準偏差は全関節共通のスカラ 8 次元。

## 4. 学習モード (`train.py --mode`)

| モード | 内容 | `init_std` 既定 |
|---|---|---|
| `frozen` | `--stage-a <ckpt>` の既存方策 (MLP と obs 正規化) を段 A に読み込んで**凍結**。B だけ学習 | 0.2 |
| `joint` | A と B をエンドツーエンドで PPO 学習 (A はランダム初期化、`--stage-a` 不可) | 1.0 |
| `baseline` | **段 B なし**。段 A 単体 (87→96→64→8、同じ入力: a_{t-4..t-2}、s_{t-3..t-1}) をゼロから学習し、出力を a_t とする。同じ環境 (4 フレーム履歴、遅延 0) | 1.0 |
| `single` (既定) | 従来どおりの 87 次元 MLP | 1.0 |

```
uv run train.py --mode frozen --stage-a logs/rsl_rl/arduino_quad_velocity/<run>/model_2299.pt
uv run train.py --mode joint
```

- `--init-std`、`--hidden-b` (既定 16) で上書きできます。
- `--resume` は従来どおり、同じモードの学習の再開用です。
- `frozen` では A の MLP と正規化の統計が更新されないことを確認済みです (B の重みだけが動く)。

### 4.1 段 B の効果の比較 (`compare_two_stage.sh`)

`joint` (A+B) と `baseline` (A のみ) を、同じ環境・報酬・iteration 数・env 数で比べます。差は「s_t を見る段 B が付くか」だけです (パラメータは B の分、約 3.4k 個多い)。

- 各モード 3 seed (1, 2, 3)、既定 2300 iteration、4096 env。
- 学習後に、最後のチェックポイントを `sim2sim.py --sim genesis` で、ドメインランダム化なし/あり (`--dr`) の両方、コマンド `0.06,0;0.12,0;0,0.3;0.06,-0.3` で評価します (転倒数、vx/wz、ロール/ピッチ、接地率)。
- 学習曲線 (平均報酬) は tensorboard (`logs/rsl_rl/.../events.*`) で比較します。
- `frozen` (既存方策への後付け) は別の比較です (同じ環境での学習前後)。

```
sh compare_two_stage.sh            # 2300 iter, 4096 env (長時間)
sh compare_two_stage.sh 300 1024   # 短い確認
```

`sim2sim.py` も 2 段/baseline のチェックポイントを自動判定します (`--sim genesis` のみ)。

## 5. 環境の変更 (`gs_env.py`)

- `actor_history` (既定 `T.ACTOR_HISTORY`=3)。2 段モデルでは 4。
- `delay_min_lag` / `delay_max_lag` (既定はタスクの値 4〜7)。2 段モデルのモードでは `train.py` が 0〜0 を渡します。`--delay-min/--delay-max` で変更できます。
  - lag=0 では、遅延ラインを通っても目標がそのサブステップの PD にそのまま効きます。

## 6. 確認用コマンド

```
uv run render.py --checkpoint logs/.../model_N.pt --sim genesis      # 2 段のチェックポイントは自動判定 (--sim genesis のみ)
```

- `render.py` はチェックポイントのキー (`stage_b.w1`) で 2 段かどうかを判定し、4 フレーム履歴・遅延 0 の環境を作ります。
- 動作確認: `joint` と `frozen` で短時間 (3〜4 iter、64 env) の学習が回ること、`frozen` で A が不変であること、保存した 2 段チェックポイントを `render.py` で動画にできることを確認しました。
  性能 (歩けるか) の評価は、長時間の学習をまだ回していないので未確認です。

## 7. 既知の制限

- 2 段モデルは JIT/ONNX エクスポートに対応していません (`as_jit` が `NotImplementedError`)。
- `sim2sim.py` の MuJoCo 側と `render.py --sim mujoco` は 2 段に非対応です。
- `joint` モードの B の入力正規化は、学習中に統計が動きます (rsl_rl の標準的な挙動)。
