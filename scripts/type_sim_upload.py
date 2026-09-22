#!/usr/bin/env python3
"""「自分でビルドした ELF をブラウザで動かす」の、ビルド側の端末を録る。

本物の bash に 1 文字ずつ打ち込む（type_demo.py と同じやり方）。見えている
プロンプトも pio の出力も本物で、打鍵だけを機械が代行している。
record_sim_upload.sh が asciinema の下から呼ぶ。打ち込む bash だけは、読者と同じ
置き場所（~/learning-os-from-arduino/...）を作った仮の HOME（DEMO_HOME）と
DEMO_PATH で動かす。
"""
import os
import sys

import pexpect

RCFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_bashrc")
CODE = "learning-os-from-arduino/docs/os-on-arduino/code"

# (打つコマンド, 打ったあと待つ秒数)。None なら pio の終わりまで待つ
STEPS = [
    (f"cd {CODE}", 1.0),
    ("sed -i 's/Environment OK!/Hello from my build!/' 00_intro/src/main.cpp", 1.0),
    ("grep -n Hello 00_intro/src/main.cpp", 2.0),
    ("pio run -d 00_intro", None),
    ("ls -lh 00_intro/.pio/build/uno_r4_wifi/firmware.elf", 3.0),
]

env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
env.update(HOME=os.environ["DEMO_HOME"], PATH=os.environ["DEMO_PATH"],
           TERM="xterm-256color")
c = pexpect.spawn(f"/bin/bash --rcfile {RCFILE} -i", encoding="utf-8",
                  timeout=None, dimensions=(22, 82), env=env)
c.logfile_read = sys.stdout


def pump(sec):
    try:
        c.expect(pexpect.TIMEOUT, timeout=sec)
    except pexpect.EOF:
        pass


pump(2.0)                       # プロンプトが出るのを待つ
for cmd, wait in STEPS:
    for ch in cmd:              # 人が打っているくらいの速さで
        c.send(ch)
        pump(0.05)
    pump(0.5)
    c.send("\n")
    if wait is None:
        # pio は色付きで出すので、色の付かない最後の行で終わりを見る
        c.expect([r"\d+ succeeded in", r"\d+ failed in"], timeout=600)
        pump(2.5)
    else:
        pump(wait)
pump(4)                         # 終わったあとの余白
