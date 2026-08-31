#!/usr/bin/env bash
# 学習環境を用意する。
#
#   ./rl/scripts/setup.sh
#
# rl/ は単体で動くプログラムではなく、上流の PPO 学習基盤
# unitree_rl_mjlab に被せる overlay。上流は src/tasks/ 配下のパッケージを
# 自動 import するので、rl/ を src/tasks/velocity/config/arduino_quad として
# 置いてやれば ArduinoQuad-* のタスクが登録される。
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/env.sh"

UPSTREAM_URL="https://github.com/unitreerobotics/unitree_rl_mjlab.git"
DEST="$ARDUINO_QUAD_UPSTREAM/src/tasks/velocity/config/arduino_quad"
NO_INSTALL="${1:-}"

# 1. 上流を取ってくる
if [ -d "$ARDUINO_QUAD_UPSTREAM/.git" ]; then
  echo "==> 上流はすでにあります: $ARDUINO_QUAD_UPSTREAM"
else
  echo "==> 上流を clone します: $UPSTREAM_URL"
  mkdir -p "$(dirname "$ARDUINO_QUAD_UPSTREAM")"
  git clone --depth 1 "$UPSTREAM_URL" "$ARDUINO_QUAD_UPSTREAM"
fi

# 2. overlay を置く（シンボリックリンクなので、こちらを編集すれば即反映される）
if [ ! -d "$(dirname "$DEST")" ]; then
  echo "上流の構成が変わっています: $(dirname "$DEST") がありません" >&2
  echo "unitree_rl_mjlab 側で src/tasks/velocity/config/ の位置を確認してください" >&2
  exit 1
fi
rm -rf "$DEST"
ln -s "$ARDUINO_QUAD_ROOT/rl" "$DEST"
echo "==> overlay を置きました: $DEST -> $ARDUINO_QUAD_ROOT/rl"

# 3. 依存を入れる
if [ "$NO_INSTALL" = "--no-install" ]; then
  echo "==> --no-install なので依存の導入は飛ばします"
else
  echo "==> 依存を入れます（GPU と数 GB の空きが要ります）"
  ( cd "$ARDUINO_QUAD_UPSTREAM" && pip install -e . )
fi

cat <<MSG

できました。学習は次のように始めます。

    source rl/scripts/env.sh
    ./rl/scripts/train.sh ArduinoQuad-Walk --env.scene.num-envs=4096

タスク ID は ArduinoQuad-Flat / -Walk / -Robust / -Recovery の 4 つです。
歩かせたいなら -Walk を使ってください。
MSG
