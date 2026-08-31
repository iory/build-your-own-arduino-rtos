#!/usr/bin/env python3
"""端末の中で、本物の bash に 1 文字ずつコマンドを打ち込む。

見えているプロンプトも出力も本物で、打鍵だけを機械が代行している。
PATH にはあえて ~/.local/bin を入れていない。入れてしまうと、入れた直後の
シェルではまだ uv が見つからない、という読者が必ず踏むところが再現できない。
"""
import os
import sys

import pexpect

HOME = os.path.expanduser("~")
RCFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_bashrc")

STEPS = [
    ("curl -LsSf https://astral.sh/uv/install.sh | sh", 11.0),
    ("uv --version", 2.0),                 # まだ PATH に無いので command not found
    ("source ~/.local/bin/env", 1.5),
    ("uv --version", 2.5),                 # 今度は通る
]

c = pexpect.spawn(f"/bin/bash --rcfile {RCFILE} -i", encoding="utf-8",
                  timeout=None, dimensions=(20, 82),
                  env={"TERM": "xterm-256color", "HOME": HOME,
                       "PATH": "/usr/local/bin:/usr/bin:/bin"})
c.logfile_read = sys.stdout


def pump(sec):
    try:
        c.expect(pexpect.TIMEOUT, timeout=sec)
    except Exception:
        pass


pump(2.5)                       # プロンプトが出るのを待つ
for cmd, wait in STEPS:
    for ch in cmd:              # 人が打っているくらいの速さで
        c.send(ch)
        pump(0.07)
    pump(0.5)
    c.send("\n")
    pump(wait)
    pump(1.5)                   # 出力を読む間
pump(5)                         # 終わったあとの余白
