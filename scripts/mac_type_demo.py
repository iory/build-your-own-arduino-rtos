#!/usr/bin/env python3
"""Terminal.app の中で、本物の zsh に 1 文字ずつ打ち込む（macOS 用）。

見えているプロンプトも出力も本物で、打鍵だけを機械が代行している。
zsh は -f（設定を一切読まない）で起動し、プロンプトだけ読み手に依らない
形に固定する。ホスト名を出すと収録した機械の名前が公開されてしまうため。
"""
import os
import sys

import pexpect

HOME = os.path.expanduser("~")
CODE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code"))
PROMPT = "%F{green}iory@build-arduino-os%f %F{blue}~%f %% "

STEPS = [
    ("ls /dev/cu.usbmodem*", 1.5),
    ("uv run pio device list | grep -A 3 usbmodem", 7.0),
]

c = pexpect.spawn(
    "/bin/zsh -f", encoding="utf-8", timeout=None, dimensions=(20, 84),
    env={"TERM": "xterm-256color", "HOME": HOME,
         "PATH": f"{HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin"})
c.logfile_read = sys.stdout


def pump(sec):
    try:
        c.expect(pexpect.TIMEOUT, timeout=sec)
    except Exception:
        pass


c.send(f"PS1='{PROMPT}'\n")
pump(0.4)
c.send(f"cd {CODE}\n")
pump(0.6)
c.send("clear\n")           # ここまでの準備を画面から消す
pump(1.5)

for cmd, wait in STEPS:
    for ch in cmd:          # 人が打っているくらいの速さで
        c.send(ch)
        pump(0.07)
    pump(0.5)
    c.send("\n")
    pump(wait)
    pump(1.5)               # 出力を読む間
pump(5)                     # 終わったあとの余白
