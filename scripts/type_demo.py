#!/usr/bin/env python3
"""端末の中で、本物の bash に 1 文字ずつコマンドを打ち込む。

見えているプロンプトも出力も本物で、打鍵だけを機械が代行している。
"""
import sys
import time

import pexpect

CMDS = [
    "curl -LsSf https://astral.sh/uv/install.sh | sh",
    "uv --version",
]

c = pexpect.spawn("/bin/bash --rcfile /tmp/demo_bashrc -i", encoding="utf-8",
                  timeout=None, dimensions=(20, 82),
                  env={"TERM": "xterm-256color", "HOME": "/home/iory",
                       "PATH": "/home/iory/.local/bin:/usr/local/bin:/usr/bin:/bin"})
c.logfile_read = sys.stdout


def pump(sec):
    try:
        c.expect(pexpect.TIMEOUT, timeout=sec)
    except Exception:
        pass


pump(2.5)                       # プロンプトが出るのを待つ
for i, cmd in enumerate(CMDS):
    for ch in cmd:              # 人が打っているくらいの速さで
        c.send(ch)
        pump(0.07)
    pump(0.6)
    c.send("\n")
    pump(12 if i == 0 else 2)   # インストールは時間がかかる
    pump(2.5)                   # 出力を読む間
pump(6)                         # 終わったあとの余白
