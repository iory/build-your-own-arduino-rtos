# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""サポートページと README に載せる紹介動画（MP4）と GIF を作る。

素材はリポジトリに入っている画像・GIF（OGP 画像、「OS」表示のボード写真、
第4章の端末 GIF、シミュレータの LED マトリクス GIF、組み立て手順の図）と、
四脚ロボットが歩く実写動画（4K、リポジトリには入れない）。字幕は Pillow で
PNG に描いて重ね、ffmpeg で 1 本につなぐ。

出力:

- ``docs/{ja,en}/source/_static/promo.mp4``  言語ごとの字幕付き（1280x720）
- ``docs/ja/source/_static/promo.gif``  README 用（480 px 幅。タイトル・
  エンドカードと、縮めると読めない端末録画を省いた短縮版）
- ``docs/{ja,en}/source/_static/quadruped_walk.gif``  四脚ロボットの章用。
  実写の歩行部分だけ（字幕なし）

Usage
-----
uv run scripts/make_promo_video.py --robot-video arduino-quad-robot.mp4
"""

import argparse
import subprocess
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = {lang: ROOT / "docs" / lang / "source" / "_static" for lang in ("ja", "en")}
ASSEMBLY_DIR = ROOT / "docs" / "ja" / "source" / "hardware" / "assembly_img"
SITE_URL = "iory.github.io/build-your-own-arduino-rtos"

WIDTH, HEIGHT, FPS = 1280, 720, 30
FADE = 0.4  # 場面の切り替え（クロスフェード）の長さ [s]
BG = "#1b1f24"  # make_brand_images.py の OGP 画像と同じ背景色
TEXT_MAIN = "#ffffff"
TEXT_SUB = "#aab2bd"
ACCENT = "#ff4a3d"  # LED マトリクスの点灯色
CAPTION_BAR = (27, 31, 36, 215)
CAPTION_H = 68  # 字幕帯の高さ [px]

GIF_WIDTH, GIF_FPS, GIF_COLORS = 480, 8, 64
WALK_GIF_WIDTH, WALK_GIF_FPS = 480, 8

CAPTIONS = {
    "ja": {
        "os": ("第0章", "Arduino UNO R4 WiFi で OS を一から自作する"),
        "preempt": ("第4章", "タイマ割り込みでタスクを切り替えるプリエンプティブ・スケジューラ"),
        "matrix": ("第7章", "kill 3 で重いタスクを止めると CPU 負荷グラフが下がる（シミュレータ）"),
        "assembly": ("第13章", "3D プリントの四脚ロボットを組み立てる"),
        "robot": ("第13章", "自作 OS でサーボ 8 個を制御して歩かせる"),
        "end_title": "書籍サポートページ",
        "end_sub": "開発環境・章ごとのコード・組み立て・正誤表",
    },
    "en": {
        "os": ("Ch. 0", "Build an OS from scratch on the Arduino UNO R4 WiFi"),
        "preempt": ("Ch. 4", "A preemptive scheduler that switches tasks on a timer interrupt"),
        "matrix": ("Ch. 7", "kill 3 stops the heavy task and the CPU-load graph drops (simulator)"),
        "assembly": ("Ch. 13", "Assemble the 3D-printed quadruped"),
        "robot": ("Ch. 13", "Your own OS drives 8 servos to make it walk"),
        "end_title": "Book Support Site",
        "end_sub": "Setup, per-chapter code, assembly, and errata",
    },
}


@dataclass
class Scene:
    """動画の 1 場面。

    Attributes
    ----------
    name : str
        ``CAPTIONS`` のキー（字幕が無い場面では識別用）。
    duration : float
        場面の長さ [s]（クロスフェードと重なる分を含む）。
    input_args : list of str
        ffmpeg の入力オプション（``-i`` を含む）。
    vfilter : str
        入力を ``WIDTH x HEIGHT`` の映像にするフィルタ。
    in_readme : bool
        README 用の短縮 GIF にも入れるか。
    caption : bool
        下端に字幕帯を重ねるか。
    """

    name: str
    duration: float
    input_args: list
    vfilter: str
    in_readme: bool = True
    caption: bool = True


def font(path, size):
    """ヒラギノの .ttc から指定サイズのフォントを読む。"""
    return ImageFont.truetype(str(path), size, index=0)


def fit_pad(bg=BG, above_caption=False):
    """アスペクト比を保って ``WIDTH x HEIGHT`` に収め、余白を ``bg`` で埋めるフィルタ。

    ``above_caption`` なら字幕帯より上に収める（画面下端に読ませたい文字がある
    端末録画や組み立て図用）。
    """
    color = bg.lstrip("#")
    box_h = HEIGHT - CAPTION_H if above_caption else HEIGHT
    return (
        f"scale={WIDTH}:{box_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:({box_h}-ih)/2:color=0x{color},setsar=1,fps={FPS}"
    )


def render_caption(tag, text, font_bold, font_regular, out):
    """下端の字幕帯（章ラベル + 説明）を透過 PNG に描く。"""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bar_h = CAPTION_H
    draw.rectangle((0, HEIGHT - bar_h, WIDTH, HEIGHT), fill=CAPTION_BAR)
    tag_font = font(font_bold, 26)
    text_font = font(font_regular, 26)
    pad_x, pill_pad = 28, 12
    tag_w = draw.textlength(tag, font=tag_font)
    cy = HEIGHT - bar_h / 2
    draw.rounded_rectangle(
        (pad_x, cy - 20, pad_x + tag_w + 2 * pill_pad, cy + 20), radius=8, fill=ACCENT
    )
    draw.text((pad_x + pill_pad, cy), tag, font=tag_font, fill=TEXT_MAIN, anchor="lm")
    draw.text((pad_x + tag_w + 2 * pill_pad + 18, cy), text, font=text_font,
              fill=TEXT_MAIN, anchor="lm")
    img.save(out)


def render_end_card(lang, font_bold, font_regular, out):
    """表紙・サイト名・URL を並べたエンドカードを描く。"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    margin = 80
    cover = Image.open(STATIC["ja"] / "book_cover.jpg").convert("RGB")
    cover_h = HEIGHT - 2 * margin
    cover_w = round(cover.width * cover_h / cover.height)
    cover = cover.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
    img.paste(cover, (margin, margin))

    draw = ImageDraw.Draw(img)
    x = margin + cover_w + 60
    cap = CAPTIONS[lang]
    title_f, sub_f = font(font_bold, 52), font(font_regular, 28)
    # URL は長いので、右端に収まる大きさまで縮める
    url_size = 30
    while draw.textlength(SITE_URL, font=font(font_bold, url_size)) > WIDTH - margin / 2 - x:
        url_size -= 1
    url_f = font(font_bold, url_size)
    y = HEIGHT / 2 - 70
    draw.text((x, y), cap["end_title"], font=title_f, fill=TEXT_MAIN, anchor="ls")
    draw.text((x, y + 56), cap["end_sub"], font=sub_f, fill=TEXT_SUB, anchor="ls")
    draw.line((x, y + 92, WIDTH - margin / 2, y + 92), fill=ACCENT, width=3)
    draw.text((x, y + 146), SITE_URL, font=url_f, fill=TEXT_MAIN, anchor="ls")
    img.save(out)


