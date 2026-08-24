# rl — 歩行方策の学習コード

第13章の四脚を歩かせている方策 (`../walk/arduino_quad_policy.*`) を学習した
コード。紙面の都合で本には載せられなかったぶんのサポート。

## 構成

これは単体で動くプログラムではなく、
[unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab)
(mjlab + rsl_rl の PPO 学習基盤) に被せる **overlay** で、
ロボット定義・報酬・環境設定・学習設定を差し替える:

| ファイル | 中身 |
|---|---|
| `robot_cfg.py` | 機体定義（アクチュエータ、初期姿勢、`home` 角） |
| `env_cfgs.py` | 観測・コマンド・ドメインランダマイゼーションの設定 |
| `rewards.py` | 報酬項（速度追従、歩容、姿勢、エネルギー等） |
| `rl_cfg.py` | PPO ハイパーパラメータとネットワーク構成 [96, 64] |
| `runner.py` | 学習・再生・エクスポートの入り口 |
| `_compat.py` | mjlab のバージョン差の吸収 |

ロボットモデル (MJCF + STL) はサポートページの
[歩行シミュレーションのモデル一式](https://iory.github.io/build-your-own-arduino-rtos/assembly/quadruped/walk/model/)
と同一のもの。

## 方策の仕様（学習結果）

- 観測 87 次元（指令・歩容位相・関節角・関節速度・前回 action、各 3 履歴）。**IMU は使わない**
- MLP [96, 64]・ELU・8 出力。サーボ目標 = home 角 + 0.25 × action
- 制御 50 Hz、歩容周期 0.32 s
- シミュレーション性能: 前進 0.148 m/s、対角トロット 3.33 Hz

学習済み方策そのもの・実機で回すコード（PC 直結版 / Arduino 版）・校正
ウィザードは [`../walk/`](../walk/) にある。まず `../walk/HANDOFF.md` を読むこと。
