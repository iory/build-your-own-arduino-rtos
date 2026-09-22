#!/usr/bin/env python3
"""「自分でビルドした ELF をブラウザで動かす」の、ブラウザ側を録る。

公開中のブラウザ版シミュレータを開き、章の一覧で「自分でビルドした ELF を
動かす…」を選び、type_sim_upload.py でビルドした firmware.elf をドロップ欄に
落とす。ドロップはページが受け取る本物の drop イベントで、中身もそのとき
ビルドした ELF。画面の上の手順の見出しだけは説明のために重ねている。

    record_sim_upload_browser.py <firmware.elf> <出力.webm> [--url URL]
"""
import argparse
import base64
import shutil
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_URL = "https://iory.github.io/build-your-own-arduino-rtos/sim/"
# 幅は GIF と同じにする（縮めるとシリアルの文字が読めなくなる）
VIEWPORT = {"width": 600, "height": 1000}
EXPECT = "Hello from my build!"

CAPTION_JS = """(text) => {
  let el = document.getElementById('demo-caption');
  if (!el) {
    el = document.createElement('div');
    el.id = 'demo-caption';
    el.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:99;padding:10px 16px;'
      + 'background:#1a7f8e;color:#fff;font:600 17px "Noto Sans CJK JP",sans-serif;';
    document.body.appendChild(el);
    document.body.style.paddingTop = '60px';
  }
  el.textContent = text;
}"""

DROP_JS = """async ([b64, name, phase]) => {
  const drop = document.getElementById('drop');
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const dt = new DataTransfer();
  dt.items.add(new File([bytes], name));
  drop.dispatchEvent(new DragEvent(phase, { dataTransfer: dt, bubbles: true, cancelable: true }));
}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("elf", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()
    b64 = base64.b64encode(args.elf.read_bytes()).decode()

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT, record_video_dir=tmp,
                                  record_video_size=VIEWPORT)
        page = ctx.new_page()
        t_video = time.time()          # 動画はページを作ったときから始まる
        # 最初の 1 回は coi-serviceworker が入って自動で読み込み直すので、録る前に済ませる
        page.goto(args.url)
        page.wait_for_function("document.getElementById('status').textContent === '動作中'",
                               timeout=120000)
        page.evaluate(CAPTION_JS, "① 章の一覧で「自分でビルドした ELF を動かす…」を選ぶ")
        # 読み込み中の部分を切り落とせるよう、見出し①が出た時刻（動画の先頭から）を出す
        print(f"{time.time() - t_video:.2f}")
        time.sleep(2.0)
        page.select_option("#chapter", "custom")          # 選ぶとページが読み込み直される
        page.wait_for_selector("#upload:not([hidden])", timeout=120000)
        page.evaluate(CAPTION_JS, "② ビルドした firmware.elf をドロップする")
        time.sleep(2.0)
        page.evaluate(DROP_JS, [b64, "firmware.elf", "dragover"])
        time.sleep(1.2)
        page.evaluate(DROP_JS, [b64, "firmware.elf", "drop"])
        page.wait_for_function(
            f"document.getElementById('console').textContent.includes({EXPECT!r})",
            timeout=120000)
        page.evaluate(CAPTION_JS, "③ 書き換えたメッセージが出て、LED マトリクスに「OS」が出る")
        time.sleep(6.0)
        video = page.video.path()
        ctx.close()
        browser.close()
        shutil.copy(video, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
