# HANDOFF — サポートページ構築の記録 (2026-08-24 時点)

『つくりながら学ぶ！リアルタイムOS自作入門』のサポートページ一式を
どう作り、どう運用するかのメモ。次に作業する人（未来の自分を含む）向け。

- 公開サイト: **https://iory.github.io/build-your-own-arduino-rtos/**
- このリポジトリ: サイトのソース + 公開サンプルコード（ミラー先）

## 1. リポジトリ構成と自動化

```
learning-os-from-arduino (private, 原稿)          build-your-own-arduino-rtos (この repo)
├─ docs/os-on-arduino/ … 原稿本文(非公開のまま)   ├─ docs/ja/source/  日本語サイト(ルート配信)
├─ docs/os-on-arduino/code/  ←単一の正           ├─ docs/en/source/  英語スケルトン(/en/)
│    └─[publish-code workflow が push の度に]──►  ├─ code/            ミラー先(直接編集禁止)
└─ .github/workflows/publish-code.yml             ├─ docs/assembly/   3Dビューア・歩行デモ(静的)
                                                  └─ .github/workflows/docs.yml → GitHub Pages
```

- **コードの誤植修正は原稿リポジトリ側だけ直す**。push すると publish-code
  workflow が `docs/os-on-arduino/code/` を丸ごとこちらの `code/` に rsync
  （`--delete`、git 管理ファイルのみ = 原稿本文が漏れる経路なし）。
- 認証: この repo に書き込み deploy key「code sync from learning-os-from-arduino」、
  秘密鍵は原稿 repo の Actions secret `CODE_SYNC_DEPLOY_KEY`。
- サイトは push で自動デプロイ（`docs.yml`。`code/**` だけの push では走らない）。
- **公開状態**: 両リポジトリとも private。**Pages サイトだけ公開**されている
  （GitHub の仕様）。章ページの GitHub コードリンクは repo を public にするまで
  第三者には 404。公開スイッチ =
  `gh repo edit iory/build-your-own-arduino-rtos --visibility public`
- サンプルコードのライセンスは **MIT**（`code/LICENSE`、原稿側から同期）。

### 落とし穴（一度踏んだ）

- グローバル gitignore の `.*` が `.github/` を黙って除外する。両 repo の
  `.gitignore` に `!.github/` を入れて対処済み。新しい dotfile を足すときは
  `git status` で本当にステージされたか見ること。
- rebase 中の `--theirs` は「適用中の自分のコミット」側。上流の再エクスポートと
  衝突したときに取り違えない。

## 2. サイトの内容

| ページ | 内容 |
|---|---|
| はじめに | 準備するもの / Arduino IDE / PlatformIO（UNO R4 **WiFi** 必須の注意） |
| 章ごとのサポート | 全 17 章。各章に code/ ディレクトリへのリンクとビルドコマンド |
| hardware/bom | 部品表。秋月直リンク、合計 約¥35,100、PD バッテリー選定、STL/3MF 配布 |
| hardware/assembly | CAD 由来の組み立て手順。3D ビューア(iframe) + PDF + 手順画像 |
| hardware/walk | 歩行の RL サポート。**ブラウザ内 MuJoCo デモ** + 学習/実機の解説 |
| FAQ / 正誤表 | 器 |

執筆方針（ユーザー指示で確定したもの）:

- **読者向けページに「どう作ったか」のメタ情報は書かない**（自動生成・検証内部の
  話は削除済み。CAD 書き出しの solidworks_urdf_exporter2 への 1 行クレジットのみ可）
- 印刷の説明は XLeRobot 程度の軽さ（スライサ深掘りはしない）
- ネジは「サーボ付属品（M2×6 / M3×6）だけで組める」で統一。CAD の M3x4 は
  表記上 M3x6 に置換済み（graph.json の名前だけ。**CAD 側の部品差し替えが本筋**、
  再エクスポートすると戻るので注意）
- キャリブレーション: 組む前は **ID 振りだけ**。0 点は組み上げ後にソフトで取る