def build_scenes(robot_video, robot_start, robot_len, robot_speed, work):
    """場面のリストを作る。長さは素材の見どころに合わせて決めてある。"""
    ja = STATIC["ja"]
    assembly = sorted(ASSEMBLY_DIR.glob("step_*.png"))
    step_sec = 0.7
    # 組み立て図は連番 PNG を 1 本の入力として読む（1 枚 step_sec 秒）
    assembly_list = work / "assembly.txt"
    assembly_list.write_text(
        "".join(f"file '{p}'\nduration {step_sec}\n" for p in assembly)
        + f"file '{assembly[-1]}'\n"
    )
    zoom_frames = int(4.0 * FPS)
    return [
        Scene("title", 3.5, ["-loop", "1", "-i", str(ja / "og_image.png")],
              fit_pad(), in_readme=False, caption=False),
        Scene("os", 4.0, ["-loop", "1", "-i", str(ja / "uno_r4_wifi_os.jpg")],
              # 写真をゆっくり LED マトリクスへ寄せる
              f"scale=2560:-1,zoompan=z='min(1+0.0018*on,1.2)':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={zoom_frames}:"
              f"s={WIDTH}x{round(WIDTH * 1200 / 1600)}:fps={FPS},"
              f"crop={WIDTH}:{HEIGHT},setsar=1"),
        Scene("preempt", 6.0, ["-i", str(ja / "ch04_preemption.gif")],
              fit_pad("#1d1f21", above_caption=True), in_readme=False),
        Scene("matrix", 9.0, ["-ss", "3", "-i", str(ja / "sim_matrix_kill.gif")],
              fit_pad(above_caption=True)),
        Scene("assembly", step_sec * len(assembly) + 0.8,
              ["-f", "concat", "-safe", "0", "-i", str(assembly_list)],
              fit_pad("#ffffff", above_caption=True)),
        Scene("robot", robot_len / robot_speed,
              ["-ss", str(robot_start), "-t", str(robot_len), "-i", str(robot_video)],
              f"setpts=PTS/{robot_speed},{fit_pad()}"),
        Scene("end", 4.0, ["-loop", "1", "-i", str(work / "end.png")],
              fit_pad(), in_readme=False, caption=False),
    ]


