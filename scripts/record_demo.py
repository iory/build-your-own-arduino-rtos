#!/usr/bin/env python3
"""サポートページ用の端末 GIF を録る。

実際の `pio device monitor` をそのまま動かして録画するので、読者が手元で
打つものと同じです。**書き込みはしません。** 収録中に書き込みが走ると
別の章の出力が混ざるため、`--flash` を明示したときだけ、収録の前に行います。

    python3 record_demo.py --list
    python3 record_demo.py ch04 --flash
    python3 record_demo.py ch04            # 録るだけ
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

CODE = os.path.expanduser("~/build-your-own-arduino-rtos/code")
UV = os.path.expanduser("~/.local/bin/uv")
OUT = os.path.expanduser("~/casts")


class Demo:
    def __init__(self, key, chapter, seconds, keys=(), handshake="", ready="",
                 pre=1.5, note=""):
        self.key = key
        self.chapter = chapter
        self.seconds = seconds
        self.keys = keys          # (待ち秒, 送る文字列) の並び。改行は自分で付ける
        self.handshake = handshake
        self.ready = ready        # これが出たらハンドシェイクをやめる
        self.pre = pre            # モニタを開いてから動かし始めるまでの間
        self.note = note


# (待つ秒数, 送る文字列)
DEMOS = [
    Demo("ch01", "01_boot", 7, handshake="S", ready=r"=== Boot", pre=2.5,
         note="S を送ると起動時の値がまとめて出る。読者が最初に見る画面"),
    Demo("ch02", "02_baremetal", 16,
         note="協調スケジューラが 3 タスクを回す。Servo の角度が動き続ける"),
    Demo("ch03", "03_context_switch", 18,
         note="os_yield() でタスクが切り替わる"),
    Demo("ch04", "04_scheduler", 18,
         note="重いタスクが 1 秒ごとのカウンタに割り込まれる。プリエンプションが見える"),
    Demo("ch06", "06_memory_protection", 26,
         keys=[(2.0, "p\n"), (3.0, "d\n"), (12.0, "p\n")],
         note="ゼロ除算で fault が起きても、ほかのタスクが動き続ける"),
    Demo("adv1", "adv1_sync", 16,
         note="5 人の食事回数が揃って伸びる = 誰も餓死していない"),
    Demo("ch11", "11_tiny_python", 30,
         keys=[(2.0, "print(1 + 2)\n"),
               (2.0, "def fact(n):\n"),
               (0.8, "    if n < 2:\n"),
               (0.8, "        return 1\n"),
               (0.8, "    return n * fact(n - 1)\n"),
               (0.8, "\n"),
               (1.5, "fact(7)\n"),
               (2.0, "fact(30)\n")],
         note="ボード上の Python。再帰が深すぎると RecursionError で止まる"),
    Demo("adv2", "adv2_syscall", 16,
         note="出力がすべて svc 経由。2 つのタスクが交互に出る"),
    Demo("adv3", "adv3_heap", 12, handshake="S", ready=r"Advanced 3", pre=2.5,
         note="malloc / free のたびにヒープの区画が変わっていく"),
    Demo("adv4", "adv4_fs", 10, handshake="S", ready=r"Advanced 4", pre=2.5,
         note="Data Flash の LittleFS を mount し、boot count と中身を出す"),
    Demo("ch08", "08_interpreter", 18,
         keys=[(2.0, "run PRINT hello\n"), (2.5, "run FORWARD 10\n")],
         note="自作インタプリタにコマンドを流す"),
]
BY_KEY = {d.key: d for d in DEMOS}


def flash(demo):
    print(f"=== flashing {demo.chapter} ===", flush=True)
    r = subprocess.run([UV, "run", "pio", "run", "-d", demo.chapter, "-t", "upload"],
                       cwd=CODE)
    if r.returncode != 0:
        sys.exit(f"flash failed: {demo.chapter}")
    time.sleep(3)      # 書き込み後、ポートが落ち着くまで


def record(demo):
    import pexpect

    os.makedirs(OUT, exist_ok=True)
    cast = os.path.join(OUT, f"{demo.key}.cast")
    if os.path.exists(cast):
        os.remove(cast)

    driver = os.path.join(OUT, f"_drive_{demo.key}.py")
    with open(driver, "w") as f:
        f.write(DRIVER.format(chapter=repr(demo.chapter), uv=repr(UV), code=repr(CODE),
                              seconds=demo.seconds, keys=repr(list(demo.keys)),
                              handshake=repr(demo.handshake), ready=repr(demo.ready),
                              pre=demo.pre))

    print(f"=== recording {demo.key} ({demo.seconds}s) ===", flush=True)
    subprocess.run(["asciinema", "rec", "--overwrite", "--cols", "68", "--rows", "18",
                    "-c", f"python3 {driver}", cast], check=True)
    print(f"wrote {cast}  ({os.path.getsize(cast)} bytes)")
    return cast


DRIVER = '''
import os, sys, time, pexpect
os.chdir({code})
c = pexpect.spawn({uv} + " run pio device monitor -b 115200", encoding="utf-8",
                  timeout=None, dimensions=(18, 68))
c.logfile_read = sys.stdout

def pump(sec):
    try:
        c.expect(pexpect.TIMEOUT, timeout=sec)
    except Exception:
        pass

pump({pre})                       # 開いた直後は静かなので、少し置いてから動かす
hs, ready = {handshake}, {ready}
if hs:
    for _ in range(60):          # 出力が始まるまで送り続ける
        c.send(hs)
        try:
            c.expect(ready, timeout=0.25)
            break                # 出はじめたら、もう送らない
        except pexpect.TIMEOUT:
            pass

start = time.time()
for wait, text in {keys}:
    pump(wait)
    for ch in text:              # 1 文字ずつ送ると、打っているように見える
        c.send(ch)
        pump(0.05)

pump(max(1.0, {seconds} - (time.time() - start)))
c.sendcontrol(']')               # pio monitor を抜ける
pump(1.0)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("demo", nargs="?")
    ap.add_argument("--flash", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list or not a.demo:
        for d in DEMOS:
            print(f"{d.key:8} {d.chapter:22} {d.seconds:3}s  {d.note}")
        return
    if a.demo not in BY_KEY:
        sys.exit(f"unknown demo: {a.demo}")
    d = BY_KEY[a.demo]
    if a.flash:
        flash(d)
    record(d)


if __name__ == "__main__":
    main()