## 3. 組み立てビューア・配布物 (docs/assembly/quadruped/)

生成元は **create-assembly-view リポジトリ**（モデル: `models/sts3215_quadruped/`、
CAD ソース: `cad/`）。再生成手順は README.md の「組み立てビューアの再生成」参照。

- ビューア/PDF/手順 PNG: create-assembly-view のフルパイプラインで生成
  （プラン → render → viewer → pdf）。全 9 手順、掃引検証パス
- `stl/`: SolidWorks 直接出力の body / bracket_outline / leg_link1（mm）
  + 作者スライス済み **Bambu Studio プロジェクト** `body.3mf` / `leg_parts.3mf`
  （X1C・0.4 ノズル・0.28mm・ABS・ツリーサポート自動・Textured PEI）
- 座標系の約束: **Z-up、+X がロボットの前**。ビューアの three.js は
  `camera.up.set(0,0,1)` 済み（PNG レンダラは元から Z-up 前提）

## 4. 歩行デモ (docs/assembly/quadruped/walk/)

学習済み方策をブラウザ内の **MuJoCo 3.12 WebAssembly**（公式 npm
`@mujoco/mujoco` のシングルスレッド版をベンダリング、特殊ヘッダ不要）で
実行する。初回ロード約 16 MB。

- `walk_core.js` — 方策の JS 移植（87 → [96,64] → 8、ELU、履歴 3 段の観測
  組み立て。`code/13_quadruped/walk/host/quad_policy.py` と同じ契約）
  + **本文 13.5 の sin/cos trot** の移植（`gait.cpp` + `leg_ik.cpp`、
  KNEE_OFFSET 込み 2 リンク IK）。UI の「制御」で切替
- `model/` — arduino_os_quad_robot の MJCF + STL 34 個
- `policy.json` — npz から変換した重み（334 KB）
- 検証は **node でヘッドレス**にやった: RL は cmd 0.12 で 10 s に 1.26 m 前進、
  naive はストライド 0.06 で 0.123 m/s、後退・旋回(RL のみ)・直立維持を確認。
  再検証スクリプトはセッションの scratchpad にあった `test_walk.mjs` /
  `test_naive.mjs`（要再作成なら walk_core.js を node から import して同じ流れ）
- 既知の罠: three.js の `OrbitControls` は bare specifier `'three'` を import
  するので **importmap 必須**（組立ビューアと同じ）

## 5. 公開したコード (code/13_quadruped/)

紙面に載らなかった学習まわりのサポート（すべて原稿 repo 側が正）:

- `walk/` — 学習済み方策 (json/npz/C ヘッダ)・PC 直結の host 実行・
  Arduino スケッチ 2 つ（歩行本体 / 校正ウィザード）・HANDOFF.md・
  sim2real の記録
- `rl/` — unitree_rl_mjlab (rsl_rl PPO) に被せる overlay 7 ファイル + README
- `arduino_os_quad_robot/` — ロボット記述の ROS パッケージ一式
  （**URDF** ×2・MJCF・GLB メッシュ・RViz 設定・display.launch.py・
  SolidWorks エクスポート → MJCF の再現スクリプト）。
  URDF の `package://assem1_description` は `arduino_os_quad_robot` に修正済み

## 6. 残タスク / 次にやるなら

- [ ] リポジトリを public に切り替える（コードリンクが世に開く。タイミングは著者判断）
- [ ] CAD 側で股関節ネジ部品を M3x4 → M3x6 に差し替え（再エクスポート時の表記戻り対策）
- [ ] 英語ページの本文埋め（現状スケルトン + "Translations in progress"）
- [ ] 正誤表の運用開始（今は器だけ）
- [ ] 歩行デモの実ブラウザ確認は Chrome のみ実施。Safari/モバイルは未確認
- [ ] 書籍リポジトリ内の旧 STL (`code/13_quadruped/stl/`, MJCF 由来で現行 CAD と
  形状が違う) の差し替えか削除