def compose(scenes, lang, work, out, width):
    """場面をクロスフェードでつなぎ、字幕を重ねて H.264 に書き出す。"""
    args = ["ffmpeg", "-v", "error", "-y"]
    for s in scenes:
        args += s.input_args
    n_video = len(scenes)
    caption_idx = {}
    for s in scenes:
        if s.caption:
            caption_idx[s.name] = n_video + len(caption_idx)
            args += ["-loop", "1", "-i", str(work / f"cap_{lang}_{s.name}.png")]

    chains = []
    for i, s in enumerate(scenes):
        chain = f"[{i}:v]{s.vfilter},trim=duration={s.duration},setpts=PTS-STARTPTS,format=yuv420p"
        if s.caption:
            chains.append(f"{chain}[b{i}]")
            chains.append(
                f"[b{i}][{caption_idx[s.name]}:v]overlay=0:0:shortest=1,"
                f"trim=duration={s.duration},setpts=PTS-STARTPTS[v{i}]"
            )
        else:
            chains.append(f"{chain}[v{i}]")

    prev, offset = "v0", 0.0
    for i in range(1, len(scenes)):
        offset += scenes[i - 1].duration - FADE
        label = f"x{i}"
        chains.append(
            f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[{label}]"
        )
        prev = label
    total = offset + scenes[-1].duration
    chains.append(f"[{prev}]fade=in:st=0:d=0.3,fade=out:st={total - 0.5:.3f}:d=0.5,"
                  f"scale={width}:-2:flags=lanczos[out]")

    args += ["-filter_complex", ";".join(chains), "-map", "[out]", "-an",
             "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", "-r", str(FPS), str(out)]
    subprocess.run(args, check=True)
    return total


def to_gif(mp4, out, width, fps, colors=GIF_COLORS):
    """MP4 を 2 パス（パレット生成 → 適用）で GIF にする。"""
    palette = mp4.with_suffix(".palette.png")
    base = f"fps={fps},scale={width}:-1:flags=lanczos"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf",
                    f"{base},palettegen=max_colors={colors}:stats_mode=diff", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-i", str(palette),
                    "-lavfi", f"{base}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:"
                    "diff_mode=rectangle", str(out)], check=True)


def main():
    """ja / en の紹介動画と README 用 GIF を書き出す。"""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--robot-video", type=Path, required=True,
                        help="四脚ロボットが歩く実写動画")
    parser.add_argument("--robot-start", type=float, default=17.0,
                        help="実写動画から切り出す開始位置 [s]")
    parser.add_argument("--robot-len", type=float, default=18.0,
                        help="実写動画から切り出す長さ [s]（等速換算）")
    parser.add_argument("--robot-speed", type=float, default=1.5,
                        help="実写部分の再生速度（倍）")
    parser.add_argument("--font-bold", type=Path,
                        default=Path("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"))
    parser.add_argument("--font-regular", type=Path,
                        default=Path("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"))
    opts = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for lang in ("ja", "en"):
            for key, value in CAPTIONS[lang].items():
                if isinstance(value, tuple):
                    render_caption(*value, opts.font_bold, opts.font_regular,
                                   work / f"cap_{lang}_{key}.png")
            render_end_card(lang, opts.font_bold, opts.font_regular, work / "end.png")
            scenes = build_scenes(opts.robot_video, opts.robot_start, opts.robot_len,
                                  opts.robot_speed, work)
            out = STATIC[lang] / "promo.mp4"
            total = compose(scenes, lang, work, out, WIDTH)
            print(f"{out.relative_to(ROOT)}: {total:.1f} s, {out.stat().st_size / 1e6:.1f} MB")

            if lang == "ja":
                short = work / "readme.mp4"
                compose([s for s in scenes if s.in_readme], lang, work, short, WIDTH)
                gif = STATIC["ja"] / "promo.gif"
                to_gif(short, gif, GIF_WIDTH, GIF_FPS)
                print(f"{gif.relative_to(ROOT)}: {gif.stat().st_size / 1e6:.1f} MB")

                walk = work / "walk.mp4"
                robot = next(s for s in scenes if s.name == "robot")
                compose([replace(robot, caption=False)], lang, work, walk, WIDTH)
                for static in STATIC.values():
                    gif = static / "quadruped_walk.gif"
                    to_gif(walk, gif, WALK_GIF_WIDTH, WALK_GIF_FPS)
                    print(f"{gif.relative_to(ROOT)}: {gif.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
