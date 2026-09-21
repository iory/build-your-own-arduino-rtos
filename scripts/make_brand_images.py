# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""ファビコンと OGP 画像を作る。

ファビコンは第0章のスケッチ（code/00_intro/src/main.cpp）が LED マトリクスに
表示する "OS" のビットマップを、そのコードから読み取って描く。OGP 画像は
表紙の書影と同じビットマップを並べる。出力は ja / en 両方の _static/ に書く。

Usage
-----
uv run scripts/make_brand_images.py [--font PATH]
"""

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SKETCH = ROOT / "code" / "00_intro" / "src" / "main.cpp"
STATIC_DIRS = [ROOT / "docs" / lang / "source" / "_static" for lang in ("ja", "en")]
COVER = STATIC_DIRS[0] / "book_cover.jpg"
SITE_URL = "iory.github.io/build-your-own-arduino-rtos"

MATRIX_ROWS, MATRIX_COLS = 8, 12  # UNO R4 WiFi の LED マトリクス
BG = "#1b1f24"
LED_ON = "#ff4a3d"
LED_OFF = "#2c3239"
TEXT_MAIN = "#ffffff"
TEXT_SUB = "#aab2bd"

OG_SIZE = (1200, 630)
PNG_ICON_SIZES = {"favicon-32.png": 32, "apple-touch-icon.png": 180}
SUPERSAMPLE = 8


def read_bitmap(sketch):
    """スケッチの ``frame[r][c] = 1`` から点灯している (row, col) を集める。

    Parameters
    ----------
    sketch : Path
        ``frame[8][12]`` に代入している Arduino スケッチ。

    Returns
    -------
    set of tuple of int
        点灯 LED の (row, col)。
    """
    lit = {
        (int(r), int(c))
        for r, c in re.findall(r"frame\[(\d+)\]\[(\d+)\]\s*=\s*1\s*;", sketch.read_text())
    }
    if not lit:
        raise SystemExit(f"{sketch} に frame[r][c] = 1 が見つからない")
    return lit


def crop_box(lit):
    """点灯 LED を囲む最小の (row0, col0, rows, cols) を返す。"""
    rows = [r for r, _ in lit]
    cols = [c for _, c in lit]
    return min(rows), min(cols), max(rows) - min(rows) + 1, max(cols) - min(cols) + 1


def icon_layout(lit, side):
    """ファビコンの一辺 ``side`` に対し、各点灯 LED の中心と半径を返す。

    点灯部分だけを切り出し、上下左右に 1 マスの余白を取って正方形の中央に置く。
    """
    row0, col0, rows, cols = crop_box(lit)
    cell = side / (max(rows, cols) + 2)
    x0 = (side - cols * cell) / 2
    y0 = (side - rows * cell) / 2
    radius = cell * 0.42
    return [
        (x0 + (c - col0 + 0.5) * cell, y0 + (r - row0 + 0.5) * cell, radius)
        for r, c in sorted(lit)
    ]


def write_svg(lit, path):
    """ファビコンを SVG で書く。"""
    side = 100
    dots = "".join(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rad:.2f}"/>'
        for x, y, rad in icon_layout(lit, side)
    )
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}">'
        f'<rect width="{side}" height="{side}" rx="{side * 0.18:.0f}" fill="{BG}"/>'
        f'<g fill="{LED_ON}">{dots}</g></svg>\n'
    )


def render_icon(lit, size):
    """ファビコンを ``size`` px 角の PNG 用画像にする（拡大して描いて縮める）。"""
    big = size * SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, big - 1, big - 1), radius=big * 0.18, fill=BG)
    for x, y, rad in icon_layout(lit, big):
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=LED_ON)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def draw_matrix(draw, lit, left, top, cell):
    """12x8 のマトリクス全体（消灯 LED も含む）を描く。"""
    radius = cell * 0.36
    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            cx = left + (c + 0.5) * cell
            cy = top + (r + 0.5) * cell
            fill = LED_ON if (r, c) in lit else LED_OFF
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill)


def render_og(lit, font_path):
    """SNS 共有用の 1200x630 画像を作る。左に表紙、右に LED マトリクスと文字。"""
    width, height = OG_SIZE
    img = Image.new("RGB", OG_SIZE, BG)

    margin = 60
    cover = Image.open(COVER).convert("RGB")
    cover_h = height - 2 * margin
    cover_w = round(cover.width * cover_h / cover.height)
    cover = cover.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", OG_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle(
        (margin + 10, margin + 14, margin + cover_w + 10, margin + cover_h + 14),
        fill=(0, 0, 0, 170),
    )
    blurred = shadow.filter(ImageFilter.GaussianBlur(14))
    img.paste(blurred, (0, 0), blurred)
    img.paste(cover, (margin, margin))

    draw = ImageDraw.Draw(img)
    title_size, sub_size = 56, 28
    title = ImageFont.truetype(str(font_path), title_size, index=0)
    sub = ImageFont.truetype(str(font_path), sub_size, index=0)
    gap_matrix, gap_title, gap_sub = 48, 30, 16
    text_h = title_size + gap_title + sub_size + gap_sub + sub_size

    right = margin + cover_w + 70
    avail_w = width - margin - right
    cell = min(avail_w / MATRIX_COLS, (cover_h - gap_matrix - text_h) / MATRIX_ROWS)
    block_h = MATRIX_ROWS * cell + gap_matrix + text_h
    y = margin + (cover_h - block_h) / 2
    draw_matrix(draw, lit, right, y, cell)

    y += MATRIX_ROWS * cell + gap_matrix
    draw.text((right, y), "書籍サポートページ", font=title, fill=TEXT_MAIN)
    y += title_size + gap_title
    draw.text((right, y), "開発環境・章ごとのコード・組み立て・正誤表", font=sub, fill=TEXT_SUB)
    y += sub_size + gap_sub
    draw.text((right, y), SITE_URL, font=sub, fill=TEXT_SUB)
    return img


def main():
    """ja / en の _static/ にファビコンと OGP 画像を書き出す。"""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--font",
        type=Path,
        default=Path("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"),
        help="OGP 画像の文字に使う日本語フォント（既定は macOS のヒラギノ角ゴ W6）",
    )
    args = parser.parse_args()

    lit = read_bitmap(SKETCH)
    og = render_og(lit, args.font)
    for static in STATIC_DIRS:
        write_svg(lit, static / "favicon.svg")
        for name, size in PNG_ICON_SIZES.items():
            render_icon(lit, size).save(static / name)
        og.save(static / "og_image.png", optimize=True)
        print(f"wrote favicon.svg, {', '.join(PNG_ICON_SIZES)}, og_image.png -> {static.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
