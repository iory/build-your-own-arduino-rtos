# rl — 歩行方策の学習コード

第13章の四脚を歩かせている方策 (`../walk/arduino_quad_policy.*`) を学習した
コード。紙面の都合で本には載せられなかったぶんのサポート。

## 動かす

これ自体は単体で動くプログラムではなく、
[unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab)
(mjlab + rsl_rl の PPO 学習基盤) に被せる **overlay** です。
用意から学習まで、次の 3 つで足ります。

```bash
./rl/scripts/setup.sh                    # 上流を .upstream/ に clone し、overlay を置く
source rl/scripts/env.sh                 # 機体の MJCF の場所を教える
./rl/scripts/train.sh ArduinoQuad-Walk --env.scene.num-envs=4096
```

`setup.sh` は上流を `.upstream/unitree_rl_mjlab` に clone し、この `rl/` を
`src/tasks/velocity/config/arduino_quad` として**シンボリックリンク**で
置きます。上流は `src/tasks/` 配下を自動 import するので、これだけで
`ArduinoQuad-*` の 4 タスクが登録されます。リンクなので、`rl/` を直接
編集すればそのまま反映されます。

学習した方策を再生するときは `./rl/scripts/play.sh ArduinoQuad-Walk` です。

| タスク ID | 用途 |
|---|---|
| `ArduinoQuad-Flat` | 平地・素の velocity レシピ（立ち上げ確認用） |
| `ArduinoQuad-Walk` | 平地 + 歩容シェーピング（**本命。トロット歩行はこれ**） |
| `ArduinoQuad-Robust` | Walk と同じだが初期状態を崩す（実機前の頑健化） |
| `ArduinoQuad-Recovery` | 転倒姿勢から立ち上がる |

> 依存の導入には GPU と数 GB の空きが要ります。置き場所だけ先に作りたいときは
> `./rl/scripts/setup.sh --no-install` で、clone と配置だけ行えます。

## 構成

ロボット定義・報酬・環境設定・学習設定を、上流に対して差し替えます:

| ファイル | 中身 |
|---|---|
| `robot_cfg.py` | 機体定義（アクチュエータ、初期姿勢、`home` 角） |
| `env_cfgs.py` | 観測・コマンド・ドメインランダマイゼーションの設定 |
| `rewards.py` | 報酬項（速度追従、歩容、姿勢、エネルギー等） |
| `rl_cfg.py` | PPO ハイパーパラメータとネットワーク構成 [96, 64] |
| `runner.py` | 学習・再生・エクスポートの入り口 |
| `_compat.py` | mjlab のバージョン差の吸収 |

ロボット記述一式（URDF・MJCF・メッシュ・RViz 設定・MJCF を SolidWorks
エクスポートから再現するスクリプト）は
[`../arduino_os_quad_robot/`](../arduino_os_quad_robot/) にある。
ROS 2 なら `ros2 launch arduino_os_quad_robot display.launch.py` で
RViz 表示できる。

## 方策の仕様（学習結果）

- 観測 87 次元（指令・歩容位相・関節角・関節速度・前回 action、各 3 履歴）。**IMU は使わない**
- MLP [96, 64]・ELU・8 出力。サーボ目標 = home 角 + 0.25 × action
- 制御 50 Hz、歩容周期 0.32 s
- シミュレーション性能: 前進 0.148 m/s、対角トロット 3.33 Hz

学習済み方策そのもの・実機で回すコード（PC 直結版 / Arduino 版）・校正
ウィザードは [`../walk/`](../walk/) にある。まず `../walk/HANDOFF.md` を読むこと。
