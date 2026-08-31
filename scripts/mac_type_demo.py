#!/usr/bin/env python3
"""Terminal.app の中で、本物の zsh に 1 文字ずつ打ち込む。"""
import sys
import pexpect

STEPS = [("ls /dev/cu.usbmodem*", 1.5),
         ("uv run pio device list | grep -A 3 usbmodem", 7.0)]

c = pexpect.spawn("/bin/zsh -f", encoding="utf-8", timeout=None, dimensions=(20, 84),
                  env={"TERM": "xterm-256color", "HOME": "/Users/user",
                       "PATH": "/Users/user/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin"})
c.logfile_read = sys.stdout

def pump(s):
    try: c.expect(pexpect.TIMEOUT, timeout=s)
    except Exception: pass

c.send("PS1='%F{green}iory@build-arduino-os%f %F{blue}~%f %% '\n")
pump(0.4)
c.send("cd /Users/user/src/github.com/iory/build-your-own-arduino-rtos/code\n")
pump(0.6)
c.send("clear\n")
pump(1.5)
for cmd, wait in STEPS:
    for ch in cmd:
        c.send(ch); pump(0.07)
    pump(0.5); c.send("\n"); pump(wait); pump(1.5)
pump(5)
