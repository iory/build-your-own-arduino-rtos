# 歩行方策を自分で学習する

第13章の四脚を歩かせている方策は、[配布済みのもの](walk.md)をそのまま使えば
学習しなくても動きます。ここでは**それを自分で学習し直す**手順をまとめます。
報酬を変えたい、速度の上限を上げてみたい、別の歩容を出したい——そういう
ときの入口です。

学習には NVIDIA GPU が要ります。**手元に無い場合は Google Colab
（無料枠の T4）で最後まで通せます。**

## 学習コードの構成

学習は [unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab)
（[mjlab](https://github.com/mujocolab/mjlab) + rsl_rl の PPO 学習基盤）の上で
行います。`docs/os-on-arduino/code/13_quadruped/rl/` はその上流に**被せる overlay** で、
それ自体は単体で動くプログラムではありません。

| ファイル | 中身 |
|---|---|
| `robot_cfg.py` | 機体定義（アクチュエータ、初期姿勢、`home` 角） |
| `env_cfgs.py` | 観測・コマンド・ドメインランダマイゼーション |
| `rewards.py` | 報酬項（速度追従、歩容、姿勢、エネルギー等） |
| `rl_cfg.py` | PPO のハイパーパラメータとネットワーク構成 [96, 64] |
| `runner.py` | ERFI（トルク外乱）を足した学習ランナー |
| `scripts/` | 環境構築・学習・再生・動画書き出し |

`setup.sh` が上流を `.upstream/unitree_rl_mjlab` に clone し、`rl/` を
`src/tasks/velocity/config/arduino_quad` として**シンボリックリンク**で
置きます。上流は `src/tasks/` 配下を自動 import するので、これだけで
次の 4 タスクが登録されます。

| タスク ID | 用途 |
|---|---|
| `ArduinoQuad-Flat` | 平地・素の velocity レシピ（立ち上げ確認用） |
| `ArduinoQuad-Walk` | 平地 + 歩容シェーピング（**本命。トロット歩行はこれ**） |
| `ArduinoQuad-Robust` | Walk と同じだが初期状態を崩す（実機前の頑健化） |
| `ArduinoQuad-Recovery` | 転倒姿勢から立ち上がる |

## Google Colab で学習する（GPU が無い人向け）

ブラウザだけで、環境構築から Arduino 用ヘッダの書き出しまで通せる
ノートブックを用意しました。

```{raw} html
<p>
  <a href="https://colab.research.google.com/github/iory/build-your-own-arduino-rtos/blob/main/code/13_quadruped/rl/colab/arduino_quad_colab.ipynb"
     target="_blank" rel="noopener">
    <img src="https://colab.research.google.com/assets/colab-badge.svg"
         alt="Open In Colab"></a>
</p>
```

ノートブックの流れ:

1. GPU の確認（**ランタイム → ランタイムのタイプを変更 → T4 GPU**）
2. コードを取ってきて、学習環境（mjlab + MuJoCo Warp + rsl_rl）を入れる
3. **配布済みの学習済み方策を再生して動画で見る** — ここまでで
   「シミュレータ・方策・エクスポート」が揃って動いていることを確認できます
4. 割り当てられた GPU で 30 iteration 回して**学習速度を実測**し、
   所要時間を見積もる
5. 学習する（チェックポイントは Google Drive に保存）
6. セッションが切れたら続きから再開する
7. 学習した方策を動画で確認して、`arduino_quad_policy.h` に書き出す

```{note}
Colab の無料枠はセッションが数時間で切れます。学習ログを Google Drive に
逃がしておけば、`--agent.resume True` で何度でも続きから再開できます。
ノートブックの 6 章がその設定です。
```

### 無料枠の T4 でどれくらいかかるか

2026-08-31 に Colab の無料枠（Tesla T4 15 GB、Python 3.13）で、環境構築から
`.h` の書き出しまで実際に通しました。そのときの実測です。

| | |
|---|---|
| 環境構築（`setup.sh`） | 約 1 分 |
| 学習（2048 環境） | **1.42 秒/iteration、34,900 steps/s** |
| 書籍と同じ 4,500 iteration に必要な時間 | **約 1.8 時間** |
| 方策の再生（300 ステップの動画） | 初回 5〜6 分（GPU カーネルの生成を含む）、2 回目以降 3〜4 分 |
| `.h` の書き出し | 約 1 分 |

参考までに、同じ設定を RTX 4090 で回すと 0.77 秒/iteration・63,700 steps/s
でした。**T4 は 4090 の半分強の速度**で、無料枠でも書籍と同じ規模の学習が
現実的な時間で終わります。

### 何 iteration で歩くようになるか

ノートブック既定の設定（`ArduinoQuad-Walk`、2048 環境）で 1500 iteration
回し、100 iteration ごとのチェックポイントを**指令 0.09 m/s で 6 秒ずつ
再生した実測**です（RTX 4090、1 シード）。

| iteration | 実測 前進 [m/s] | iteration | 実測 前進 [m/s] |
|---|---|---|---|
| 0 | −0.000 | 800 | 0.086 |
| 100 | **−0.219** | 900 | 0.071 |
| 200 | −0.194 | 1000 | 0.072 |
| 300 | 0.005 | 1100 | 0.096 |
| 400 | 0.014 | 1200 | 0.072 |
| 500 | 0.046 | 1300 | 0.086 |
| 600 | 0.046 | 1400 | 0.101 |
| 700 | 0.058 | 1499 | **0.089** |

**100〜200 iteration では後ろに進みます。** 前進報酬を拾うより先に
「転ばない」を覚えるためで、失敗ではありません。前進に転じるのが 300 付近、
指令の速度に届くのが 800 前後、そこから先は 0.07〜0.10 の範囲で揺れながら
追従します。各点は 1 エピソードの測定なので、隣り合う点の ±0.02 m/s は
誤差の範囲です。

```{note}
これは**既定の設定で学習した別の方策**であって、[配布済み方策](walk.md)
（home 高さ 0.11 m、歩容周期 0.32 s、3498 iteration、指令 0.12 m/s で 0.165 m/s）の再現では
ありません。エクスポートされるヘッダには学習時の home 角が書き込まれるので、
実機側の整合はそのまま取れます。
```


## 手元の GPU で学習する

```bash
cd docs/os-on-arduino/code/13_quadruped
./rl/scripts/setup.sh                    # 上流を clone して overlay を置き、依存を入れる
source rl/scripts/env.sh                 # 機体の MJCF の場所を教える
./rl/scripts/train.sh ArduinoQuad-Walk --env.scene.num-envs=4096
```

`setup.sh --no-install` にすると、clone と配置だけ行って依存の導入を飛ばせます。

### 版の固定について

`setup.sh` は依存を**版で固定して**入れます。上流 (unitree_rl_mjlab) の
`setup.py` が指すままでは、この機体の設定が読み込めません。

| | | なぜ固定するか |
|---|---|---|
| mjlab | 1.3.0 | サーボの逆起電力 (`viscous_damping`) と 27 ms の指令遅れ (`delay_min/max_lag`) が 1.2.0 に無い。後者は sim2real の要なので外せない |
| mujoco-warp | 3.7.0.1 | mjlab 1.3.0 が要求する版 |
| mujoco | 3.7.0 | 最新版が入ると mujoco-warp の import が落ちる |
| warp-lang | 1.14.0 | 1.16 では学習開始時のカーネル生成が落ちる |
| scipy | 1.15 以上 | mjlab 1.3.0 が使っているのに宣言していない |

`setup.sh` は加えて、上流のロボット定義が使う `update_assets`（mjlab 1.3.0 で
削除された）を補う小さな互換パッチを、clone したチェックアウトに当てます。
当てないと `src/assets/robots` 全体が ImportError になり、`ArduinoQuad-*` の
登録まで巻き添えになります。

この組み合わせは **2026-08-31 に RTX 4090 で、環境構築から `.h` の書き出しまで
通して確認**しています（2048 環境で 0.77 秒/iteration、63,700 steps/s）。

学習した方策を見るには:

```bash
./rl/scripts/play.sh ArduinoQuad-Walk    # ビューアを開く（画面のある環境）
```

画面の無いサーバや Colab では、ビューアではなく mp4 に落とします:

```bash
source rl/scripts/env.sh
cd "$ARDUINO_QUAD_UPSTREAM"
python "$ARDUINO_QUAD_ROOT/rl/scripts/record_video.py" \
    --ckpt logs/rsl_rl/arduino_quad_velocity/<run>/model_1500.pt \
    --vx 0.09 --steps 300 --out walk.mp4
```

`--bundle` を渡すと、チェックポイントの代わりに**エクスポート済みの方策**
（`walk/` の `.npz` + `.json`）を、実機と同じ numpy 実装で再生します。

## 実機に持っていく

チェックポイントから Arduino 用のヘッダを書き出します。

```bash
cd "$ARDUINO_QUAD_UPSTREAM"
python "$ARDUINO_QUAD_ROOT/host/export_quad_policy.py" \
    logs/rsl_rl/arduino_quad_velocity/<run>/model_1500.pt \
    出力先ディレクトリ ArduinoQuad-Walk
```

出てくるのは 3 つです。

| ファイル | 使うところ |
|---|---|
| `arduino_quad_policy.h` | Arduino スケッチ（`walk/arduino/arduino_quad/`） |
| `arduino_quad_policy.npz` | PC 直結版（`walk/host/quad_host.py`） |
| `arduino_quad_policy.json` | 同じ情報の機械可読版 |

重みだけでなく、**観測の並び・履歴の順序・正規化の統計・home 角・action の
スケール**まで、学習時の環境から読み出して書き込みます。ここを人間が
書き写すと、エラーも出ないまま「震えるだけのロボット」になるためです。
書き出したあとで numpy 実装と PyTorch の出力を突き合わせて検証します。

実機で動かす手順は {doc}`walk` と `walk/HANDOFF.md` を読んでください。
**最初は必ず機体を吊るしてから**動かすこと。

## つまずきやすいポイント

| 症状 | 原因と対処 |
|---|---|
| wandb のログインを求められて止まる | mjlab の既定ロガーが wandb です。`--agent.logger tensorboard` を付ける |
| `MJCF が見つかりません` | `source rl/scripts/env.sh` を忘れています（`$ARDUINO_QUAD_XML`） |
| 画面が無い環境で `play.sh` が止まる | ビューアを開こうとしています。`record_video.py` を使ってください |
| `home 姿勢が環境と方策で違います` | 方策と環境の学習設定が食い違っています。メッセージが出す `ARDUINO_QUAD_HOME_HEIGHT=...` を付けて実行し直す |
| 学習が「その場で止まる」方策に収束する | 到達できない速度を指令しています。この機体でサーボの余裕の中に収まるのは 0.05〜0.09 m/s です |

（読者からの質問に応じて随時追記します。質問は
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues)
へどうぞ）
